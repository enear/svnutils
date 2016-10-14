#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Emanuel
#
# Created:     12/10/2016
# Copyright:   (c) Emanuel 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import subprocess
import re
import argparse
from collections import deque
from multiprocessing import Pool

SVN_BASE_CALL = ["svn", "--non-interactive", "--no-auth-cache"]
SVN_DEPTH = "immediates"

def exec_and_output(args):
    return subprocess.check_output(args)

def match_any(patterns, string):
    if patterns:
        for pattern in patterns:
            if re.search(pattern, string):
                return True
        return False
    else:
        return False

def filter_by_patterns(filters, strings):
    return [string for string in strings if not filters or match_any(filters, string)]

def exclude_by_patterns(excludes, strings):
    return [string for string in strings if not match_any(excludes, string)]

def list_svn(svnUrl):
    args = SVN_BASE_CALL[:]
    args.append("ls")
    args.extend(svnUrl.split())
    args.append("--depth")
    args.append(SVN_DEPTH)
    output = exec_and_output(args)
    paths = output.splitlines()
    return paths

def filter_dirs(paths):
    return [x for x in paths if x.endswith('/')]

def join_sub_paths(path, subpaths):
    return [path + subpath for subpath in subpaths]

def print_path(svnURl, path):
    print svnURl + "/" + path

def list_svn_recursive_worker(svnUrl, tasks, stops = [], filters = [],
                              callback = print_path):
    task = tasks.pop()
    # Get list paths
    new_subpaths = list_svn(svnUrl + task)
    # Construct full paths
    new_paths = join_sub_paths(task, new_subpaths)
    # Filter paths new 'filters'
    filtered_new_paths = filter_by_patterns(filters, new_paths)
    # Get only directories
    new_paths_dirs = filter_dirs(new_paths)
    # Exclude paths with 'stops'
    excluded_new_paths_dirs = exclude_by_patterns(stops, new_paths_dirs)
    # Add new tasks has the excluded tasks
    tasks.extend(excluded_new_paths_dirs)
    for path in filtered_new_paths:
        callback(svnUrl, path)

def list_svn_recursive(svnUrl, stops = [], filters = [], callback = print_path):
    tasks = deque([""])
    while tasks:
        list_svn_recursive_worker(svnUrl, tasks, stops, filters, callback)

def parse_args():
    parser = argparse.ArgumentParser(description='List subversion URL recursively.')
    parser.add_argument('url', help = 'the repository url')
    parser.add_argument('--stop', metavar = 's', nargs = '*',
                        help = 'stop recursion pattern')
    parser.add_argument('--filter', metavar = 'f', nargs = '*',
                        help = 'filter result pattern')
    return parser.parse_args()

def main():
    args = parse_args()
    list_svn_recursive(args.url, args.stop, args.filter)

if __name__ == '__main__':
    main()
