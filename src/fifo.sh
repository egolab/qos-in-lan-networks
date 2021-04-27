#!/bin/bash

tc qdisc del dev h0-eth0 root
tc qdisc add dev h0-eth0 root handle 1: netem rate 125kbps
tc qdisc add dev h0-eth0 parent 1: pfifo limit 30
