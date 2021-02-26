import os
'''
import sys
'''
from argparse import ArgumentParser
import hashlib

'''
search for all file objects (any kind) and store the info in a dictionary
'''
def searchPath(path, repo, epRepo, snRepo):
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    BUF_SIZE = 65536
    files = os.listdir(path)
    for file in files:
        shortFile = file
        file = path + "/" + file
        fAttr = {}
        try:
            statFile = os.stat(file,follow_symlinks=False)
            fAttr["st_size"] = statFile.st_size
        except:
            print("Error while stat: {0}".format(file))
        if os.path.isfile(file):
            fAttr["st_type"] = "f"
            try:
                with open(file, 'rb') as f:
                    while True:
                        data = f.read(BUF_SIZE)
                        if not data:
                            break
                        #md5.update(data)
                        sha256.update(data)
                    #fAttr["md5"] = md5.hexdigest()
                    sha256sum = sha256.hexdigest()
                    fAttr["sha256"] = sha256sum
                    # create/add reference in sha256repo
                    try:
                        epRepo[sha256sum].append(file)
                        #print("try {0}\n".format(epRepo[sha256sum]))
                    except:
                        epRepo[sha256sum] = [file]
                        #print("except {0}\n".format(epRepo[sha256sum]))
                    # create/add reference in shortNameRepo
                    try:
                        snRepo[shortFile].append(file)
                    except:
                        snRepo[shortFile] = [file]

            except ArithmeticError:
                print("Error while reading: {0}".format(file))
        elif os.path.islink(file):
            fAttr["st_type"] = "l"
        elif os.path.isdir(file):
            fAttr["st_type"] = "d"
            searchPath(file, repo, epRepo, snRepo)
        repo[file] = fAttr
        '''
        print an info every ... found elements
        '''
        count = len(repo)
        if count % 100 == 0:
            print("Found {0} elements".format(count))

def listItems(repo):
    print(repo)

def checkDoubles(repo, epRepo):
    '''
    checkDoubles output files with same size and sha256 hash value
    '''
    #print(epRepo)
    for k in epRepo.keys():
        # first we check, if we have more than one file with same hash value
        if len(epRepo[k]) > 1:
            #print("candidates: Seams to have the same file content: {0}".format(epRepo[k]))
            # now we check, if all candidates have also same st_size
            candidates = epRepo[k]
            first = candidates.pop(0)
            #print("first: {0}".format(repo[first]))
            for file in epRepo[k]:
                #print("file: {0}".format(repo[file]))
                if repo[file]['st_size'] == repo[first]['st_size']:
                    print("doubles: {0} has same size and sha256sum as {1}".format(first, file))
        #except:
        #    print("Error in epRepo for object {0}".format(k))

def checkSameShortName(repo, snRepo):
    '''
    checkSameShortName check files (f) for same name but different sha256 value
    '''
    for k in snRepo.keys():
        if len(snRepo[k]) > 1:
            #print("candidates: Seams to have the same short file name: {0}".format(snRepo[k]))
            candidates = snRepo[k]
            first = candidates.pop(0)
            #print("first: {0}".format(repo[first]))
            for file in snRepo[k]:
                #print("file: {0}".format(repo[file]))
                if repo[file]['sha256'] != repo[first]['sha256']:
                    print("variants: {0} has same name but different sha256sum as {1}".format(first, file))

'''
init
'''
cmdLineParser = ArgumentParser()
filesRepo = {}
sha256Repo = {}
shortNameRepo = {}

cmdLineParser.add_argument("-d", "--directory", dest="path", default=".")

args = cmdLineParser.parse_args()

searchPath(args.path, filesRepo, sha256Repo, shortNameRepo)

#listItems(filesRepo)

checkDoubles(filesRepo, sha256Repo)

checkSameShortName(filesRepo, shortNameRepo)
