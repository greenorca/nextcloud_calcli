#!/usr/bin/env python3
# Sven Schirmer, 2016, schirmer@green-orca.com
# requires ~/.nextcloud_cal.ini with following format
# [DEFAULT]
# user = guggus
# pwd = guggus
# url = https://odroid/remote.php/dav/calendars/guggus/default/
# ssl = True | False (in case your certficate cannot be verified)
# urgent_words=BirhtDay, meeting #case insesitive
# urgent_cals=Contact birthdays
# urgent_color=db6823
# summary_length=20
# lines_to_display=10
# time_delta=20

from datetime import datetime, date, timedelta
import caldav
import os
import sys
import configparser
import re

summertime = 1  # 0 for winter, 1 for summer in Europe

# parse event data into dictionary


def parseInfo(data, name):
    events = re.split(
        "END:VEVENT\nBEGIN:VEVENT\n|END:VEVENT\nEND:VCALENDAR\n\n", data)
    for event in events:
        pieces = event.split('\n')
        keys = []
        values = []
        tStart = 0
        for piece in pieces:
            kv = piece.split(':')
            if kv[0] == 'SUMMARY' and kv[1] != "Alarm notification":
                keys.append(kv[0])
                values.append(kv[1])
            else:
                if kv[0].split(';')[0] == 'DTSTART':
                    keys.append('DSTART')
                    values.append(parseDate(kv[1]))
                    tStart = values[-1]
                else:
                    # look for multi_day events
                    if tStart != 0 and kv[0].split(';')[0] == 'DTEND':
                        tEnd = parseDate(kv[1])
                        if (tEnd-tStart).days > 1:
                            keys.append('DEND')
                            values.append(tEnd)
        keys.append('CAL')
        values.append(name)
        return dict(list(zip(keys, values)))


def parseDate(dateString):
    pieces = dateString.split('T')
    if len(pieces) == 1:
        return datetime.strptime(dateString, "%Y%m%d") + timedelta(hours=1 + summertime)
    else:
        return datetime.strptime(dateString, "%Y%m%dT%H%M%SZ") + timedelta(hours=1 + summertime)


def getKey(item):
    return item["DSTART"]


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/')+'.nextcloud_cal.ini')
    # create client
    client = caldav.DAVClient(config['DEFAULT']['url'],
                              proxy=None, username=config['DEFAULT']['user'],
                              password=config['DEFAULT']['pwd'], auth=None,
                              ssl_verify_cert=bool(config['DEFAULT']['ssl'] == 'True'))

    # create connection
    principal = client.principal()
    calendars = principal.calendars()
    event_data = []
    # cycle through all calendars
    for calendar in calendars:
        props = calendar.get_properties([caldav.elements.dav.DisplayName(),])
        name = props[caldav.elements.dav.DisplayName().tag]
        results = calendar.date_search(date.today(), date.today()
                                       + timedelta(days=int(config['DEFAULT']['time_delta'])))
        for ev in results:
            event_data.append(parseInfo(ev.data, name))
    # sort by datetime
    event_data = sorted(event_data, key=getKey)

    # parsing keywords for later colourization
    words = config['DEFAULT']['urgent_words'].split(', ')
    urgent_cals = config['DEFAULT']['urgent_cals'].split(', ')

    currentDate = date.today()-timedelta(days=1)
    i = 0

    # output
    for event in event_data:
        if i >= int(config['DEFAULT']['lines_to_display']):
            break
        datestr = event['DSTART'].date().strftime('%a %d.%m')
        # avoid duplicate date output
        if event['DSTART'].date() == currentDate:
            datestr = "         "
        else:
            currentDate = event['DSTART'].date()
        # replace todays date with "Today"
        if event['DSTART'].date() == date.today():
            datestr = "Today    "
        timestr = str(event['DSTART'].time())[0:5]
        # all-day events
        if timestr == '00:00':
            timestr = '-all-'
        # actual output generation with colors depending on keywords
        if (any(word.lower() in event['SUMMARY'].lower() for word in words)
                or any(urgent_cal in event['CAL'] for urgent_cal in urgent_cals)):
            sys.stdout.write(datestr + '  ' + timestr + '  ' + '${color '
                             + config['DEFAULT']['urgent_color'] + '}'
                             + event['SUMMARY'][:int(config['DEFAULT']['summary_length'])]
                             + '${color}' + os.linesep)
        else:
            sys.stdout.write(datestr + '  ' + timestr + '  '
                             + event['SUMMARY'][:int(config['DEFAULT']['summary_length'])]
                             + os.linesep)

        if 'DEND' in event.keys():
            sys.stdout.write("ends on "+str(event['DEND'].date())+os.linesep)
        i = i + 1
