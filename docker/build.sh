#!/bin/bash
# build image produitdervivelidar
PROJECT_NAME=lidar_hd/produits_derives_lidar
VERSION=`cat ../VERSION.md`

docker build -t $PROJECT_NAME -f Dockerfile ..
docker tag $PROJECT_NAME $PROJECT_NAME:$VERSION
