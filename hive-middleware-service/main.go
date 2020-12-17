package main

import (
	"context"
	"fmt"
	"log"

	gohive "github.com/beltran/gohive"
)

var hiveEndpoint string = "10.123.252.213" //insert Zookeeper endpoint

func connectToHive() {
	ctx := context.Background()
	configuration := gohive.NewConnectConfiguration()
	//Look into necessary configs for Zookeeper connection
	configuration.FetchSize = 1000
	configuration.Username = ""
	configuration.Password = ""
	fmt.Println("One")
	connection, errConn := gohive.Connect(hiveEndpoint, 10000, "NONE", configuration)

	fmt.Println("Two")
	if errConn != nil {
		fmt.Println(errConn)
	}

	fmt.Println("Three")
	cursor := connection.Cursor()

	fmt.Println("Four")
	cursor.Exec(ctx, "SELECT * FROM test2;")
	if cursor.Err != nil {
		log.Fatal(cursor.Err)
	}

	fmt.Println("Five")

	fmt.Println(cursor)

	var s string
	for cursor.HasMore(ctx) {
		if cursor.Err != nil {
			fmt.Println("Err")
			log.Fatal(cursor.Err)
		}
		cursor.FetchOne(ctx, &s)
		if cursor.Err != nil {
			fmt.Println("Err")
			log.Fatal(cursor.Err)
		}
		fmt.Println(s)
	}
	fmt.Println("Done")
}

func main() {
	connectToHive()
}
