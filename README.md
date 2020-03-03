# iotKnativeSource

This repository houses a knative service that will accept data from IOT devices and run realtime processing on the data

The overall system Architecture is described by the following diagram 

![image1](https://raw.githubusercontent.com/astoycos/iotKnativeSource/master/docs/iotKnativeSource.png)
## *Components/Prequisites*  

### OpenShift
  This demo assumes you have a functional Openshift 4.X Cluster 
  
### Enmasse Setup

[Enmasse](enmasse.io) is a scalable cloud hosted messaging architecture which in this example is used to connect the [iotDeviceSimulator](https://github.com/astoycos/iotDeviceSimulator) to a kubernetes cluser, or in this case an OpenShift Cluster. 
For this Demo, Enmasse requires some specific configurations for the iot protocol adapters, specifically `HONO_HTTP_MAX_PAYLOAD_SIZE` must be raised from its default value of 2048 bits. See the following [Issue](https://github.com/EnMasseProject/enmasse/issues/4032) for updates on a possible change with this

1. To configure the hono device adapter, first [Download Enmasse v0.30.1](https://github.com/EnMasseProject/enmasse/releases/tag/0.30.1) Note: The most current version v0.30.2 had some issues with the iot services initially I will update once I verify they are working correctly. 

2. Change the `iot-config.yaml` to configure the http protocol adapter by editing `enmasse-0.30.1/install/components/iot/examples/iot-config.yaml` 
```yaml
apiVersion: iot.enmasse.io/v1alpha1
kind: IoTConfig
metadata:
  name: default
  namespace: enmasse-infra
spec:
  adapters:
    http:
      enabled: true
      options:
        maxPayloadSize: 5000000 # 5MB
```

3. Follow the standard instructions to [setup enmasse IoT on OpenShift](https://enmasse.io/documentation/0.30.2/openshift/#'iot-guide-messaging-iot)

4. Apply the Version Permissions Fix `oc apply -f demo-setup/permfix.yam` note:This was another issue with enmasse v0.30.1 on Openshift


### Knative Setup

[Knative](https://knative.dev/) is a great serverless framework that dedicates cloud resources only when they are needed. 

  1. Download and install [Knative Serving](https://knative.dev/docs/serving/) 
  
  2. Download and install [Knative Eventing and Sources](https://knative.dev/docs/eventing/) 
  
## The Service

The iotKnativeSource service implements two major blocks 

   1. listener 
      - contains a cloudEvents listener that accepts incoming CE messages from the IOT containerSource

   2. APP
      - [Tensorflow object detection API](https://github.com/tensorflow/models/tree/master/research/object_detection) module         that does realtime image analysis on an incoming IOT video stream 
      - Basic Flask application that streams the analyzed video for viewing outside of the cloud hosted container 

 ## How to run 
 
 1. Clone this repo with `git clone https://github.com/astoycos/iotKnativeSource.git`
 
 2. Either Download and build (using the provided instructions) the [iotContainerSource repo](https://github.com/astoycos/iotContainerSource) or simply use the prebuilt image at quay.io/astoycos/iotcontainersource with the premade demo yamls in the git folder `demo-seup`
 
 3. Clone the iotDeviceSimulator repo and run the following commands to simulate an IoT camera
      * `export ENDPOINT=$(oc -n enmasse-infra get routes iot-http-adapter --template='{{ .spec.host }}')`
      * `export STREAMURL=<youtube livestream link>` 
      * `go run ./cmd`
    The resulting terminal output will resemble the following since the `iotContainerSource` has not been started 
    ```
    [astoycos@localhost iotDeviceSimulator]$ go run ./cmd
    2020/03/03 10:06:30 Got File
    2020/03/03 10:06:30 Wrote file to index.m3u8
    2020/03/03 10:06:30 Opening file index.m3u8
    2020/03/03 10:06:31 Sent file to http adapter
    2020/03/03 10:06:31 &{503 Service Unavailable 503 HTTP/1.1 1 1 map[Content-Length:[23] Content-Type:[text/plain; charset=utf-8] Retry-After:[2] Set-Cookie:[c5fd7217f7707044dc2416fe50445fe8=7ea6a34bc4958818cb24c9fc69e9c9aa; path=/; HttpOnly; Secure]] 0xc0001862c0 23 [] false false map[] 0xc000110200 0xc00044e000}
     ```

 4. Open a new terminal and make sure you are in the `knative-eventing` namespace with `oc project knative-eventing`

 5. Apply the iotKnativeService with `oc apply -f demo-setup/iotknativeservice.yaml`
 
 6. Wait for the service to be ready with `oc get pods` which should look like the following 

```
NAME                                               READY   STATUS    RESTARTS   AGE
eventing-controller-6f4bbb779b-5rmd9               1/1     Running   0          4d2h
eventing-webhook-9c697c59-7gh25                    1/1     Running   0          4d2h
imc-controller-675dd47677-dvs7n                    1/1     Running   0          4d2h
imc-dispatcher-6c9875f557-wtpkc                    1/1     Running   0          4d2h
iotcam-display-5cr26-deployment-78f8f65575-rcv8d   2/2     Running   0          68s
sources-controller-6bf9f6d958-s7cqh                1/1     Running   0          4d2h
```
 7. Use `oc get ksvc` to get external link to the service, and open link in browser(It will just be loading for now)  
 ```
 oc get ksvc
NAME             URL                                                                       LATESTCREATED          LATESTREADY            READY   REASON
iotcam-display   http://iotcam-display.knative-eventing.apps.astoycos-ocp.shiftstack.com   iotcam-display-5cr26   iotcam-display-5cr26   True    
```
 
 7. Once the service is ready and the browser is loading the URL setup the iotContainerSource environemnt variables with `. ./demo-setup/setupScript.sh`
 
 8. Apply the iotContainerSource prepopulated with the relevent environment variables `cat demo-setup/iotcontainersource.yaml.in | envsubst | oc apply -n knative-eventing -f -`
 
 9. Go back to the link shown by `oc get ksvc` to see the livestream video analysis, which should look like the following
      * NOTE: You may see a "DNS not resolved" error if so checkout [this article](https://medium.com/@astoycos/openshift-          newbie-plagued-with-this-site-cant-be-reached-aa47909f6551) to fix it. 
 
 ![image0](https://raw.githubusercontent.com/astoycos/iotKnativeSource/master/docs/Article.jpg)

**EXTRA INFO:** 

#### Serverless Scaling
  * After two minutes of inactivity with the webapp the `iotKnativeSource` will scale back down to zero 
  * To bring it back up reload the link and then reconfigure the `iotContainerSource`'s IP with 
        1. `. ./demo-setup/setupScript.sh`
        2. `cat demo-setup/iotcontainersource.yaml.in | envsubst | oc apply -n knative-eventing -f -`
  * Now the Web APP should be back up and running 

#### Changing Streams 
  * It is possibly to change the livstream camera source by resetting `STREMURL` and restarting the `iotCameraSimulator`
  * Then simply reload the web app to see the new video stream 

## How to delete 

If you run into any problems at first delete the deployments and try again 

1. Remove the `iotContainerSource` with `cat demo-setup/iotcontainersource.yaml.in | envsubst | oc delete -n knative-eventing -f -`

2. Remove the `iotKnativeService` with `oc apply -f demo-setup/iotknativeservice.yaml`
