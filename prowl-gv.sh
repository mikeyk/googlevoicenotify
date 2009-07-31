#!/bin/bash
#
# Script to start/stop the Prowl Google Voice daemon
#
# v1.0 - Tested and working - released.
#
# Copyright (C) 2008 James Bair <james.d.bair@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# Where to find the main script
file=prowlgooglevoice.py
script=$(basename $0)

# Since we check this status a lot, we'll just re-create the variable as needd.
findOurPID() {
	ourPID=$(ps ax | while read pid a b c d script; do [ "$script" == "$file" ] && echo $pid; done)
	export ourPID
}

# General usage function
usage() {
	echo "USAGE: $script - <start|stop|restart>"
}

# Need an argument, no more, no less.
if [ $# -ne 1 ]; then
	usage
	exit 1
fi

# Start
startFile() {

	# Find our PID
	findOurPID

	# Make sure we're not already running.
	if [ -n "$ourPID" ]; then
		echo "$file is already running."
	else
	
		# If it's a file and non-zero, then call it with Python.
		if [ -f $file -a -s $file ]; then
			python $file > /dev/null 2>&1 &
			echo "$file is now running in the background."
		else
			echo "$file is either missing or not executable. Exiting."
			exit 1
		fi
	fi
}

stopFile() {
	
	# Find our PID
	findOurPID

	# Make sure we're actually running.
	if [ -z "$ourPID" ]; then
		echo "$file is not running."
	else

		# Kill the PID and make sure it's gone
		kill $ourPID
		sleep .1
		findOurPID
		if [ -z "$ourPID" ]; then
			echo "$file has been shutdown. Exiting."
		else
			echo "$file is still running. This is a bug, please diagnose."
			echo "ourPID = $ourPID"
			echo "checkPID = $checkPID"
			exit 1
		fi
	fi
}

############
### MAIN ###
############

# Make sure all requird libraries and configs exist
mustHaves="credentials googlevoicenotify.py prowlgooglevoice.py prowlkey prowlpy.py"
for i in $mustHaves; do
	# Verify it's non-zero
	if [ ! -s $i ]; then
		echo "ERROR: Missing required file: $i - Exiting."
		exit 1
	fi
done

# Begin the real work.
case $1 in 
	start)
		startFile
		exit 0
		;;

	stop)
		stopFile
		exit 0
		;;

	restart)
		stopFile && startFile
		exit 0
		;;

	*)
		usage
		exit 1
		;;
esac
