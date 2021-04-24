#!/usr/bin/python

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Controller
from mininet.node import CPULimitedHost, Host
from mininet.link import TCLink
import argparse
import os, sys, time
import os.path


class TreeTopology(Topo):
    def __init__(self, switches, hosts):
        Topo.__init__(self)

        self.addSwitch('s0') # main switch
        self.addHost('h0', ip = '10.0.0.254')
        self.addLink('s0', 'h0', bw = 1)
        index = 0

        for switch in range(switches):
            switch_name = 's{}'.format(switch + 1)
            self.addSwitch(switch_name)
            self.addLink('s0', switch_name)

            for host in range(hosts):
                host_name = 'h{}'.format(host + index + 1)
                self.addHost(host_name, ip = '10.0.0.{}'.format(host + index + 1))
                self.addLink(host_name, switch_name, bw = 10, delay = '1ms', loss = 0)

            index = index + hosts

def background(net, hosts, duration):
    iperf_start_port = 9000
    iperf_server_cmd = 'iperf -s -p {port} -i 1 &'
    iperf_client_cmd = 'iperf -c {ip} -p {port} -t {duration} &'

    h0 = net.get('h0')

    for h in range(hosts):
        h0.cmd(iperf_server_cmd.format(port = iperf_start_port + hosts + h + 1))
        host = net.get('h{}'.format(h + hosts + 1))
        host.cmd(iperf_client_cmd.format(ip = h0.IP(), port = iperf_start_port + hosts + h + 1, duration = str(duration)))

    print("Background started")

def stream(net, hosts, duration):
    warm_up = 5
    iperf_start_port = 8000
    iperf_server_cmd = 'iperf -s -p {port} -i 1 -u -y C | tee results/h{host_id}.out &'
    iperf_client_cmd = 'iperf -c {ip} -p {port} -t {duration} -u -b 200000 &'

    time.sleep(warm_up)

    h0 = net.get('h0')

    for h in range(hosts):
        h0.cmd(iperf_server_cmd.format(port = iperf_start_port + h + 1, host_id = h + 1))
        host = net.get('h{}'.format(h + 1))
        host.cmd(iperf_client_cmd.format(ip = h0.IP(), port = iperf_start_port + h + 1, duration = str(duration - warm_up)))

    print("Streaming started")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--switches', help = 'Number of Switches')
    parser.add_argument('--hosts', help = 'Number of Hosts connected to each switch')
    parser.add_argument('--duration', help = 'Streaming duration')
    args = parser.parse_args()

    switches = 2
    hosts = 1
    duration = 30

    if args.switches:
        switches = int(args.switches)

    if args.hosts:
        hosts = int(args.hosts)

    if args.duration:
        duration = int(args.duration)

    setLogLevel('info')
    topo = TreeTopology(switches = switches, hosts = hosts)
    net = Mininet(topo = topo, link = TCLink, host = CPULimitedHost)
    c = net.addController('c', controller = Controller, ip = '127.0.0.1', port = 6633)

    net.addNAT().configDefault()
    net.start()

    h0 = net.get('h0')
    h0.cmd('tcpdump -i {intf} -w jows-0.pcap &'.format(intf = h0.intf()))


    s0 = net.get('s0')
    print(s0.cmd('./src/fifo.sh'))
    


    background(net, hosts = hosts, duration = duration)
    stream(net, hosts = hosts, duration = duration)
    
    print("Processing...")
    time.sleep(duration + 5)
    
    for h in range(hosts):
        os.system('./src/terminator.sh {host_id}'.format(host_id=h+1))
    print("Closing...")

    net.stop()
    os.system('sudo mn -c')
    info('*** You\'ve successfully exited mininet\n')
