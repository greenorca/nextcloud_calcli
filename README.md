# nextcloud_calcli
Python based command line extension to display Owncloud/Nextcloud calendar agenda within conky 

![screenshot](doc/Screenshot.png)

## Requirements

- Python3
- caldav library (pip3 install caldav)
- create `.nextcloud_cal.ini` in your home directory. Use the following syntax:

    [DEFAULT]<br>
    user = user<br>
    pwd = guggus<br>
    url = https://yourserver/remote.php/dav/calendars/user/default/<br>


## Adaptations
In .conkyrc just add the following line:

    ${execi 600 python3 /pathTo/nextcloud_cal.py}

