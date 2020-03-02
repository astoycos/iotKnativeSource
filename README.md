# iotKnativeSource

This repository houses a knative service that will accept data from IOT devices and run realtime processing on the data, an Example is shown below 
![image0](https://raw.githubusercontent.com/astoycos/iotKnativeSource/master/docs/Article.jpg)

## Components/Prequisites 

## Kubernetes 

### OpenShift
  This demo assumes you have a functional Openshift Cluster 
  
## Enmasse

[Enmasse](enmasse.io) is a scalable cloud hosted messaging architecture which in this example is used to connect the [iotDeviceSimulator](https://github.com/astoycos/iotDeviceSimulator) to a kubernetes cluser, or in this case an OpenShift Cluster. 

### Enmasse Setup 
For this Demo, Enmasse requires some specific configurations for the iot protocol adapters, specifically `HONO_HTTP_MAX_PAYLOAD_SIZE` must be raised from its default value of 2048 bits. See the following [Issue](https://github.com/EnMasseProject/enmasse/issues/4032) for updates on a possible change with this

1. To configure the hono device adapter, first [Download Enmasse v0.30.1](https://github.com/EnMasseProject/enmasse/releases/tag/0.30.1) Note: The most current version v0.30.2 had some issues with the iot services initially I will update once I verify they are working correctly. 

2. Edit enmasse-0.30.1/install/bundles/enmasse/050-Deployment-enmasse-operator.yaml Line 65 to the following 
* `value: quay.io/astoycos/iot-http-adapter:0.30.2` To pull my custom http Adapter Image from my quay.io repo

3. Follow the standard instructions to [setup enmasse IoT on OpenShift](https://enmasse.io/documentation/0.30.2/openshift/#'iot-guide-messaging-iot)

4. Apply the Version Permissions Fix `oc apply -f permfix.yam` note:This was another issue with enmasse v0.30.1 on Openshift


## Knative 

[Knative](https://knative.dev/) is a great serverless framework that dedicates cloud resources only when they are needed. 

### Knative Setup 

  1. Download and install [Knative Serving](https://knative.dev/docs/serving/) 
  
  2. Download and install [Knative Eventing and Sources](https://knative.dev/docs/eventing/) 
  
The overall system Architecture is described by the following diagram 

![image2](https://raw.githubusercontent.com/astoycos/iotKnativeSource/master/docs/iotKnativeSource.png)

## The Service

The iotKnativeSource service implements two major blocks 

   1. listener 
      - contains a cloudEvents listener that accepts incoming CE messages from the IOT containerSource

   2. APP
      - [Tensorflow object detection API](https://github.com/tensorflow/models/tree/master/research/object_detection) module         that does realtime image analysis on an incoming IOT video stream 
      - Basic Flask application that streams the analyzed video for viewing outside of the cloud hosted container 

 ## How to run 
 
 1. Either Download and build the [iotContainerSource repo](https://github.com/astoycos/iotContainerSource) or simply use the prebuilt image at quay.io/astoycos/iotcontainersource with the following demo yamls
 
 

