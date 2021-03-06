#!/usr/bin/env python

import subprocess
import re
import argparse
import logging
import threading
import logging
from queue import Queue
from threading import Thread
from getpass import getpass

SVN_BASE_CALL = ["svn"]
SVN_DEPTH = "immediates"
DEFAULT_NR_PROCESSES = 3

def exec_and_output(args):
    return subprocess.check_output(args, universal_newlines=True,
                                   stderr = subprocess.PIPE)

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

def list_svn(svn_url, username, password):
    args = SVN_BASE_CALL[:]
    args.append("ls")
    args.append(svn_url)
    if username:
        args.append("--username")
        args.append(username)
    if password:
        args.append("--no-auth-cache")
        args.append("--password")
        args.append(password)
    args.append("--depth")
    args.append(SVN_DEPTH)
    args.append("--non-interactive")
    output = exec_and_output(args)
    paths = output.splitlines()
    return paths

def filter_dirs(paths):
    return [x for x in paths if x.endswith('/')]

def join_sub_paths(path, subpaths):
    return [path + subpath for subpath in subpaths]

def output_worker(output_queue, output_file, quiet):
    while True:
        item = output_queue.get()
        if item is None:
            break
        if not quiet:
            print(item)
        if output_file:
            output_file.write(item + '\n')

def list_svn_recursive_worker(svn_url, username, password,
                              list_queue, output_queue,
                              stops, filters):
    while True:
        task = list_queue.get()
        if task is None:
            break

        try:
            # Executes callback for each path
            new_subpaths = list_svn(svn_url + task, username, password)
            new_paths = join_sub_paths(task, new_subpaths)
            filtered_new_paths = filter_by_patterns(filters, new_paths)
            for path in filtered_new_paths:
                output_queue.put(path)

            # Recursively list all directories
            new_paths_dirs = filter_dirs(new_paths)
            excluded_new_paths_dirs = exclude_by_patterns(stops, new_paths_dirs)
            for excluded_new_path_dir in excluded_new_paths_dirs:
                list_queue.put(excluded_new_path_dir)
        except subprocess.CalledProcessError as ex:
            logging.error(ex.stderr)

        list_queue.task_done()

def list_svn_recursive(svn_url, username, password,
                       nthreads = DEFAULT_NR_PROCESSES,
                       stops = [], filters = [],
                       output_path = None, quiet = False):
    output_queue = Queue()
    list_queue = Queue()

    # Opens file for writing
    output_file = None
    if output_path:
        output_file = open(output_path, 'w')

    # Starts the print worker
    output_thread = Thread(target = output_worker,
                           args = (output_queue, output_file, quiet))
    output_thread.start()

    # Starts the recursive list workers
    list_threads = []
    for i in range(nthreads):
        list_thread = Thread(target = list_svn_recursive_worker,
                             args = (svn_url, username, password,
                                     list_queue, output_queue,
                                     stops, filters))
        list_threads.append(list_thread)
        list_thread.start()

    # Wait for list workers to finish
    list_queue.put("")
    list_queue.join()

    # Terminate list workers
    for i in range(nthreads):
        list_queue.put(None)
    for list_thread in list_threads:
        list_thread.join()

    # Terminate printer worker
    output_queue.put(None)
    output_thread.join()

    # Close file
    if output_file:
        output_file.close()

def parse_args():
    parser = argparse.ArgumentParser(description='List subversion URL recursively.')
    parser.add_argument('url', help = 'the repository url')
    parser.add_argument('--nthreads', type = int, default = DEFAULT_NR_PROCESSES,
                        help = "maximum number of parallel list processes")
    parser.add_argument('--stop', metavar = 's', nargs = '*',
                        help = 'stop recursion pattern')
    parser.add_argument('--filter', metavar = 'f', nargs = '*',
                        help = 'filter result pattern')
    parser.add_argument('--only-trunk-dirs', action='store_true',
                        help = "Lists only trunk directories")
    parser.add_argument('--username', default=None, help="svn username")
    parser.add_argument('--ask-password', action='store_true',
                        help="ask for svn password")
    parser.add_argument('--output-path', default=None,
                        help="Path to output result")
    parser.add_argument('--quiet', action='store_true',
                        help="Does not output to stdout")
    return parser.parse_args()

def main():
    args = parse_args()

    url = args.url
    nthreads = args.nthreads
    stops = args.stop
    filters = args.filter
    username = args.username
    ask_password = args.ask_password
    output_path = args.output_path
    quiet = args.quiet

    password = None
    if ask_password:
        password = getpass('Password: ')

    if args.only_trunk_dirs:
        stops = ["trunk/$", "branches/$", "tags/$"]
        filters = [".*/trunk/"]

    list_svn_recursive(url, username, password,
                       nthreads, stops, filters,
                       output_path, quiet)

if __name__ == '__main__':
    main()
