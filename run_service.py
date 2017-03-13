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

from service.request_broker import start_web_service
import sys
import getopt


def main(argv):
    """
    Synopsis:
        Starts Snape service with given parameters.
    :param argv: command line arguments. need to contain
        1. ip: the IP on which Snape should be registered
        2. port: the port on which Snape should be listening
    """
    IP = '127.0.0.1'
    PORT = 20030

    try:
        opts, args = getopt.getopt(argv, "hi:p:", ["ip=", "port="])
    except getopt.GetoptError:
        print 'Usage: run_service.py -i <ip> -p <port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'run_service.py -i <ip> -p <port>'
            sys.exit()
        elif opt in ("-i", "--ip"):
            IP = arg
        elif opt in ("-p", "--port"):
            PORT = arg

    start_web_service(host = IP, port = PORT)


if __name__ == "__main__":
    main(sys.argv[1:])
