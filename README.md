# Subversion Utilities

This project provides a set of utilities for subversion.

## Requirements

Both utilities require Python 3.

## Recursive List

The recursive list does the same the `svn list -R <url>` command but uses
multiple list threads and allows to set filters and stops.

The script includes a detailed usage command:

    $> python recursiveList.py -h
    usage: recursiveList.py [-h] [--nthreads NTHREADS] [--stop [s [s ...]]]
                            [--filter [f [f ...]]] [--only-trunk-dirs]
                            [--username USERNAME] [--ask-password]
                            [--output-path OUTPUT_PATH]
                            url
    
    List subversion URL recursively.
    
    positional arguments:
      url                   the repository url
    
    optional arguments:
      -h, --help            show this help message and exit
      --nthreads NTHREADS   maximum number of parallel list processes
      --stop [s [s ...]]    stop recursion pattern
      --filter [f [f ...]]  filter result pattern
      --only-trunk-dirs     Lists only trunk directories
      --username USERNAME   svn username
      --ask-password        ask for svn password
      --output-path OUTPUT_PATH
                            Path to output result

To output all files recursively:

    $> python3 recursiveList.py <url>

To output only trunk directories:

    $> python3 recursiveList.py <url> --only-trunk-dirs

Which would does the same as executing:

    $> python3 recursiveList.py <url> \
               --stop "trunk/$" "branches/$" "tags/$" \
               --filter ".*/trunk/"

That is, each recursive list thread stops if it finds a `trunk`, `branches` or
`tags` directory and only outputs the `trunk` directories`.

To set a username and password:

    $> python3 recursiveList.py <url> --username <username> --ask-password
    Password: ******

Note that the script is non interactive. If the client does not know the
password for the default username the script exists with an authentication
error without asking for the password.

## Checkout

The checkout utility checks out a given working copy, if it doesn't already
exist, and updates recursively every file or directory that exists in the given
input file.

The script includes a detailed usage command:

    $> python3 checkout.py -h
    usage: checkout.py [-h] [--username USERNAME] [--ask-password]
                       url destination input
    
    Checkout infinity paths in input file
    
    positional arguments:
      url                  The root url
      destination          The destination
      input                The input file
    
    optional arguments:
      -h, --help           show this help message and exit
      --username USERNAME  svn username
      --ask-password       ask for svn password

This script is easier to explain with a concrete example. Let's say we want to
checkout only the `doc/programmer` and `doc\user` from the subversion
repository. To do that first create the following file:

    -- subversion.txt
    doc/programmer
    doc/user

We can accomplish our objective by executing following command:

    $> python3 checkout.py http://svn.apache.org/repos/asf/subversion/trunk \
                           subversion \
                           subversion.txt
    subversion/doc/programmer
    subversion/doc/user


The contents of the checkout are in the `subversion` directory:

    $> find subversion/*                                                                                                                        
    subversion/doc
    subversion/doc/programmer
    subversion/doc/programmer/gtest-guide.txt
    subversion/doc/programmer/WritingChangeLogs.txt
    subversion/doc/user
    subversion/doc/user/cvs-crossover-guide.html
    subversion/doc/user/lj_article.txt
    subversion/doc/user/svn-best-practices.html

You can also update new content by updating the workspace again. Let's say you
add a new file:

    -- subversion.txt
    doc/user
    doc/README

And then execute the same command:

    $> python3 checkout.py http://svn.apache.org/repos/asf/subversion/trunk \
                           subversion \
                           subversion.txt
    subversion/doc/user
    subversion/doc/README

The script updated `doc/user` and `doc/README`. Since `doc/README` didn't
exist, it was added into the working copy.

## Combine utilities

These utilities were designed so that the output from one utility can be used
by another.

To checkout only trunk directories:

    $> python3 recursiveList.py <url> --only-trunk-dirs --output-path list.out
    $> python3 checkout.py <url> <dest> list.out
