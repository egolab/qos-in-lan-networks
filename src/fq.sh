#!/bin/bash

tc qdisc del dev s0-eth1 root

tc qdisc add dev s0-eth1 root handle 1: tbf rate 250kbps burst 1600 latency 100000
tc qdisc add dev s0-eth1 parent 1:1 handle 10: fq maxrate 250kbps limit 30
