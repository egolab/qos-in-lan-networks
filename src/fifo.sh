
#!/bin/bash

tc qdisc del dev s0-eth1 root
tc qdisc add dev s0-eth1 root handle 1: netem rate 125kbps
tc qdisc add dev s0-eth1 parent 1: pfifo limit 30

echo "fifo enabled"