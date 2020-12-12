pip3 install opencv-python is not working use: sudo apt install python3-opencv ,to install cv2
if using python2: pip install opencv-python==4.2.0.32

export PYSPARK_PYTHON=python3

pip3 install scikit-image && pip install scikit-image
pip3 install numpy

sudo apt-get install python-matplotlib python-numpy python-pil python-scipy && sudo apt-get install build-essential cython && sudo apt-get install python-skimage

# Start spark program
```bash
$ /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py

% or with more files
$ /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/big-data-medium-analyzer/processing/pipelines.py /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py
```