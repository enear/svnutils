import subprocess
import argparse
import logging
import re
from enum import Enum
from os.path import isdir
from getpass import getpass
from urllib.parse import urlparse

SVN_COMMAND = 'svn'
INFO_PATTERN = '^([^:]+): (.*)$'

class SubCommand(Enum):
    Checkout = 'checkout'
    Update = 'update'
    Info = 'info'

class Depth(Enum):
    Empty = 'empty'
    Files = 'files'
    Immediates = 'immediates'
    Infinity = 'infinity'

def _exec_and_output(args):
    return subprocess.check_output(args, universal_newlines=True,
                                   stderr = subprocess.PIPE)

def _parse_info(output):
    parsed = {}
    line_regex = re.compile(INFO_PATTERN)
    for line in output.splitlines():
        match = line_regex.search(line)
        if match:
            key = match.group(1)
            value = match.group(2)
            parsed[key] = value
    return parsed 

def _add_global_options(args, username=None, password=None,
        no_auth_cache=False, non_interactive=False):
    if username:
        args.append('--username')
        args.append(username)
    if password:
        args.append('--password')
        args.append(password)
    if no_auth_cache:
        args.append('--no-auth-cache')
    if non_interactive:
        args.append('--non-interactive')

def checkout(url, path, username=None, password=None, no_auth_cache=False,
        non_interactive=False, quiet=False, depth=Depth.Empty):
    args = [SVN_COMMAND]
    args.append('checkout')
    _add_global_options(args, username, password, no_auth_cache,
                        non_interactive)
    if depth:
        args.append('--depth')
        args.append(depth)
    if quiet:
        args.append('--quiet')
    args.append(url)
    args.append(path)
    return subprocess.run(args, check=True)

def update(path, username=None, password=None, no_auth_cache=False,
        non_interactive=False, depth=Depth.Empty, parents=False):
    args = [SVN_COMMAND]
    args.append('update')
    _add_global_options(args, username, password, no_auth_cache,
                        non_interactive)
    if parents:
        args.append('--parents')
    if depth:
        args.append('--set-depth')
        args.append(depth)
    args.append(path)
    return subprocess.run(args, check=True)

def info(path, username=None, password=None, no_auth_cache=False,
        non_interactive=False):
    args = [SVN_COMMAND]
    args.append('info')
    _add_global_options(args, username, password, no_auth_cache,
                        non_interactive)
    args.append(path)
    output = _exec_and_output(args)
    return _parse_info(output)

def _parse_args():
    parser = argparse.ArgumentParser(description='Subversion wrapper')
    parser.add_argument('subcommand', choices=[s.value for s in SubCommand],
                        help='subcommand')
    parser.add_argument('--username', default=None, help="Username")
    parser.add_argument('--password', default=None, help="Password")
    parser.add_argument('--no-auth-cache', default=False,
                        help="Do not cache authentication tokens")
    parser.add_argument('--non-interactive', default=False,
                        help="Do no interactive prompting")
    return parser.parse_args()

def main():
    args = _parse_args()

    subcommand = SubCommand(args.subcommand)
    username = args.username
    password = args.password
    no_auth_cache = args.no_auth_cache
    non_interactive = args.non_interactive

    print(subcommand, username, password, no_auth_cache, non_interactive)

if __name__ == '__main__':
    main()
