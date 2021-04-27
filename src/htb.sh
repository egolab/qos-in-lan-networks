#!/bin/bash

tc qdisc del dev s0-eth1 root

tc qdisc add dev s0-eth1 root handle 1: htb default 11
tc class add dev s0-eth1 parent 1: classid 1:1 htb rate 250kbps ceil 250kbps
tc class add dev s0-eth1 parent 1:1 classid 1:10 htb rate 200kbps ceil 250kbps
tc class add dev s0-eth1 parent 1:1 classid 1:11 htb rate 50kbps ceil 250kbps

tc filter add dev s0-eth1 protocol ip parent 1:0 prio 1 u32 match ip tos 0x10 0xff flowid 1:10
tc filter add dev s0-eth1 protocol ip parent 1:0 prio 1 u32 match ip tos 0x20 0xff flowid 1:11

tc qdisc add dev s0-eth1 parent 1:10 handle 20: sfq perturb 10
tc qdisc add dev s0-eth1 parent 1:11 handle 30: sfq perturb 10
