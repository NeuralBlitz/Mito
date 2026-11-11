#!/usr/bin/env python3
"""Generate a PBKDF2-SHA256 password verifier for MITO_JWT_USERS.

Usage: python3 scripts/hash_password.py
This script does not write the password or verifier to disk.
"""
from getpass import getpass
from hashlib import pbkdf2_hmac
from secrets import token_bytes


def main():
    password = getpass("New Mito API user password: ")
    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters long")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    salt = token_bytes(16)
    iterations = 260_000
    digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    print("pbkdf2_sha256$" + str(iterations) + "$" + salt.hex() + "$" + digest.hex())
    print("Store the verifier (not the password) under the username in MITO_JWT_USERS.")


if __name__ == "__main__":
    main()
