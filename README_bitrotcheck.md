# bitrot\_check
This a utility to check for disk corruption by reading
all files, computing MD5 hashes, and where the file timestamps haven't
changed, comparing to saved MD5 hashes from the previous run.  This is
similar to what some filesystems offer as a built-in feature (e.g. btrfs).

bitrot\_check.sh is intended as simple front-end script to the bitrot\_check.py
which does the real work.

## Setup

1. Copy bitrot\_check.sh and bitrot\_check.py to your desired destination
directory.

2. Edit bitrot\_check.sh as desired; for example, to modify the list of
filenames to check, to put the file with saved hashes elsewhere, or
to find bitrot\_check.py in another location.

3. You may wish to put this in a cron job (perhaps monthly) and have
its output emailed to you.

## Usage

### First run

On its first run, bitrot\_check won't have any saved hashes to compare so
it will simply read all files and save their hashes. It will report
no files compared.

### Second and later runs

On later runs, bitrot\_check will compare files and report any changed
files as well as the total number of files compared.

Changed files are reported only if their timestamp (truncated to
one-second resolution) has not changed, using the file's ctime so that it's
confused by programs that try to modify a file's content without changing
its timestamp.

