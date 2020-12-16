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