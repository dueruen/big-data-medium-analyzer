# High Availability and Load Balancing For Hiveserver2
**Pre-requisite**: 
- Java and Hadoop must be installed on the server. 
- A MySQL database running on a remote server.

# Install Hive

## 1. Download hive 3.1.2
```bash
$ wget https://downloads.apache.org/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz
```
## 2. Untar Hive
```bash
$ tar xzf apache-hive-3.1.2-bin.tar.gz
```

## 3. Rename the unzipped package
```bash
$ mv apache-hive-3.1.2-bin hive
```

## 4. Configure hive env variables
```bash
$ sudo nano ~/.bashrc
```
Add the following to `./bashrc` 
```
export HIVE_HOME=/home/hadoop/hadoop/hive
export PATH=${PATH}:${HIVE_HOME}/bin:${HIVE_HOME}/sbin
```
Save and exit the file. Apply the env to the current env with the command

```
$ source ~/.bashrc
```

## 5. Edit hive-config.sh
To be able to interact with hadoop we need to add the hadoop path to the end of `hive-config.sh` 
```
# Hadoop path
export HADOOP_HOME=/home/hadoop/hadoop
```

## 6. Create hive directories in HDFS
We need to create the following 2 seperate directories(tmp and warehouse directory) to store data in the HDFS.

**Create tmp directory** - This is going to store intermediary data hive sends to HDFS
```
$ hdfs dfs -mkdir /tmp
```

Add write and exec permissions to tmp group members
```
$ hdfs dfs -chmod 777 /tmp
```

To verify the permissions were added and check the read write permissions
```
$ hdfs dfs -ls /
```
**Create warehouse directory**
Create the warehouse dir in /user/hive/ parent dir.
```
$ hdfs dfs -mkdir -p /user/hive/warehouse
```
Add write and execute permissions to warehouse group member
```
$ hdfs dfs -chmod g+w /user/hive/warehouse
```

To verify the permissions were added and check the read write permissions
```
$ hdfs dfs -ls /user/hive
```

## 7. Configure hive-site.xml
To locate the right file
```
$ cd $HIVE_HOME/conf
```

We choose to just create a completely new file instead of using the hive-site.xml.template
```
$ touch hive-site.xml
```
Now we edit the hive-site.xml file
```
$ nano hive-site.xml
```
Insert the following into the master node `hive-site.xml`, where the mysql server is running:
```
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:mysql://localhost/metastore_db?createDatabaseIfNotExist=true&amp;useSSL=false</value>
        <description>JDBC connect string for a JDBC metastore.</description>
    </property>
    <property>
	<name>javax.jdo.option.ConnectionUserName</name>
	<value>hiveuser</value>
    </property>
    <property>
	<name>javax.jdo.option.ConnectionPassword</name>
	<value>hivepassword</value>
    </property>
    <property>
        <name>hive.metastore.client.socket.timeout</name>
        <value>300</value>
    </property>
    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
        <description>location of default database for the warehouse</description>
    </property>
    <property>
        <name>hive.metastore.uris</name>
        <value>thrift://node-master:9083,thrift://node1:9083,thrift://node2:9083</value>
        <description>Thrift URI for the remote metastore.</description>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>com.mysql.jdbc.Driver</value>
        <description>MYSQL Driver class name for a JDBC metastore</description>
    </property>
    <property>
        <name>javax.jdo.PersistenceManagerFactoryClass</name>
        <value>org.datanucleus.api.jdo.JDOPersistenceManagerFactory</value>
        <description>class implementing the jdo persistence</description>
    </property>
    <property>
        <name>hive.server2.enable.doAs</name>
        <value>false</value>
    </property>
    <property>
        <name>hive.server2.authentication</name>
        <value>NONE</value>
    </property>
    <property>
	    <name>hive.exec.local.scratchdir</name>
	    <value>/tmp/${user.name}</value>
	    <description>Local scratch space for Hive jobs</description>
    </property>
    <property>
	    <name>hive.downloaded.resources.dir</name>
	    <value>/tmp/${user.name}_resources</value>
	    <description>Temporary local directory for added resources in the remote file system.</description>
    </property>
    <property>
	    <name>hive.support.concurrency</name>
	    <value>true</value>
    </property>
    <property>
	    <name>hive.zookeeper.quorum</name>
	    <value>node-master,node1,node2</value>
    </property>
    <property>
	    <name>hive.zookeeper.client.port</name>
	    <value>2181</value>
    </property>
    <property>
	    <name>hive.server2.support.dynamic.service.discovery</name>
	    <value>true</value>
    </property>
    <property>
	    <name>hive.server2.zookeeper.namespace</name>
	    <value>hiveserver2</value>
    </property>
    <property>
        <name>hive.server2.thrift.port</name>
        <value>10000</value>
    </property>
    <property>
        <name>hive.server2.webui.port</name>
        <value>10002</value>
    </property>
    <property>
        <name>hive.metastore.event.db.notification.api.auth</name>
        <value>false</value>
        <description>
       Should metastore do authorization against database notification related APIs such as get_next_notification.
       If set to true, then only the superusers in proxy settings have the permission
        </description>
    </property>
</configuration>
```
On the slave nodes you'll have to change the `javax.jdo.option.ConnectionURL` to the external RDBMS URI which is:
```
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:mysql://node-master/metastore_db?createDatabaseIfNotExist=true&amp;useSSL=false</value>
        <description>JDBC connect string for a JDBC metastore.</description>
    </property>
```
And the username and password to:
```
    <property>
	    <name>javax.jdo.option.ConnectionUserName</name>
	    <value>remotehiveuser</value>
    </property>
    <property>
	    <name>javax.jdo.option.ConnectionPassword</name>
	    <value>remotehivepassword</value>
    </property>
```


### 8. Install mysql connector
Install the mysql connector package
```
$ sudo apt-get install libmysql-java
```
Link the jar file and hive/lib and copy jar to the lib folder
```
sudo ln -s /usr/share/java/mysql-connector-java.jar $HIVE_HOME/lib/mysql-connector-java.jar
```
### 9. Fix guava incompability error in Hive
First you need to remove the outdated version
```
rm $HIVE_HOME/lib/guava-19.0.jar
```
Then you need to copy the guava version from hadoop lib dir to Hive lib dir
```
$ cp $HADOOP_HOME/share/hadoop/hdfs/lib/guava-27.0-jre.jar $HIVE_HOME/lib/
```

### 10. Fix multiple bindings
You need to remove the `log4j-slf4j-impl-2.10.0.jar`file
```
$ rm $HIVE_HOME/lib/log4j-slf4j-impl-2.10.0.jar
``` 


# Run the Hive multiple cluster setup with loadbalancing 
### Step 1 - Hive metastore server
Start the hive metastore server on all three nodes(node-master,node1,node2)
```bash
$ hive --service metastore
```
### Step 2 - Hiveserver2 start
Start the hiveserver2 with logging directly to console and thrift on port 10000 on all three nodes(node-master,node1,node2)
```bash
$ hive --service hiveserver2 --hiveconf hive.server2.thrift.port=10000 --hiveconf hive.root.logger=INFO,console
```

### Step 3 - Connect to Hiveserver2 with beeline
You're now ready to connect to the Hiveserver2. 
```bash
$ beeline -u "jdbc:hive2://node-master:2181,node1:2181,node2:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2"
```

You can know perform the hive queries.

## Test the high availability and loadbalancing
To test the high availability you'll have to do the following.

1. Start with stopping the hiveserver2 on node-master(or one of your nodes)
Now try to connect to hiveserver2 with the same command 
```bash
$ beeline -u "jdbc:hive2://node-master:2181,node1:2181,node2:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2"
```
Any errors? No, because zookeeper forwarded a connection to node1´s hiveserver2. Thank god.

2. Now stop the hiveserver2 on node1 and try to connect to hiveserver2 with the same command as before. 
```bash
$ beeline -u "jdbc:hive2://node-master:2181,node1:2181,node2:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2"
```
Still no errors? Wonderful! Zookeeper got you're back.

3. Last but not least stop the hiveserver2 on node2(or the last hiveserver2 you got running) and try to connect to hiveserver2 with the same command as before. 
```bash
$ beeline -u "jdbc:hive2://node-master:2181,node1:2181,node2:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2"
```
**Error!** now you're connection through beeline to the hiveserver2 would fail because all youre hiveserver2 instances are not running.

But this proves that it works!


### 
To show databases in the metastore server.
```bash
$ > SHOW DATABASES;
```


### Connect to hive metastore - Embedded mode
Write the following in beeline CLI
```bash
$ !connect jdbc:hive2://
```

## Things to remember
Hive url
`http://localhost:9870/explorer.html#/user/hive/warehouse`

### Create articles table in hive
Header line is skipped in the following query
```sql
CREATE TABLE articles ( id int, url String, title String, subtitle String, image String, claps int, responses int, reading_time int, publication int, date_str String, image_pixel_height int, image_pixel_width int, image_size int, image_average_pixel_color_r int, image_average_pixel_color_g int, image_average_pixel_color_b int, title_len int, title_words int, title_type_words int, title_key_words int, subtitle_len int, subtitle_words int, subtitle_type_words int, subtitle_key_words int)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
tblproperties("skip.header.line.count"="1")
;
```

### List port use
`netstat -tulpn | grep LISTEN`

### Load data from hdfs into hive table
```
beeline $ > load data inpath 'pre_data.csv' into table articles;
```
### Running java apps
show running java apps `jps`
### Kill hiveserver2 if its running as daemon
kill java tasks `pkill -9 -f RunJar`

## References
- http://www.hadooplessons.info/2017/12/dynami-service-discovery-in-hive-using-zookeeper.html
- https://cwiki.apache.org/confluence/display/Hive/AdminManual+Metastore+3.0+Administration#AdminManualMetastore3.0Administration-Option2:ExternalRDBMS
- https://cwiki.apache.org/confluence/display/Hive/HiveServer2+Clients#HiveServer2Clients-ConnectionURLWhenZooKeeperServiceDiscoveryIsEnabled
- https://cwiki.apache.org/confluence/display/Hive/GettingStarted#GettingStarted-SimpleExampleUseCases
- https://acadgild.com/blog/connect-hive-with-beeline-hive-installation-with-mysql-metastore
- https://www.geeksforgeeks.org/apache-hive-installation-and-configuring-mysql-metastore-for-hive/
- https://www.bbsmax.com/A/qVdeeMOpdP/
- https://kontext.tech/column/hadoop/303/hiveserver2-cannot-connect-to-hive-metastore-resolutionsworkarounds
- https://sparkbyexamples.com/apache-hive/hive-start-hiveserver2-and-beeline/
- https://github.com/PacktPublishing/Hadoop-2.x-Administration-Cookbook/blob/master/Chapter07/ch7_recipes.txt
- https://subscription.packtpub.com/book/big_data_and_business_intelligence/9781787126732/7/ch07lvl1sec80/operating-hive-with-zookeeper
- https://blog.pythian.com/setup-high-availability-load-balancing-hiveserver2/
- https://dzone.com/articles/how-configure-mysql-metastore 
- https://medium.com/@divingwai/installing-hive-with-external-mysql-58a958ff1692
- https://phoenixnap.com/kb/install-hive-on-ubuntu