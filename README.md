# infrastructure

Ansible playbooks for the remaining infrastructure: web/Docker services,
host bootstrap and package maintenance.

Services managed by separate projects:

- [MegaProxyServer](https://github.com/andre487/MegaProxyServer): HTTPS/SSH proxies, chains, users and client configuration exports.
- [MegaTgProxyServer](https://github.com/andre487/MegaTgProxyServer): Telegram MTG/MTProxy servers and SSH egress.
- [ClamavMirror487](https://github.com/andre487/ClamavMirror487): ClamAV database mirror, Caddy HTTPS, updates and optional DNS publication.

Keep migrated hosts and credentials in those projects' inventories. Do not reintroduce
them into infrastructure-wide provisioning or maintenance groups. Shared Docker,
nginx, firewall and security roles remain for other services.

## Bootstrap

Copy [inventory-examples/bootstrap.yml](inventory-examples/bootstrap.yml) to a private
inventory and replace its example host and public key. The example contains no real
credentials or infrastructure addresses. The personal inventory lives separately at
`~/MyProjects/ansible-inventory/bootstrap-inventory.yml`; add targets to its
`bootstrap.hosts` mapping before running:

```sh
bin/ansible-playbook -i ~/MyProjects/ansible-inventory/bootstrap-inventory.yml bootstrap.yml
```

Install the dependencies from `requirements.txt` into `.venv` first.
Initial access uses normal Ansible SSH settings: omit connection variables to use
SSH configuration, set `ansible_user` and `ansible_ssh_private_key_file` for a
specific key, or pass `--ask-pass` for password access. For an initial non-root
account, enable `bootstrap_become` and use `--ask-become-pass` when needed.
Store inventory passwords with Ansible Vault, never in this repository.

Bootstrap creates the configured administrator with a public key and passwordless
sudo. It checks a fresh key-only login and sudo before disabling root and password
SSH access, then validates the effective SSH configuration and checks access again.
On subsequent runs it falls back to the administrator if initial access is disabled.
Do not override connection settings with `-e ansible_user=...`: extra variables
prevent this switch. Use `bootstrap_admin_ssh_extra_args` for any required jump host
options during the administrative connection.

It performs a full dist-upgrade, autoremove and cache cleanup, installs minimal
packages, sets UTC and optionally `bootstrap_hostname`. It does not reboot.
Keep console access and a recovery method available for first provisioning.
Check mode is rejected because it cannot verify a newly created login.

Fail2ban enables only its SSH jail through an early baseline configuration;
project jail files can override it. UFW inserts an SSH rate limit and enables the
firewall without resetting rules or changing configured default policies.
On a fresh host UFW's packaged defaults apply; allow any other required services
before enabling the firewall. Existing project rules remain in place. Later project
runs may override these shared settings.

Validate without connecting to a server:

```sh
bin/ansible-playbook -i inventory-examples/bootstrap.yml bootstrap.yml --syntax-check
.venv/bin/python tests/check_bootstrap.py
```
