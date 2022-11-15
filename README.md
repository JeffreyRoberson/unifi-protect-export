# unifi-protect-export
Export Unifi Protect detections as individual MP4 files

I needed the ability to export all detections within a specific hour range from a video camera system.  This will connect to the Unifi Protect Postgresql database, looking for detections on a specific camera.  If the detection falls within a given time frame, it will then convert the detection time from UTC to local time.  From there it will create a folder structure, year/month/day as needed.  It will then export the UBV file to MP4, and export the detection to an MP4 naming the file based on the given camera name, local hour, minute and second.  

It is not well refined code, but this was built for a specific purpose.  Hopefully it will help someone else.

This was intended to run on the local Protect UNVR.  Some Debian pakcages will need to be installed to make this work.  FFMPEG is used to export the video.

The output was sent to a CIFS mount point for archiving.  
To create a CIFS mountpoint follow these steps
sudo apt install smbclient
sudo mkdir /mnt/video
sudo mount.cifs -o sec=ntlmssp,username=USERNAME //PC_NAME/SHARE /mnt/video

Minor adjustments need to be made to the file.  The MAC address of the camera to export is on line 12 of the file.  The MAC address is without colon's. (:)
This script will only look at specific hours, listed on line 85.  This time range, or date rnage can be adjusted with that if statement.

Good luck, hopefully this helps someone else too.
