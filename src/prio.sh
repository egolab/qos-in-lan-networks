#!/bin/bash

tc qdisc del dev s0-eth1 root


tc qdisc add dev s0-eth1 root handle 1: prio

tc qdisc add dev s0-eth1 parent 1:1 handle 10: tbf rate 200kbps burst 1600 latency 30000
tc qdisc add dev s0-eth1 parent 10:1 handle 100: sfq perturb 10

tc qdisc add dev s0-eth1 parent 1:2 handle 20: tbf rate 50kbps burst 1600 latency 100000
tc qdisc add dev s0-eth1 parent 20:2 handle 200: sfq perturb 10

tc qdisc add dev s0-eth1 parent 1:3 handle 30: sfq

tc filter add dev s0-eth1 protocol ip parent 1:0 prio 1 u32 match ip tos 0x10 0xff flowid 10:1
tc filter add dev s0-eth1 protocol ip parent 1:0 prio 1 u32 match ip tos 0x20 0xff flowid 20:2
