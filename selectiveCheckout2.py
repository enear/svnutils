#-------------------------------------------------------------------------------
# Name:        selectiveCheckout v2
# Purpose:
#
# Author:      Diogo
#
# Created:     10/10/2016
# Copyright:   (c) Diogo 2016
# Licence:     <your licence>
#
# TOOD:         -increase performance (multithread)
#               -add ignore list to checkout
#               -checkout specific revision
#               -checkout specific tag
#               -checkout specific branch
#-------------------------------------------------------------------------------

import os
import sys, getopt
import subprocess
import getpass

##########################################
##              CONSTANTS               ##
##########################################

SVN_BASE_CALL = ["svn", "--non-interactive", "--no-auth-cache"]

SVN_CHECKOUT_EMPTY = "empty"
SVN_CHECKOUT_FILES = "files"
SVN_CHECKOUT_IMMEDIATES = "immediates"
SVN_CHECKOUT_INFINITY = "infinity"
SVN_CHECKOUT_LEAFS = "leafs"

CHECKOUT_EMPTY = "empty"
CHECKOUT_FULL = "full"
CHECKOUT_TRUNK = "trunk"
CHECKOUT_TAGS = "tags"
CHECKOUT_BRANCHES = "branches"

LEAF_CHECKOUT_TYPES = [CHECKOUT_BRANCHES, CHECKOUT_TAGS, CHECKOUT_TRUNK]


##########################################
##              CLASSES                 ##
##########################################

class Credentials():
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return "Credentials(username = %s, password = ****)" % (self.username)

    def getAsArray(self):
        return ["--username", self.username, "--password", self.password]

class StartupParams():
    def __init__(self, credentials):
        self.svnUrl=""
        self.checkoutType=""
        self.destinationFolder=""
        self.credentials = credentials

    def __str__(self):
        return "StartupParams(svnUrl = %s, checkoutType = %s, destinationFolder = %s, credentials = %s)" % (self.svnUrl, self.checkoutType, self.destinationFolder, self.credentials)


##########################################
##              METHODS                 ##
##########################################

def execAndOutputProcess(args):
    return subprocess.check_output(args)

def execProcess(args):
	rc = subprocess.call(args)
	if rc != 0:
		exit(1)

def addCredentials(credentials):
    return ["--username", credentials.username , "--password", credentials.password]

def checkout(path, credentials, depth):
    print "checking out the root of the repository"

    args = SVN_BASE_CALL[:]
    args.extend(credentials.getAsArray())
    args.append("co")
    args.extend(path.split())
    args.append("--depth")
    args.append(depth)
    execProcess(args)

def update(path, credentials):
    print "updating " + path
    try:
        args = SVN_BASE_CALL[:]
        args.extend(credentials.getAsArray())
        args.append("up")
        args.extend(path.split())
        args.append("--parents")
        execAndOutputProcess(args)
    except:
        e = sys.exc_info()[0]
        print "Error updating " + path
        print e


def sortCheckoutType(startup):
    if startup.checkoutType == CHECKOUT_FULL:
        checkout(startup.svnUrl, startup.credentials, SVN_CHECKOUT_INFINITY)
    elif startup.checkoutType == CHECKOUT_EMPTY:
        checkout(startup.svnUrl, startup.credentials, SVN_CHECKOUT_EMPTY)
    elif startup.checkoutType in LEAF_CHECKOUT_TYPES:
        checkout(startup.svnUrl, startup.credentials, SVN_CHECKOUT_EMPTY)
        searchAndUpdate(startup.svnUrl, startup.credentials, startup.checkoutType, "")
    else:
        print "Invalid checkout option"
        exit(3)

def getHeadDir(path):
    tmp = path.strip()
    if (tmp.endswith("/")):
        tmp = path[:-1]

    return tmp.split("/")[-1]

def listSvn(svnUrl, credentials, depth="immediates"):
    args = SVN_BASE_CALL[:]
    args.extend(credentials.getAsArray())
    args.append("ls")
    args.extend(svnUrl.split())
    args.append("--depth")
    args.append(depth)
    output = execAndOutputProcess(args)

    return output

def searchAndUpdate(svnUrl, credentials, leafCheckoutType, basePath=""):
    try:
        output = listSvn((svnUrl+basePath), credentials)
        paths = output.splitlines()

        for path in paths:
            newPath = basePath+path
            if path.strip('/') in LEAF_CHECKOUT_TYPES:
                if leafCheckoutType in path.strip('/') :
                    update(os.path.join(getHeadDir(svnUrl),newPath), credentials)
                elif path.endswith('/'):
                    continue
            else:
                searchAndUpdate(svnUrl, credentials, leafCheckoutType, newPath)
    except:
        e = sys.exc_info()[0]
        print "Error listing  " + (svnUrl+basePath)
        print e


def usage():
    return '''selectiveCheckout -u <url> -c <checkoutType> -d <destinationFolder>
checkoutType:
    full
    empty
    trunk
    tags
    branches
'''

def promptCredentials():
    username = raw_input("username: ")
    password = getpass.getpass("password: ")

    credentials = Credentials(username, password)

    return credentials

def interactiveCall(argv):
    svnUrl=""
    checkoutType=""
    destinationFolder=""

    try:
        opts, args = getopt.getopt(argv,"h:u:c:d:",["url=","checkout=","destination="])
        if len(opts) < 3:
            print usage()
            sys.exit(2)

    except getopt.GetoptError:
        print usage()
        sys.exit(2)

    startup = StartupParams(promptCredentials())

    for opt, arg in opts:
        if opt == '-h':
            print usage()
            sys.exit()
        elif opt in ("-u", "--url"):
            if (not arg.endswith("/")):
                arg = arg + "/"
            startup.svnUrl = arg
        elif opt in ("-c", "--checkout"):
            startup.checkoutType = arg
        elif opt in ("-d", "--destination"):
            startup.destinationFolder = arg

    return startup

def main(argv):
    startup = interactiveCall(argv)
    os.chdir(startup.destinationFolder)
    sortCheckoutType(startup)

if __name__ == '__main__':
    main(sys.argv[1:])
