# iotKnativeSource

This repository houses a knative service that will accept data from IOT devices and run realtime processing on the data. 

## Components 

### Knative 

Knative is a great serverless framework that dedicates cloud resources only when they are needed

### The Application 

This Application specifically implements two major blocks 

1. listener 
  - contains a cloudEvents listener that accepts incoming CE messages from the IOT containerSource
  
2. APP
  - Tensorflow module that does realtime image analysis on an incoming IOT video stream 
  - Basic Flask application that streams the analyzed video for viewing outside of the cloud hosted container 
  
 

