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

## Docker cleanup

```sh
bin/docker-clean
bin/docker-clean -i inventory.yml --limit docker
bin/docker-clean -e docker_clean_until=720h
bin/docker-clean --volumes
```

Uses Docker's built-in `system prune`, defaulting to objects created over 7 days ago.
Deletes stopped containers (including their writable layers), unused networks,
dangling images and build cache. Volumes and tagged images are retained by default.
`--volumes` also deletes unused anonymous volumes of any age (requires Docker 23+).
Named volumes remain; Docker does not support the age filter for volume pruning.
`--check` reports disk usage without deleting anything; it does not predict removals.

## Checks

```sh
bin/ansible-playbook -i inventory-examples/bootstrap.yml bootstrap.yml --syntax-check
for check in tests/check_*.py; do uv run --locked python "$check" || exit; done
```
