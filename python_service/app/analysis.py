from __future__ import absolute_import, division, print_function, unicode_literals

## If we just use Tensorflow 2.x we git "Config"
try:
  import tensorflow.compat.v2 as tf
except Exception:
  pass

tf.enable_v2_behavior()

print(tf.__version__)

import pathlib
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import subprocess
import time


from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import time
import cv2

##Config for Flask
frame = None
cap = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__,template_folder='templates')
# initialize the video stream and allow the camera sensor to
# warmup

@app.route("/")
def index():
	# return the rendered template
	return render_template('index.html')

# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile

def load_model(model_name):
  base_url = ' http://download.tensorflow.org/models/object_detection/'

  model_file = model_name + '.tar.gz'
  model_dir = tf.keras.utils.get_file(
    fname=model_name, 
    origin=base_url + model_file,
    untar=True)

  model_dir = pathlib.Path(model_dir)/"saved_model"
  model = tf.compat.v2.saved_model.load(str(model_dir),None)
  model = model.signatures['serving_default']

  return model

def run_inference_for_single_image(model, image):
  
  image = np.asarray(image)

  # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
  input_tensor = tf.convert_to_tensor(image)
  # The model expects a batch of images, so add an axis with `tf.newaxis`.
  input_tensor = input_tensor[tf.newaxis,...]

  # Run inference
  output_dict = model(input_tensor)
  

  # All outputs are batches tensors.
  # Convert to numpy arrays, and take index [0] to remove the batch dimension.
  # We're only interested in the first num_detections.
  num_detections = int(output_dict.pop('num_detections'))
  output_dict = {key:value[0, :num_detections].numpy() 
                 for key,value in output_dict.items()}
  output_dict['num_detections'] = num_detections


  # detection_classes should be ints.
  output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
   
  # Handle models with masks:
  if 'detection_masks' in output_dict:
    # Reframe the the bbox mask to the image size.
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
              output_dict['detection_masks'], output_dict['detection_boxes'],
               image.shape[0], image.shape[1])      
    detection_masks_reframed = tf.cast(detection_masks_reframed > 0.3,
                                       tf.uint8)
    output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
    
  return output_dict

def show_inference(model, image_path):
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = np.array(image_path)
    # Actual detection.
    output_dict = run_inference_for_single_image(model, image_np)
    # Visualization of the results of a detection.
    #print(output_dict['detection_classes'])
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=2)

    #Image.fromarray(image_np).imshow()
    #cv2.imshow('frame',image_np)
    # Display the resulting frame
    return(image_np)
 
#Function to read in frames and do analysis 
def generate():
  global cap, frame, lock
  count = 0 
  while(cap.isOpened()): 
    # Capture frames 
    count+=1 
    ret, frame = cap.read()
    if count == 10:
      count = 0 
      if ret == True:    
        out_frame = show_inference(detection_model, frame)
        
        with lock: 
          frame = out_frame.copy() 

        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
  video_digest.kill()

#Wrapper function to try and get Multithreading to work Not currently in use 
def servid():
  global lock, frame
  
  while True: 
    #Image.fromarray(frame).save("test.png")
    #cv2.imshow('frame2',frame)
    with lock:
      cv2.imshow('frame2',frame)
      if frame is None: 
        continue
      (flag, encodedImage) = cv2.imencode(".jpg", frame)
      if flag:
        break
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')



@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
      help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
      help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
      help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    #Load model 

    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = 'models/research/object_detection/data/mscoco_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
    model_name = "ssd_resnet50_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03"
    detection_model = load_model(model_name)
    ffmpeg_log = open('ffmpeg_log.txt', 'w')

    ## Make sure video stream is current 

    try: 
      os.remove("out.mkv")
    except:
      print("No Video file present")
    video_digest = subprocess.Popen(['ffmpeg','-protocol_whitelist','file,http,https,tcp,tls', '-i', 'app/index.m3u8','-c','copy','-bsf:a','aac_adtstoasc','out.mkv'],stdout=ffmpeg_log,stderr=ffmpeg_log)
    
    #Give a few seconds for video stream to populate
    time.sleep(10)
    cap = cv2.VideoCapture("out.mkv")
    

    # start a thread that will perform motion detection
    t = threading.Thread(target=generate)
    t.daemon = True
    t.start()

    #Currently Threading is diabled Can can only open on one browser
    app.run(host=args["ip"], port=args["port"], debug=True,
      threaded=False, use_reloader=False)
