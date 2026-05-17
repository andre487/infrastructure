#!/usr/bin/env python3
import subprocess as sp
import sys


def main():
    content = sys.stdin.read()
    sp.check_call(["ansible-vault", "encrypt_string", "--output", "-", content])


if __name__ == "__main__":
    main()
