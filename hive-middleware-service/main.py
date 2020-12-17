from pyhive import hive 
import re, os, time 

host_name="localhost"
port = 10000
user = "APP"
password = "mine"
database = "default"

def hiveConnection(host_name, port, user, password, database):
    conn = hive.Connection(host=host_name, port=port, username=user, password=password, database=database, auth="CUSTOM")
    cur = conn.cursor()

    print(conn) 


if __name__ == "__main__":
    hiveConnection(host_name, port, user, password, database)