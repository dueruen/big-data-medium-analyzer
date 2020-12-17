# Start
Start metastore
```bash
hive --service metastore
```
In another terminal open hive
```bash
hive
```

Hive url
`http://localhost:9870/explorer.html#/user/hive/warehouse`

Create table
```
CREATE TABLE IF NOT EXISTS articles ( id int, url String, title String, subtitle String, image String, claps int, responses int, reading_time int, publication int, date_str String, image_pixel_height int, image_pixel_width int, image_size int, image_average_pixel_color_r int, image_average_pixel_color_g int, image_average_pixel_color_b int, title_len int, title_words int, title_type_words int, title_key_words int, subtitle_len int, subtitle_words int, subtitle_type_words int, subtitle_key_words int)
> ROW FORMAT DELIMITED
> FIELDS TERMINATED BY '\t'
> LINES TERMINATED BY '\n'
> STORED AS TEXTFILE;
```


LINKS DER ER BRUGT
http://www.hadooplessons.info/2017/12/dynami-service-discovery-in-hive-using-zookeeper.html
https://cwiki.apache.org/confluence/display/Hive/AdminManual+Metastore+3.0+Administration#AdminManualMetastore3.0Administration-Option2:ExternalRDBMS
https://cwiki.apache.org/confluence/display/Hive/HiveServer2+Clients#HiveServer2Clients-ConnectionURLWhenZooKeeperServiceDiscoveryIsEnabled
https://cwiki.apache.org/confluence/display/Hive/GettingStarted#GettingStarted-SimpleExampleUseCases
https://acadgild.com/blog/connect-hive-with-beeline-hive-installation-with-mysql-metastore
https://www.geeksforgeeks.org/apache-hive-installation-and-configuring-mysql-metastore-for-hive/
https://www.bbsmax.com/A/qVdeeMOpdP/
https://kontext.tech/column/hadoop/303/hiveserver2-cannot-connect-to-hive-metastore-resolutionsworkarounds
https://sparkbyexamples.com/apache-hive/hive-start-hiveserver2-and-beeline/
https://github.com/PacktPublishing/Hadoop-2.x-Administration-Cookbook/blob/master/Chapter07/ch7_recipes.txt
https://subscription.packtpub.com/book/big_data_and_business_intelligence/9781787126732/7/ch07lvl1sec80/operating-hive-with-zookeeper
