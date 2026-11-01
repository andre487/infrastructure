#!/usr/bin/env python3
"""Shared host selection for maintenance playbooks."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


HELP = """Usage: bin/{command} [ansible-playbook options]
Prompts for SSH hostnames, aliases or IP addresses, separated by spaces or commas.
With -i/--inventory, uses that inventory without prompting (all hosts unless limited).
Examples:
  bin/{command}
  bin/{command} -u deploy --private-key ~/.ssh/id_ed25519
  bin/{command} --ask-pass --ask-become-pass
  bin/{command} --check --diff
  bin/{command} -i inventory.yml --limit servers
"""


def main(command: str, action: str) -> int:
    args = sys.argv[1:]
    if args and args[0] in ("--help", "-h"):
        print(HELP.format(command=command), end="")
        if command == "docker-clean":
            print("  --volumes  Also prune unused anonymous volumes (without an age filter).")
        return 0
    cleanup_args = []
    if command == "docker-clean":
        volume_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        volume_parser.add_argument("--volumes", action="store_true")
        volume_options, args = volume_parser.parse_known_args(args)
        if volume_options.volumes:
            cleanup_args = ["-e", "docker_clean_volumes=true"]
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("-i", "--inventory", "--inventory-file", action="append")
    options, _ = parser.parse_known_args(args)
    hosts = None
    if options.inventory is None:
        try:
            hosts = input(f"Hosts to {action} (spaces or commas): ").replace(",", " ").split()
        except EOFError:
            hosts = []
        except KeyboardInterrupt:
            print(file=sys.stderr)
            return 130
        if not hosts:
            print("No hosts entered; nothing to do.", file=sys.stderr)
            return 2
        for host in hosts:
            if not re.fullmatch(r"[a-zA-Z0-9_:][a-zA-Z0-9_.:%-]*", host):
                print(f"Invalid host: {host}", file=sys.stderr)
                return 2
        print(f"Targets: {' '.join(hosts)}", flush=True)

    root = Path(__file__).resolve().parents[1]
    runner = str(root / "bin/ansible-playbook")
    playbook_args = [str(root / f"{command}.yml"), "-e", "arg_hosts=all", *cleanup_args, *args]
    if hosts is not None:
        inventory = {"all": {"vars": {"ansible_python_interpreter": "/usr/bin/python3"},
                             "hosts": {host: {} for host in hosts}}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as stream:
            json.dump(inventory, stream)
            stream.flush()
            return subprocess.call([runner, "-i", stream.name, *playbook_args])
    os.execv(runner, [runner, *playbook_args])
