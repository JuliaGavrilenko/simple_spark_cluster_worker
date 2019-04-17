#!/bin/bash
## PRE_CONFIG EVENT ##
docker build -t simple_spark_cluster_worker_sh_pre_config ./sh/pre_config/
docker run -it -e "EXECUTION_ID=0" -v $(pwd)/:/component_repository simple_spark_cluster_worker_sh_pre_config bash
docker stop simple_spark_hadoop_worker && docker rm simple_spark_hadoop_worker
### BOOT EVENT ###
#build image
sudo docker build -t simple_spark_hadoop_worker sh/
sudo docker run -itd \
    --name simple_spark_hadoop_worker \
    --privileged \
    -p "8042:8042" \
    -v $(pwd)/sh/config:/etc/simple_grid/config \
    -v $(pwd)/augmented_site_level_config_file.yaml:/etc/simple_grid/augmented_site_level_config_file.yaml \
    --net spark_tests \
    --ip 10.1.1.11 \
    --hostname spark-hadoop-worker-localhost01-1.cern.ch \
    --add-host "spark-master.cern.ch:10.1.1.10" \
    simple_spark_hadoop_worker \
#### PRE INIT HOOKS #####


### INIT EVENT ######
sudo docker exec -t simple_spark_hadoop_worker /etc/simple_grid/config/init.sh
sudo docker exec -it simple_spark_hadoop_worker bash
#### POST INIT HOOKS ######