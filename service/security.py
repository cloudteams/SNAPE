# coding=utf-8

"""
Copyright (c) 2016, 2017 FZI Forschungszentrum Informatik am Karlsruher Institut für Technologie

This file is part of SNAPE.

SNAPE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SNAPE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SNAPE.  If not, see <http://www.gnu.org/licenses/>.
"""

from config import *
import shelve
import hashlib
import os
import string
import random


def is_int_castable(s):
    """
    Synopsis:
        Returns True if s can be type-cast to int, False otherwise.
    :param s: entity to check
    :returns castable: boolean
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def allowed_file(filename):
    """
    Synopsis:
        Checks if a given filename is allowed, i.e. contains exactly one '.' and ends on an allowed extension.
    :param filename: filename to check
    :returns allowed: boolean
    """
    if filename.count('.') != 1:
        return False
    suffix = filename.rsplit('.', 1)[-1]
    if len(suffix) < 3:
        return False
    return suffix[0] + suffix[1] + suffix[2] in ALLOWED_EXTENSIONS


def server_password_is_valid(password):
    """
    Synopsis:
        Calculates SHA-512 hash of server secret and compares to stored hash.
        Hash is used in order to avoid storage of correct server secret.
    :param password: password to be checked for validity
    :returns valid: boolean
    """
    password_hash = hashlib.sha512(password).hexdigest()
    with open(os.path.join('resources', 'server-secret-hash.txt'), 'r') as hash_file:
        correct_hash = hash_file.read()
    return password_hash == correct_hash


def shutdown_password_is_valid(password):
    """
    Synopsis:
        Calculates SHA-512 hash of the shutdown routine secret and compares to stored hash.
        Hash is used in order to avoid storage of correct shutdown routine secret.
    :param password: password to be checked for validity
    :returns valid: boolean
    """
    password_hash = hashlib.sha512(password).hexdigest()
    with open(os.path.join('resources', 'shutdown-server-secret-hash.txt'), 'r') as hash_file:
        correct_hash = hash_file.read()
    return password_hash == correct_hash


def token_is_valid(project_id, token):
    """
    Synopsis:
        Checks if a user submitted token is valid for a given project.
    :param project_id: ID of the project for which validation is checked
    :param token: token for which the access rights are checked
    :returns valid: boolean
    """
    valid = False
    try:
        token_file = shelve.open('token_list')
        if token in token_file[str(project_id)]:
            valid = True
        token_file.close()
    finally:
        return valid


def generate_token(existing_tokens):
    """
    Synopsis:
        Generate unique user security tokens for project login.
        Tokens are composed of ASCII letters and digits, but not special characters.
    :param existing_tokens: list of tokens already in use
    :returns token: string
    """
    chars = string.ascii_letters + string.digits
    rnd = random.SystemRandom()
    res = ''.join(rnd.choice(chars) for _ in range(TOKEN_LENGTH))
    while res in existing_tokens:
        rnd = random.SystemRandom()
        res = ''.join(rnd.choice(chars) for _ in range(TOKEN_LENGTH))
    return res
