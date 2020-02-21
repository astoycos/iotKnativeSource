import os
import sys
import kncloudevents
import logging
import subprocess

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def run_event(event):
    
    f = open("index.m3u8","w")
    logging.info("Creating index.m3u8 file")
    f.write(event.Data())
    logging.info("Writing to index.m3u8 file")
    f.close() 
    #try:
    #   logging.info(event.Data())
    #except Exception as e:
    #    logging.error(f"Unexpected error: {e}")
    #    raise


client = kncloudevents.CloudeventsServer()
client.start_receiver(run_event)

#subprocess.call(['ffmpeg','-protocol_whitelist','file,http,https,tcp,tls', '-i', 'index.m3u8','-c','copy','-bsf:a','aac_adtstoasc','out.mp4'])