#!/usr/bin/python

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Controller
from mininet.node import CPULimitedHost, Host
from mininet.link import TCLink
import argparse
import os, sys


class TreeTopology(Topo):
    def __init__(self, switches = 2, hosts = 5):
        Topo.__init__(self)

        self.addSwitch('s0') # main switch
        self.addHost('h0', ip = '10.0.0.254')
        self.addLink('s0', 'h0')
        index = 0

        for switch in range(switches):
            switch_name = 's{}'.format(switch + 1)
            self.addSwitch(switch_name)
            self.addLink('s0', switch_name)

            for host in range(hosts):
                host_name = 'h{}'.format(host + index + 1)
                self.addHost(host_name, ip = '10.0.0.{}'.format(host + index + 1))
                self.addLink(host_name, switch_name, bw=10, delay='1ms', loss=5)

            index = index + hosts


def stream(net, server='h0', client='h1'):
    server_command = 'cvlc ./samples/audio.mp3 --sout "#standard{access=http,mux=ogg,dst=0.0.0.0:8080}" --run-time 30 vlc://quit &'
    client_command = 'cvlc http://10.0.0.254:8080 &'

    h0, h1 = net.get(server, client)

    print('Executing command on server: ')
    h0.cmd("sed -i 's/geteuid/getppid/' /usr/bin/vlc") # to run vlc as root
    h0.cmd(server_command)

    print('Executing command on client: ')
    h1.cmd("sed -i 's/geteuid/getppid/' /usr/bin/vlc")
    h1.cmd(client_command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--switches', help = 'Number of Switches')
    parser.add_argument('--hosts', help = 'Number of Hosts connected to each switch')
    args = parser.parse_args()

    s = 2
    h = 5

    if args.switches:
        s = int(args.switches)

    if args.hosts:
        h = int(args.hosts)

    setLogLevel('info')
    topo = TreeTopology(switches = s, hosts = h)
    net = Mininet(topo=topo, link=TCLink, host=CPULimitedHost)
    c = net.addController('c', controller=Controller, ip='127.0.0.1', port=6633)

    net.addNAT().configDefault()
    net.start()
    #net.pingAll()
    stream(net)
    CLI(net)

    net.stop()
    os.system('sudo mn -c')
    info('*** You\'ve successfully exited mininet\n')
