# infrastructure

Ansible host bootstrap and package upgrades. Requires `uv`; `bin/ansible*` runs it automatically.

## Setup

```sh
uv sync --locked
```

## Bootstrap

Copy and edit [inventory-examples/bootstrap.yml](inventory-examples/bootstrap.yml), then run:

```sh
bin/ansible-playbook -i ~/bootstrap-inventory.yml bootstrap.yml
```

Creates and verifies key-based admin access before disabling root/password SSH.
Upgrades packages, configures UTC, SSH fail2ban and UFW. No reboot; no check mode.
Use inventory connection settings, not `-e ansible_user=...`.

## Package upgrades

```sh
bin/upgrade-packages                                      # Enter hosts interactively
bin/upgrade-packages -i inventory.yml --limit servers      # Use an inventory
bin/upgrade-packages -u deploy --ask-become-pass           # Set SSH user and prompt for sudo password
```

Hosts accept spaces or commas. With an inventory, all hosts are selected unless limited.
Use `--check --diff` to preview; no automatic reboot.

## Checks

```sh
bin/ansible-playbook -i inventory-examples/bootstrap.yml bootstrap.yml --syntax-check
for check in tests/check_*.py; do uv run --locked python "$check" || exit; done
```
