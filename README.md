# nextcloud_calcli
Python based command line extension to display Owncloud/Nextcloud calendar agenda within conky 

## Requirements

- Python3
- caldav library (pip3 install caldav)
- .nextcloud_cal.ini in your home directory


    [DEFAULT]<br>
    user = user<br>
    pwd = guggus<br>
    url = https://yourserver/remote.php/dav/calendars/user/default/<br>


## Adaptations
In .conkyrc just add the following line:

    ${execi 600 python3 /pathTo/nextcloud_cal.py}

