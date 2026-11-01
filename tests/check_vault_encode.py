"""Check that the shell encoder preserves stdin through an actual Vault round trip."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    password = Path(td) / 'password'
    password.write_text('test-only-vault-password\n')
    password.chmod(0o600)
    env = {key: value for key, value in os.environ.items() if not key.startswith("ANSIBLE_VAULT")}
    env["ANSIBLE_LOCAL_TEMP"] = td
    original = '-leading-dash, quotes \'" and unicode: привет\nsecond line\n'
    encoded = subprocess.run([str(root / 'bin/vlt-ans-encode'), '--vault-password-file', str(password)],
                             input=original, text=True, capture_output=True, check=True, env=env).stdout
    vault = encoded[encoded.index('$ANSIBLE_VAULT;'):].replace(' ', '')
    decoded = subprocess.run([str(root / 'bin/ansible-vault'), 'decrypt', '--output', '-',
                              '--vault-password-file', str(password), '-'],
                             input=vault, text=True, capture_output=True, check=True, env=env).stdout
    assert decoded == original
print('Vault stdin round-trip check passed')
