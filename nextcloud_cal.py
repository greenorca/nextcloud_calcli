#!/usr/bin/env python3
# Sven Schirmer, 2016, schirmer@green-orca.com
# requires ~/.nextcloud_cal.ini with following format
#[DEFAULT]
#user = guggus
#pwd = guggus
#url = https://odroid/remote.php/dav/calendars/guggus/default/


from datetime import datetime, date, timedelta
import caldav, os, sys
import configparser

#parse event data into dictionary
def parseInfo(data):
    pieces = data.split('\r\n')
    keys=[]
    values=[]
    tStart=0
    for piece in pieces:
        kv=piece.split(':')
        if kv[0]=='SUMMARY' and kv[1]!="Alarm notification":
            keys.append(kv[0])
            values.append(kv[1])
        else:
            if kv[0].split(';')[0]=='DTSTART':
                keys.append('DSTART')
                values.append(parseDate(kv[1]))
                tStart=values[-1]
            else:
                # look for multi_day events
                if tStart!=0 and kv[0].split(';')[0]=='DTEND':
                    tEnd = parseDate(kv[1])
                    if (tEnd-tStart).days > 1:
                        keys.append('DEND')
                        values.append(tEnd)

    return dict(list(zip(keys,values)))

def parseDate(dateString):
    pieces = dateString.split('T')
    if len(pieces)==1:
        return datetime.strptime(dateString,"%Y%m%d")
    else:
        return datetime.strptime(dateString,"%Y%m%dT%H%M%SZ")

def getKey(item):
     return item["DSTART"]

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/home/sven/.nextcloud_cal.ini')
        
 
    client=caldav.DAVClient(config['DEFAULT']['url'],
                            proxy=None,username=config['DEFAULT']['user'],
                            password=config['DEFAULT']['pwd'],auth=None,ssl_verify_cert=False)
    principal = client.principal()
    
    calendars = principal.calendars()
    event_data=[]
    #cycle through all calendars
    for calendar in calendars:    
        results = calendar.date_search(date.today(), date.today()+timedelta(days=17))
        for ev in results:
            event_data.append(parseInfo(ev.data))
    # sort by datetime
    event_data = sorted(event_data, key=getKey) 
    
    currentDate = date.today()-timedelta(days=1)
    i=0
    #output
    for x in event_data: 
        if i > 6:
            break;
        datestr = x['DSTART'].date().strftime('%a %d.%m.')
        if x['DSTART'].date()==currentDate:
            datestr="          "
        else:
            currentDate = x['DSTART'].date()               
            
        timestr = str(x['DSTART'].time())[0:5]
        if timestr=='00:00':
            timestr = '-all-'
        sys.stdout.write(datestr+' '+timestr+'\t'+x['SUMMARY'][0:15]+os.linesep)
        if 'DEND' in x.keys():
            sys.stdout.write("ends on "+str(x['DEND'].date())+os.linesep)
        i=i+1