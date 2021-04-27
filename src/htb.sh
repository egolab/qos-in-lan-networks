#!/bin/bash

tc qdisc del dev h0-eth0 root

tc qdisc add dev h0-eth0 root handle 1: htb default 20

tc class add dev h0-eth0 parent 1: classid 1:1 htb rate 250kbps ceil 250kbps
tc class add dev h0-eth0 parent 1:1 classid 1:10 htb rate 200kbps prio 1 ceil 250kbps
tc class add dev h0-eth0 parent 1:1 classid 1:20 htb rate 50kbps prio 2 ceil 250kbps

tc qdisc add dev h0-eth0 parent 1:10 handle 10: sfq perturb 10
tc qdisc add dev h0-eth0 parent 1:20 handle 20: sfq perturb 10

tc filter add dev h0-eth0 protocol ip parent 1:0 prio 1 u32 match ip tos 0x10 0xff flowid 1:10
tc filter add dev h0-eth0 protocol ip parent 1:0 prio 1 u32 match ip tos 0x20 0xff flowid 1:20
