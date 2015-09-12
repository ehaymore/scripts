#!/usr/bin/env python

'''Compute MD5 sums of a list of files, compare them against a stored
list of sums, report any differences, and update the stored list of sums.

Usage: find / -type f -print0 | bitrot_check.py md5sum_savefile

    md5sum_savefile must exist
'''

from __future__ import print_function

import sys
import os
import csv
import hashlib
import traceback

# Read files to hash in chunks of this many bytes
CHUNKSIZE = 1024*1024

usage_str = '''Usage: bitrot_check.py savefilename

Compute MD5 sums of a list of files, compare them against a stored
list of sums, report any differences if the file timestamp (ctime) hasn't
changed, and update the stored list of sums.  List of filenames to check must
be provided on stdin, null-terminated, for example:

find / /home -xdev -type f -print0 | bitrot_check.py md5sum_savefile
'''

def read_stored_hashes(fname):
    '''Read the previously-stored hashes from fname and a return a
        dict with { fname : (ctime, hash), ... }.
    '''
    hashes = {}     # { fname : (ctime, hash), ... }
    try:
        with file(fname) as fp:
            for ctime, md5sum, fname in csv.reader(fp):
                hashes[fname] = (ctime, md5sum)
    except IOError:
        # File probably doesn't exist; if there's a real problem,
        # we'll see it when we try to write the file at the end
        pass
    return hashes

def compute_current_hashes(fnamelist):
    '''Given a list of files, look up their ctimes, compute hashes, and
        return a dict similar to what read_stored_hashes() provides.
    '''
    hashes = {}
    for fname in fnamelist:
        try:
            with file(fname) as fp:
                # Integer time resolution is good enough, and we'll
                # need it stringified to compare it with the time strings
                # read from csv and to write it to csv
                ctime = str(int(os.path.getctime(fname)))
                md5sum = hashlib.md5()
                chunk = fp.read(CHUNKSIZE)
                while chunk:
                    md5sum.update(chunk)
                    chunk = fp.read(CHUNKSIZE)
            hashes[fname] = (ctime, md5sum.hexdigest())
        except IOError:
            # It might have been deleted already
            if os.path.exists(fname):
                print('Failed read:', fname, file=sys.stderr)
        except Exception:
            traceback.print_exc()
    return hashes

def compare_hashes(stored, current):
    '''Compare the just-computed file hashes to the stored hashes, return
         a tuple of 
         (number of compared files, number of failed hash compares).
         File hashes are compared only when they have the same ctime
         (truncated to integer seconds).
    '''
    num_compared = num_errors = 0
    for fname, current_tup in current.iteritems():
        # current_tup has (ctime, hash)
        if fname in stored:
            num_compared += 1
            stored_ctime, stored_hash = stored[fname]
            current_ctime, current_hash = current_tup
            if stored_ctime == current_ctime and stored_hash != current_hash:
                num_errors += 1
                print('Difference in', fname)
    return (num_compared, num_errors)

def save_hashes(current, outfname):
    '''Write a dict of hashes out to disk to save for the next run.
        current is a dict returned from compute_current_hashes().
        outfname is an output filename with full path.
    '''
    fnames = sorted(current.keys())
    with file(outfname, "wt") as fp:
        csvfp = csv.writer(fp)
        for fname in fnames:
            csvfp.writerow((current[fname][0], current[fname][1], fname))

def main(args):
    '''Run all processing - read stored hashes, compute new hashes,
        compare, save the new hashes, and report differences.
    '''
    savename = args[1]
    stored = read_stored_hashes(savename)
    current_fnames = filter(None, sys.stdin.read().split('\0'))
    current = compute_current_hashes(current_fnames)
    num_compared, num_errors = compare_hashes(stored, current)
    save_hashes(current, savename)
    print(num_compared, 'files compared')
    if num_errors:
        print(num_errors, 'FILE ERRORS!!!!!!!!!!!!')

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == '-h':
        print(usage_str, file=sys.stderr)
        sys.exit(1)
    main(sys.argv)

