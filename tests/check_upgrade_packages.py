"""Check interactive target selection without connecting to any servers."""
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    fake = Path(td).resolve()
    (fake / 'bin').mkdir()
    shutil.copy(root / 'bin/upgrade-packages', fake / 'bin/upgrade-packages')
    runner = fake / 'bin/ansible-playbook'
    runner.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    runner.chmod(0o755)

    def run(hosts, *args):
        return subprocess.run([str(fake / 'bin/upgrade-packages'), *args], input=hosts,
                              capture_output=True, text=True)

    result = run('server-a, 203.0.113.10\n', '-u', 'deploy', '--check')
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[1:] == ['-i', 'server-a,203.0.113.10,', str(fake / 'upgrade-packages.yml'),
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
    runner.write_text('#!/bin/sh\nexit 7\n')
    assert run('server-a\n').returncode == 7
print('Interactive upgrade checks passed')
