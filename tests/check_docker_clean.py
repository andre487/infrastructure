"""Exercise the real playbook with a fake Docker CLI; never contact a Docker daemon."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    work = Path(td)
    docker = work / 'docker'
    docker.write_text(f'''#!{sys.executable}
import json, os, sys
with open(os.environ['DOCKER_TEST_LOG'], 'a') as log:
    log.write(json.dumps(sys.argv[1:]) + '\\n')
if sys.argv[1] == 'version':
    print(os.environ.get('DOCKER_TEST_API', '1.42 1.42'))
elif sys.argv[1:3] == ['system', 'df']:
    print('Test Docker disk usage')
else:
    print('Total reclaimed space: 0B')
''')
    docker.chmod(0o755)
    log = work / 'calls'
    env = dict(os.environ, PATH=str(work) + os.pathsep + os.environ['PATH'],
               DOCKER_TEST_LOG=str(log), ANSIBLE_LOCAL_TEMP=str(work / 'ansible'))

    def run(*args, api='1.42 1.42'):
        log.write_text('')
        result = subprocess.run([str(root / 'bin/ansible-playbook'), '-i', 'localhost,',
            '-c', 'local', str(root / 'docker-clean.yml'), '-e', 'arg_hosts=all',
            '-e', 'ansible_become=false', '-e', f'ansible_python_interpreter={sys.executable}', *args],
            env=dict(env, DOCKER_TEST_API=api), capture_output=True, text=True)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        return result, calls

    result, calls = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert calls == [['system', 'df'], ['system', 'prune', '--force', '--filter', 'until=168h']], calls
    result, calls = run('-e', 'docker_clean_volumes=true', '-e', 'docker_clean_until=720h')
    assert result.returncode == 0, result.stdout + result.stderr
    assert ['system', 'prune', '--force', '--filter', 'until=720h'] in calls
    assert calls[-1] == ['volume', 'prune', '--force'], calls
    assert not any('--all' in call or '-a' in call for call in calls)
    result, calls = run('-e', 'docker_clean_volumes=true', '--check')
    assert result.returncode == 0, result.stdout + result.stderr
    assert all('prune' not in call for call in calls), calls
    for api in ('1.41 1.42', '1.42 1.41'):
        result, calls = run('-e', 'docker_clean_volumes=true', api=api)
        assert result.returncode != 0
        assert all('prune' not in call for call in calls), calls
print('Docker cleanup playbook checks passed')
