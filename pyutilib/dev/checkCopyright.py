#!/usr/bin/env python
#
# A script that verifies that suitable copyright statements are 
# defined in files.
#

import sys
import os
import re

suffixes = ['.c', '.cc', '.h', '.H', '.cpp', '.py']
pat = re.compile('Copyright')

def recurse(dir):
    for root, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            for suffix in suffixes:
                if filename.endswith(suffix):
                    yield os.path.join(root,filename)

def match(filename):
    INPUT = open(filename,'r')
    for line in INPUT:
        if pat.search(line):
            return True
    return False

def main():
    nfiles = 0
    badfiles = []
    for dir in sys.argv[1:]:
        for filename in recurse(dir):
            nfiles += 1
            if not match(filename):
                badfiles.append(filename)

    print("Total number of files missing copyright: "+str(len(badfiles)))
    print("Total number of files checked:           "+str(nfiles))
    if len(badfiles) > 0:
        print("")
        print("Bad Files")
        print("-" * 40)
        for filename in badfiles:
            print(filename)

if __name__ == '__main__':
    main()
