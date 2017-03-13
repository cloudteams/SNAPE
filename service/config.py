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

ALLOWED_EXTENSIONS = [          # file types that are accepted
    'mdj'
]
ROOT = r'~/example/path'        # SNAPE root path
TOKEN_LENGTH = 128              # number of characters for user identification tokens
MDJ_MAX_SIZE = 5e6              # upper limit of mdj-filesize that is not rejected
USE_SSL = False                 # if true a valid SSL certificate is required
CRT_PATH = r'~/example/path'    # Certificate path. Necessary if USE_SSL is True
KEY_PATH = r'~/example/path'    # Certificate path. Necessary if USE_SSL is True
TOKEN_MAX_REQUEST = 1000        # max number of tokens requestable in one request
