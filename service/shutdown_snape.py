#!/usr/bin/env python
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

from subprocess import call

with open('resources/shutdown-secret.txt', 'r') as secret_file:
    secret = secret_file.read()

call(["curl", "-k", "-X", 'POST', '--header', 'Content-Type: application/json', '-d',
      '{"password":"%s"}' % secret, 'https://127.0.0.1:20030/shutdown'])
