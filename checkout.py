import subprocess
import argparse
from os.path import isdir
from getpass import getpass

SVN_COMMAND = "svn"
SVN_DEPTH_EMPTY = "empty"
SVN_DEPTH_INFINITY = "infinity"

def _checkout(url, path, username, password):
    args = [SVN_COMMAND]
    args.append("co")
    if username:
        args.append("--username")
        args.append(username)
    if password:
        args.append("--password")
        args.append(password)
    args.append("--depth")
    args.append(SVN_DEPTH_EMPTY)
    args.append("--quiet")
    args.append("--non-interactive")
    args.append(url)
    args.append(path)
    return subprocess.run(args, check=True)

def _update(path, username, password):
    args = [SVN_COMMAND]
    args.append("up")
    if username:
        args.append("--username")
        args.append(username)
    if password:
        args.append("--password")
        args.append(password)
    args.append("--parents")
    args.append("--set-depth")
    args.append(SVN_DEPTH_INFINITY)
    args.append("--quiet")
    args.append("--non-interactive")
    args.append(path)
    return subprocess.run(args, check=True)

def _parse_args():
    parser = argparse.ArgumentParser(
      description = "Checkout infinity paths in input file")
    parser.add_argument("url", help="The root url")
    parser.add_argument("destination", help="The destination")
    parser.add_argument("input", help="The input file")
    parser.add_argument('--username', default=None, help="svn username")
    parser.add_argument('--ask-password', action='store_true',
                        help="ask for svn password")
    return parser.parse_args()

def _parse_line(line, destination):
    return destination + "/" + line.rstrip('\n')

def on_complete(path):
  print(path)

def checkout(url, destination, file, username, password):
    if not isdir(destination):
        _checkout(url, destination, username, password)
    for line in file:
        path = _parse_line(line, destination)
        _update(path, username, password)
        on_complete(path)

def main():
    parser = _parse_args()

    url = parser.url
    destination = parser.destination
    input_path = parser.input
    username = parser.username
    ask_password = parser.ask_password
    password = None
    if ask_password:
        password = getpass('Password: ')

    with open(input_path, 'r') as file:
      checkout(url, destination, file, username, password)

if __name__ == "__main__":
    main()
