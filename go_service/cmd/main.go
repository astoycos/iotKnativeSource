package main

import (
	"context"
	"fmt"
	"log"

  cloudevents "github.com/cloudevents/sdk-go"
  

  "os"
)

/*
Example Output:
☁  cloudevents.Event:
Validation: valid
Context Attributes,
  SpecVersion: 0.2
  Type: dev.knative.eventing.samples.heartbeat
  Source: https://knative.dev/eventing-contrib/cmd/heartbeats/#local/demo
  ID: 3d2b5a1f-10ca-437b-a374-9c49e43c02fb
  Time: 2019-03-14T21:21:29.366002Z
  ContentType: application/json
  Extensions:
    the: 42
    beats: true
    heart: yes
Transport Context,
  URI: /
  Host: localhost:8080
  Method: POST
Data,
  {
    "id":162,
    "label":""
  }
*/

func display(event cloudevents.Event) {

  fmt.Println("☁️  cloudevents.Event\n%s", event.Source())
  
  out, err := os.Create("index.m3u8")
    if err != nil {
        log.Fatalln(err)
	}
	
	_, err = out.WriteString(string(event.Data.([]uint8)))
    if err != nil {
        log.Fatalln(err)
    }
  log.Println("Wrote file to index.m3u8")
  
}

func main() {
	c, err := cloudevents.NewDefaultClient()
	if err != nil {
		log.Fatal("Failed to create client, ", err)
  }
  if err := c.StartReceiver(context.Background(), display); err != nil {
		log.Fatal(err)
	}

}

