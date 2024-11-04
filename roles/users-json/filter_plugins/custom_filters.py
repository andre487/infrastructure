import hashlib
import json
import os

from ansible.parsing.yaml.objects import AnsibleVaultEncryptedUnicode
from ansible.plugins.filter.core import FilterModule as BaseFilterModule

type PasswordItem = dict[str, str | AnsibleVaultEncryptedUnicode]
type PasswordItems = list[PasswordItem]


def users_json_create(password_db: dict[str, PasswordItems]) -> str:
    data = {}
    for service_type, pass_data in password_db.items():
        data[service_type] = {}
        for item in pass_data:
            name: str = item['name']
            pwd: AnsibleVaultEncryptedUnicode = item['password']
            salt = os.urandom(16)

            n_hash = hashlib.sha256(name.encode('utf8')).hexdigest()
            p_hash = hashlib.pbkdf2_hmac('sha512', pwd.data.encode('utf8'), salt, 256_000)
            p_string = f'{salt.hex()}:{p_hash.hex()}'
            data[service_type][n_hash] = p_string
    return json.dumps(data, indent=2)


class FilterModule(BaseFilterModule):
    def filters(self):
        return {
            'users_json_create': users_json_create,
        }
