"""Check interactive target selection without connecting to any servers."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    fake = Path(td).resolve()
    (fake / 'bin').mkdir()
    for name in ('upgrade-packages', 'docker-clean', '_maintenance.py'):
        shutil.copy(root / 'bin' / name, fake / 'bin' / name)
    runner = fake / 'bin/ansible-playbook'
    snapshot = fake / 'inventory.json'
    runner.write_text(f"#!{sys.executable}\nimport os\nimport sys\nfrom pathlib import Path\nargs = sys.argv[1:]\nif args[0] == '-i' and Path(args[1]).is_file():\n    Path(os.environ['INVENTORY_SNAPSHOT']).write_text(Path(args[1]).read_text())\nprint('\\n'.join(args))\n")
    runner.chmod(0o755)

    def run(hosts, *args):
        return subprocess.run([str(fake / 'bin/upgrade-packages'), *args], input=hosts,
                              capture_output=True, text=True, env=dict(os.environ, INVENTORY_SNAPSHOT=str(snapshot)))

    result = run('server-a, 203.0.113.10\n', '-u', 'deploy', '--check')
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[1] == '-i'
    assert not Path(lines[2]).exists()
    assert json.loads(snapshot.read_text()) == {'all': {'vars': {'ansible_python_interpreter': '/usr/bin/python3'}, 'hosts': {'server-a': {}, '203.0.113.10': {}}}}
    assert lines[3:] == [str(fake / 'upgrade-packages.yml'),
                         '-e', 'arg_hosts=all', '-u', 'deploy', '--check'], lines
    assert run('::1,2001:db8::10\n').returncode == 0
    assert run('\n').returncode == 2
    assert run('').returncode == 2
    assert run('host;command\n').returncode == 2
    for args in [('-i', 'inventory with spaces.yml'), ('-iinventory.yml',),
                 ('--inventory', 'inventory.yml'), ('--inventory=inventory.yml',),
                 ('--inventory-file', 'inventory.yml'),
                 ('-i', 'first.yml', '-i', 'second.yml', '--limit', 'servers')]:
        result = run('', *args)
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == [str(fake / 'upgrade-packages.yml'),
                                             '-e', 'arg_hosts=all', *args]
    assert run('', '-i').returncode == 2
    assert run('', '--help').returncode == 0
    result = subprocess.run([str(fake / 'bin/docker-clean'), '-i', 'inventory.yml', '--limit', 'docker'],
                            input='', capture_output=True, text=True, env=dict(os.environ, INVENTORY_SNAPSHOT=str(snapshot)))
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [str(fake / 'docker-clean.yml'), '-e', 'arg_hosts=all',
                                         '-i', 'inventory.yml', '--limit', 'docker']
    result = subprocess.run([str(fake / 'bin/docker-clean')], input='server-a\n',
                            capture_output=True, text=True, env=dict(os.environ, INVENTORY_SNAPSHOT=str(snapshot)))
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[1] == '-i'
    assert not Path(lines[2]).exists()
    assert json.loads(snapshot.read_text())['all']['vars']['ansible_python_interpreter'] == '/usr/bin/python3'
    assert lines[3:] == [str(fake / 'docker-clean.yml'), '-e', 'arg_hosts=all']
    result = subprocess.run([str(fake / 'bin/docker-clean'), '--volumes', '-i', 'inventory.yml', '--check'],
                            input='', capture_output=True, text=True, env=dict(os.environ, INVENTORY_SNAPSHOT=str(snapshot)))
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [str(fake / 'docker-clean.yml'), '-e', 'arg_hosts=all',
                                         '-e', 'docker_clean_volumes=true', '-i', 'inventory.yml', '--check']
    runner.write_text('#!/bin/sh\nexit 7\n')
    assert run('server-a\n').returncode == 7
print('Interactive upgrade checks passed')
