# sshfsmounter
Quick utility to keep track of all the remote file systems you want to connect to.

#How it works
This script reads /etc/smount.conf for configuration settings to determine what user will be mounting remote directories over SSHFS. Then, it reads /root/.smount for configuration settings for each remote site that you might want to mount to your local file system. When you launch the script, and mount a remote file system, it will mount it at /home/YourUserAsDictatedInTheEtcSmountConfFile/sshfs/[remotedirname] and you'll be able to easily access that remote file system, work on it directly, make changes, etc...

#Where it stores stuff.

## Global settings
Global settings are stored in /etc/smount.conf
Contents of /etc/smount.conf
Should look like this:

     [smount]
     home = /home/youruser/sshfs/

Where *youruser* is the username where you want to access the remote files. Presumably, your own username. But, don't bother doing this manually. use *config set home* in the CLI to set this.

## Site settings
Site settings are stored in /root/.smount.
All site settings are stored as pipe-separated values on a single line.

# BEFORE YOU INSTALL
This script relies on ssh key authentication. Make sure you have properly setup key authentication for the users and servers you plan on using this with!

# Installation
I recommend that you clone this into /usr/src/, and use a symbolic link from /usr/local/bin/smount -> /usr/src/sshfsmounter/smount.py.

#Creating remote shares

     sudo smount

Run the command *createmount* and press enter. Fill in the information as requested.

#Commands
This script allows for tab completion, so you can see other commands and command hints as needed. Currently, the supported commands are:
1. config
2. createmount
3. exit
4. mount
5. sites
6. unmount
7. version
8. 

#config
Supported command: config set home [path] 
This sets the home directory of your user and saves it in /etc/smount.conf

#createmount
Creates a remote share and askes for a name (friendly name), the username for the remote server you're conenctiong to, the address of the remote server (IP or FQDN are both acceptable, but IP is preferred), and the remote directory you want to mount to /home/youruser/sshfs/.

This information is stored in ~/.smount

#help
Shows license information. Should be updated to include the text from this readme.

#mount
Mounts a remote directory. *Use tab completion to get a list of saved sites available for remote mounts!*

#sites
Commands:
1. sites show
2. sites reload

*sites show* will show you all the sites you have saved and their corresponding connection information.
*sites reload* will reload all sites from ~/.smount

#unmount
Unmounts a remote share. You can unmount them one at a time, or you can use *unmount all*.

#version
Doesn't work. Has been replaced with *help*.
