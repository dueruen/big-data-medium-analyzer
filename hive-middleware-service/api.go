package main

import (
	"context"
	"fmt"
	"log"
	"net/http"

	gohive "github.com/beltran/gohive"
)

var zookeeperEndpoint string = "10.123.252.213:2181,10.123.252.211:2181,10.123.252.212:2181" //insert Zookeeper endpoint

func getHistoricalDataFromHive(w http.ResponseWriter, r *http.Request) {
	cursor, connection, err := connectToHive()
	defer cursor.Close()
	defer connection.Close()

	if err != nil {
		fmt.Printf("Error connecting to Hive: %v \n Shutting down...", err)
		cursor.Close()
		connection.Close()
		panic(err)
	}
	//TODO
	//What data to fetch?

	ctx := context.Background()

	cursor.Exec(ctx, "INSERT SQL QUERY") //Look into using prepared statements, if we wish to use params
	if cursor.Err != nil {
		log.Fatal(cursor.Err)
		cursor.Close()
		connection.Close()
		return
	}

}

func handleRequests() {
	http.HandleFunc("/", getHistoricalDataFromHive)
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func connectToHive() (*gohive.Cursor, *gohive.Connection, error) {

	configuration := gohive.NewConnectConfiguration()
	//Look into necessary configs for Zookeeper connection
	//configuration.Username = "APP"
	//configuration.Password = "mine"
	configuration.ZookeeperNamespace = "hiveserver"
	configuration.Service = "hive"
	configuration.TransportMode = "http"

	connection, errConn := gohive.ConnectZookeeper(zookeeperEndpoint, "NONE", configuration)

	if errConn != nil {
		return nil, nil, errConn
	}

	cursor := connection.Cursor()
	return cursor, connection, nil
}

func main() {
	handleRequests()
}
