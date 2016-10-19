import subprocess
import argparse

SVN_COMMAND = "svn"
SVN_DETPH_EMPTY = "empty"
SVN_DETPH_INFINITY = "infinity"

def _checkout(url, path):
    return subprocess.run([SVN_COMMAND, "co",
                           "--depth", SVN_DETPH_EMPTY,
                           "--quiet",
                           url, path],
                          check=True)

def _update(path):
    return subprocess.run([SVN_COMMAND, "up",
                          "--parents",
                          "--set-depth", SVN_DETPH_INFINITY,
                          "--quiet",
                          path],
                          check=True)

def _parse_args():
    parser = argparse.ArgumentParser(
      description = "Checkout infinity paths in input file")
    parser.add_argument("url", help="The root url")
    parser.add_argument("destination", help="The destination")
    parser.add_argument("input", help="The input file")
    return parser.parse_args()

def _parse_line(line, destination):
    return destination + "/" + line.rstrip('\n')

def checkout(url, destination, file):
    _checkout(url, destination)
    for line in file:
        path = _parse_line(line, destination)
        _update(path)

def main():
    parser = _parse_args()

    url = parser.url
    destination = parser.destination
    input_path = parser.input

    with open(input_path, 'r') as file:
      checkout(url, destination, file)

if __name__ == "__main__":
    main()
