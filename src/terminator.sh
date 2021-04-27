#!/bin/bash
echo $1
cat results/h$1.out | awk -F',' '{print $7"," $8","$9","$10","$11","$12","$13}' | sed --expression '1s/^/time,transfer,bandwidth,jitter,lost,total,loss_rate\n/' > results/h$1-$2.csv