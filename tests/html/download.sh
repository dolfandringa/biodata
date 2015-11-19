#!/bin/bash
filename=$(echo $1|sed -e "s/index\.html//g" -e "s/\.html//g")
wget -O $1 http://localhost:8080/$filename
