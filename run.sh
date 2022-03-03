#!/bin/bash
cd /home/ubuntu/ASoul-Comment

pgrep python
if [$?!=""];then
  nohup /usr/bin/python3 -m uvicorn server:server &
  sleep 100;exit
fi