"""Offline checks for bootstrap's access-preservation ordering."""
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
play = yaml.safe_load((root / "bootstrap.yml").read_text())[0]
tasks = play["tasks"]
names = [task["name"] for task in tasks]
assert names.index("Verify non-interactive sudo before disabling old access") < names.index(
    "Harden SSH only after verified administrative access"
)
initial = tasks[1]["block"][0]
assert initial["ansible.builtin.raw"] == "/bin/true"
assert initial["ignore_unreachable"] is True
key_task = next(t for t in tasks if "ansible.posix.authorized_key" in t)
assert key_task["ansible.posix.authorized_key"]["exclusive"] is False
firewall = [t["community.general.ufw"] for t in tasks if "community.general.ufw" in t]
assert all("default" not in rule and rule.get("state") != "reset" for rule in firewall)
helper = yaml.safe_load((root / "tasks/bootstrap-admin-connection.yml").read_text())
facts = helper[0]["ansible.builtin.set_fact"]
assert facts["ansible_password"] == ""
assert "PasswordAuthentication=no" in facts["ansible_ssh_extra_args"]
example = (root / "inventory-examples/bootstrap.yml").read_text()
assert not any(value in example for value in ("andre487", "jethelix", "id_ecdsa"))
assert "203.0.113.10" in example
print("Bootstrap offline checks passed")
