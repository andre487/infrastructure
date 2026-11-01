"""Check uv invocation and argument forwarding without invoking Ansible."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    fake = Path(td)
    shutil.copytree(root / 'bin', fake / 'bin')
    uv = fake / 'bin/uv'
    uv.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    uv.chmod(0o755)
    env = dict(os.environ, PATH=str(fake / 'bin') + os.pathsep + os.environ['PATH'])

    def call(name, *args, environment=env):
        return subprocess.run([str(fake / 'bin' / name), *args], env=environment,
                              capture_output=True, text=True, cwd='/private/tmp')

    # The existing wrappers resolve their project root independently of cwd.
    prefix = ['run', '--locked', '--project', str(fake / 'bin/..'), '--']
    for command in ('ansible', 'ansible-playbook'):
        result = call(command, '-i', 'host,', '--check')
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == prefix + [command, '-i', 'host,', '--check']
    result = call('ansible', '--version')
    assert result.stdout.splitlines() == prefix + ['ansible', '--version']
    result = call('ansible-vault', 'view', 'file with spaces.yml')
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == prefix + ['ansible-vault', 'view', 'file with spaces.yml']
print('Ansible uv wrapper checks passed')
