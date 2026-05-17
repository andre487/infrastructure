#!/usr/bin/env python3
import re
import subprocess as sp
import sys
import tempfile


def main():
    raw_content = sys.stdin.read()
    res = re.search(r"(\$ANSIBLE_VAULT;.+)", raw_content, re.DOTALL)
    if not res:
        raise Exception("No matches found")

    content = res[0].replace(" ", "")
    with tempfile.NamedTemporaryFile() as f:
        f.write(content.encode("utf8"))
        f.seek(0)
        sp.check_call(["ansible-vault", "decrypt", "--output", "-", "-"], stdin=f)


if __name__ == "__main__":
    main()
