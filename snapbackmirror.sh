#!/bin/bash

# Utility for performing backups while retaining multiple historical
# snapshots. Each snapshot version is available as a full-fledged copy
# that can be browsed to see all of the files at that instant in time.
# Hard links of all files that are the same keep the storage requirements
# to a minimum.

# Just edit the configuration options here as desired, mount your external 
# drive to $backdir, and run this script with no arguments.

# CONFIGURATION OPTIONS

# Space-delimited list of filesystems to back up, no leading or trailing /;
# specify "root" for /; rsync will not cross filesystem boundaries
fs_to_backup="root home"

# Backups will be stored here as backup.0, backup.1, etc.
backdir=/mnt/encfs

# Keep last max_history historical versions
max_history=15

# Additional rsync options: exclude unneeded directories,
# other options as desired (e.g. --xattrs, --acls)
rsync_opts="--exclude=var/cache/apt-cacher --exclude=var/spool/squid"

# END OF CONFIG OPTIONS

# Ensure that backup directory is mounted
z=$( df "$backdir" )
if [ -z "$z" ]
then
   echo "Oops -- $backdir doesn't appear to be mounted"
   exit 1
fi

# Delete the oldest rotation
if [ -e "$backdir/backup.$max_history" ]
then
    /bin/rm -rf "$backdir/backup.$max_history"
fi

# Rename the newer daily rotations, leaving backup.0 unused
for f in $( seq $((max_history-1)) -1 0 )
do
    if [ -e "$backdir/backup.$f" ]
    then
	f1=$(($f+1))
        /bin/mv "$backdir/backup.$f" "$backdir/backup.$f1"
    fi
done

# Recreate backup.0 so we can populate it
mkdir "$backdir/backup.0"

# Back up each filesystem one at a time
for f in $fs_to_backup
do
    case $f in
        # Can put any filesystem-specific mapping/processing here;
        # g is the actual directory being rsync'ed from and must end
        # in a slash
        root)
            g=/
            ;;
        *)
            g=/$f/
            ;;
    esac

    rsync -av --numeric-ids --one-file-system --delete --hard-links --sparse \
        $rsync_opts \
        --link-dest="$backdir/backup.1/$f" "$g" "$backdir/backup.0/$f"
done

# Put a timestamp in this backup directory
/bin/date > "$backdir/backup.0/now"

