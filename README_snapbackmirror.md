# snapbackmirror.sh
This script is a utility for performing backups while retaining multiple
historical snapshots. Each snapshot version is available as a
full-fledged copy that can be browsed to see all of the files at that
instant in time.

Under the hood it just uses 'rsync' with the --hard-links option which
allows the backup to use only a single copy on disk of all files that
have remained unchanged across snapshot versions.

## Setup

You'll probably need to edit a few configuration options that are
specified at the top of the script:

1. fs\_to\_backup
The specific root-level filesystems to back up. The backup will not
cross filesystem boundaries so you will need to specify each one you
want.  You can run the 'df' command to see a list of all the filesystems
you might want to include in the backup.

Do not include a leading or trailing slash. Also, to include the root
filesystem (i.e. just "/"), specify root.

For example, to back up / and /home, specify

'''
fs\_to\_backup="root home"
'''

2. backdir
Top-level directory where the backups are written to.  The snapshot
directories "backup.0", "backup.1", etc. will be created in this
directory. The filesystems named in fs\_to\_backup will be rsync'ed to
the backup.N directories using directory names given in fs\_to\_backup.

3. max\_history
How many historical snapshot versions to retain. The script will
retain versions backup.0 through backup.$max\_history.

4. rsync\_opts
Any additional options to pass to rsync, such as directories to exclude
from the backups. rsync is already being given

'''
-av --numeric-ids --one-file-system --delete --hard-links --sparse
'''

## Usage

### Insert external drive (optional)

First, you'll probably want to attach an external backup drive, although
the script really doesn't care where the files go to. If you're using an
external drive, insert it now.

### Set up encryption (optional)

You may wish encrypt your backups. The FUSE module
[encfs](https://github.com/vgough/encfs) can provide encryption on the
backups so that all someone else would see is garbage filenames and
encrypted contents.

snapbackmirror.sh itself doesn't handle encryption; it's just a front end
to rsync which knows how to read and write files. But encfs can be used
to provide a transparent encryption layer so that the backup files are
encrypted as they rest on your drive.  encfs lets you map a directory
tree of physical encrypted files to a virtual tree of plain, decrypted
files; you interact with the virtual tree as a set of normal files, and
encfs decrypts and encrypts them as it reads and writes to the physical
drive.

You may need to preface these commands with a sudo, or be the root user,
depending on your system and what you're trying to do. I'll assume the
drive is mounted to /mnt/ext (where the encrypted files physically
reside) and the decrypted filesystem (where the decrypted virtual files
are accessed) is on /mnt/encfs, but this could be anywhere. snapbackmirror.sh
will access the files only on the virtual tree.

1. If it's not done automatically, mount your external drive. If your fstab is
set up, it could be as simple as

        mount /mnt/ext

2. If this is your first time setting up encrypted files on this drive,
create a directory for the encrypted physical files and set up encfs on
it.

        mkdir /mnt/ext/data
        encfs /mnt/ext/data /mnt/encfs

    Let encfs create /mnt/encfs. Select 'x' for the expert
    configuration mode. Select:

    * AES
    * Key size of 256 bits
    * Block size of 1024
    * Block filename encoding
    * Disable filename initialization vector chaining (i.e. answer "n" to the
    question)
    * Enable per-file initialization vectors
    * Disable block authentication code headers
    * Add 0 random bytes to each block header
    * Enable file-hole pass-through
    * Enter a password and don't forget it
    
    The only option that really matters to snapbackmirror.sh is the filename
    initialization vector chaining. When the script renames the historical
    snapshot directories, if this option is enabled encfs will have to
    re-encrypt every one of your files in all the snapshots and this will
    make the backup take *much* longer.
    
    You'll now be able to write files to /mnt/encfs and have the encrypted
    version physically stored in /mnt/ext/data.

3. If you skipped step 2 because this is not your first time setting up
encrypted files, you'll need to start encfs running:

        encfs /mnt/ext/data /mnt/encfs

### Perform the backup

Just run snapbackmirror.sh without any arguments and it will perform the
backup. Note that the first time you'll see a harmless warning that says
"--link-dest arg does not exist".

When it's complete, you should be able to do

```
ls -alR /mnt/encfs
```

and see all of the backed-up files in all snapshots. You could even do

```
diff -r /mnt/encfs/backup.0/root /
```

(substituting whatever filesystem you want to compare) to be sure.

### Remove the external drive (optional)

Cleanly unmount the external drive and remove it. You're done!

