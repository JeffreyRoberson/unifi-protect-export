import os, psycopg2

import unicodedata
import re
from datetime import datetime
import time

# apt install python-psycopg2
#  psql -U postgres -d unifi-protect -p 5433

# MAC Address of camera to export videos from
cam = "FCECDA308AC3"

# Output root folder, needs tailing "/"
# Can be a CIFS mount on an external server
outroot = "/mnt/video/"


#
#
def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return str(re.sub(r'[-\s]+', '-', value).strip('-_'))

def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset

# Connect to the local database
conn = psycopg2.connect(database = "unifi-protect", user = "postgres", host = "127.0.0.1", port = "5433")

cur = conn.cursor()

# Determine camera internal id
cur.execute("SELECT mac, id, name FROM cameras WHERE mac='" + cam + "'")
rows = cur.fetchall()
for row in rows:
    camid =  row[1]
    name = row[2]

# Make valid filename prefix
camname = slugify(name)

# Find detections and recordings for that camera
vidfile = ''
cur.execute("SELECT \"eventStart\", \"eventEnd\", start, file, folder, detections.\"createdAt\"  FROM detections, \"recordingFiles\" AS rf WHERE detections.\"recordingFileId\" = rf.id AND rf.\"cameraId\" = '" + camid + "' ORDER BY folder, file")
rows = cur.fetchall()
for row in rows:
    eventStart = int(row[0])
    eventEnd = int(row[1])
    vidstart = int(row[2])
    file = row[3]
    folder = row[4]
    # 2022-11-14 23:42:38
    event = datetime.strptime(str.split(str(row[5]), ".")[0], "%Y-%m-%d %H:%M:%S")

    # New input file? 
    if vidfile != file:
        # Export it as mpeg4
        print ("Export: " + folder + "/" + file + "\n")
        if os.path.exists("export.mp4"):
           os.remove("export.mp4")
        os.system('/usr/share/unifi-protect/app/node_modules/.bin/ubnt_ubvexport -s ' + folder + "/" + file + ' -d ubvexport')
        vidfile = file

    startsec = str((eventStart - vidstart) / 1000)
    duration = str((eventEnd - eventStart) / 1000)
    # Convert event date and time to local time from UTC
    localtime = utc2local(event)

    # Check to see if this is in our needed time range
    if localtime.hour > 6 and localtime.hour < 19:
        # Build output folders as needed
        newpath = outroot + str(localtime.year) + '/' + str(localtime.month) + '/' + str(localtime.day)
        if not os.path.exists(newpath):
            print('mkdir ', newpath)
            os.makedirs(newpath)
    
        outfile = camname + "_" + str(localtime.hour) + "-" + str(localtime.minute) + "-" + str(localtime.second) + ".mp4"
        print ("ffmpeg -ss " + startsec + " -i ubvexport_0.mp4 -c copy -t " + duration + " " + newpath + "/" + outfile)
        os.system("ffmpeg -ss " + startsec + " -i ubvexport_0.mp4 -c copy -t " + duration + " " + newpath + "/" + outfile)

conn.close()

