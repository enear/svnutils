import subprocess
import argparse
import re
from enum import Enum
from argparse import ArgumentParser

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

def _info_args(targets, username=None, password=None, no_auth_cache=False,
               non_interactive=False):
    args = [SVN_COMMAND]
    args.append('info')
    _add_global_options(args, username, password, no_auth_cache,
                        non_interactive)
    for t in targets:
        args.append(t)
    return args

def info(targets, username=None, password=None, no_auth_cache=False,
         non_interactive=False):
    args = _info_args(targets, username, password, no_auth_cache,
                      non_interactive)
    return subprocess.run(args, check=True)

def _parse_info(output):
    info_entry = {}
    line_regex = re.compile(INFO_PATTERN)
    for line in output.splitlines():
        match = line_regex.search(line)
        if match:
            key = match.group(1)
            value = match.group(2)
            info_entry[key] = value
    return info_entry

def info_dict(targets, username=None, password=None, no_auth_cache=False,
              non_interactive=False):
    args = _info_args(path, username, password, no_auth_cache,
                      non_interactive)
    output = subprocess.check_output(args, universal_newlines=True,
                                     stderr = subprocess.PIPE)
    return _parse_info(output)

def _global_options_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--username', default=None, help="Username")
    parser.add_argument('--password', default=None, help="Password")
    parser.add_argument('--no-auth-cache', default=False,
                        help="Do not cache authentication tokens")
    parser.add_argument('--non-interactive', default=False,
                        help="Do no interactive prompting")
    return parser

def _subcommand_parser():
    parser = ArgumentParser(description='Subversion wrapper')
    parser.add_argument('subcommand', choices=[s.value for s in SubCommand],
                        help='subcommand')
    return parser

def _checkout_parser():
    sb_parser = _subcommand_parser()
    gb_parser = _global_options_parser()
    parser = ArgumentParser(parents=[sb_parser, gb_parser], add_help=False)
    parser.add_argument('url')
    parser.add_argument('path')
    parser.add_argument('--depth', choices=[d.value for d in Depth],
                        help="Limits operation by depth")
    parser.add_argument('--quiet', default=False,
                        help="Print nothing, or only summary information")
    return parser

def _update_parser():
    sb_parser = _subcommand_parser()
    gb_parser = _global_options_parser()
    parser = ArgumentParser(parents=[sb_parser, gb_parser], add_help=False)
    parser.add_argument('path')
    parser.add_argument('--parents', default=False,
                        help="Make intermediate directories")
    parser.add_argument('--depth', choices=[d.value for d in Depth],
                        help="Limits operation by depth")
    return parser

def _info_parser():
    sb_parser = _subcommand_parser()
    gb_parser = _global_options_parser()
    parser = ArgumentParser(parents=[sb_parser, gb_parser], add_help=False)
    parser.add_argument('targets', metavar='TARGET', nargs='+')
    return parser

def _run_checkout():
    parser = _checkout_parser()
    args = parser.parse_args()

    url = args.url
    path = args.path
    username = args.username
    password = args.password
    no_auth_cache = args.no_auth_cache
    non_interactive = args.non_interactive
    quiet = args.quiet
    depth = Depth(args.depth) if args.depth else None

    checkout(url, path, username, password, no_auth_cache,
             non_interactive, quiet, depth)

def _run_update():
    parser = _update_parser()
    args = parser.parse_args()

    path = args.path
    username = args.username
    password = args.password
    no_auth_cache = args.no_auth_cache
    non_interactive = args.non_interactive
    quiet = args.quiet
    depth = Depth(args.depth) if args.depth else None

    update(path, username, password, no_auth_cache,
           non_interactive, quiet, depth)

def _run_info():
    parser = _info_parser()
    args = parser.parse_args()

    targets = args.targets
    username = args.username
    password = args.password
    no_auth_cache = args.no_auth_cache
    non_interactive = args.non_interactive

    info(targets, username, password, no_auth_cache, non_interactive)

def main():
    parser = _subcommand_parser()
    args, unknown = parser.parse_known_args()

    subcommand = SubCommand(args.subcommand)
    if subcommand is SubCommand.Checkout:
        _run_checkout()
    elif subcommand is SubCommand.Update:
        _run_update()
    elif subcommand is SubCommand.Info:
        _run_info()

if __name__ == '__main__':
    main()
