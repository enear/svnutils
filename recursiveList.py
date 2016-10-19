import subprocess
import re
import argparse
import logging
import threading
import logging
from queue import Queue
from threading import Thread

SVN_BASE_CALL = ["svn", "--non-interactive", "--no-auth-cache"]
SVN_DEPTH = "immediates"
DEFAULT_NR_PROCESSES = 3

def exec_and_output(args):
    return subprocess.check_output(args, shell=True, universal_newlines=True,
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

def list_svn(svnUrl):
    args = SVN_BASE_CALL[:]
    args.append("ls")
    args.append(svnUrl)
    args.append("--depth")
    args.append(SVN_DEPTH)
    output = exec_and_output(args)
    paths = output.splitlines()
    return paths

def filter_dirs(paths):
    return [x for x in paths if x.endswith('/')]

def join_sub_paths(path, subpaths):
    return [path + subpath for subpath in subpaths]

def print_path(path):
    print(path)

def list_svn_recursive_worker(svn_url, tasks, stops = [], filters = [],
                              callback = print_path):
    while True:
        try:
            task = tasks.get()
            if task is None:
                tasks.task_done()
                break
            else:
                # Executes callback for each path
                new_subpaths = list_svn(svn_url + task)
                new_paths = join_sub_paths(task, new_subpaths)
                filtered_new_paths = filter_by_patterns(filters, new_paths)
                for path in filtered_new_paths:
                    callback(path)

                # Recursively list all directories
                new_paths_dirs = filter_dirs(new_paths)
                excluded_new_paths_dirs = exclude_by_patterns(stops, new_paths_dirs)
                for excluded_new_path_dir in excluded_new_paths_dirs:
                    tasks.put(excluded_new_path_dir)

                # Finishes this task
                tasks.task_done()
        except subprocess.CalledProcessError as ex:
            logging.error(ex)
            logging.error(ex.stderr)
            tasks.task_done()
        else:
            tasks.task_done()

def list_svn_recursive(svn_url, nthreads = DEFAULT_NR_PROCESSES, stops = [],
                       filters = [], callback = print_path):
    tasks = Queue()

    for i in range(nthreads):
        t = Thread(target = list_svn_recursive_worker,
                   args = (svn_url, tasks, stops, filters, callback))
        t.start()

    tasks.put("")
    tasks.join()

    for i in range(nthreads):
        tasks.put(None)
    tasks.join()

def parse_args():
    parser = argparse.ArgumentParser(description='List subversion URL recursively.')
    parser.add_argument('url', help = 'the repository url')
    parser.add_argument('--nthreads', type = int, default = DEFAULT_NR_PROCESSES,
                        help = "maximum number of parallel list processes")
    parser.add_argument('--stop', metavar = 's', nargs = '*',
                        help = 'stop recursion pattern')
    parser.add_argument('--filter', metavar = 'f', nargs = '*',
                        help = 'filter result pattern')
    return parser.parse_args()

def main():
    args = parse_args()
    list_svn_recursive(args.url, args.nthreads, args.stop, args.filter)

if __name__ == '__main__':
    main()