#!/bin/bash

# -xdev prevents find from crossing filesystem boundaries so you'll need to
#       specify each filesystem to check.
# -size +1c prevents it from checking 0-length files.
# -not -path excludes a directory tree; multiple paths to exclude can be 
#       specified with Boolean logic (check the find man page) or simply
#       by inserting a grep or grep -v after the find (use grep's -z option)
# -print0 null-terminates each filename so we don't have to worry about
#       special characters in the name
#
# Hashes will be saved in the filename provided as an argument to
# bitrot_check.py.

find / /home -xdev -type f -size +1c -not -path '/home/scratch/backup/*' -print0 | $HOME/bin/bitrot_check.py $HOME/.bitrot_check.dat
chmod 600 $HOME/.bitrot_check.dat


