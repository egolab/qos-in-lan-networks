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


class TreeTopology(Topo):
    def __init__(self, switches, hosts):
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
                self.addLink(host_name, switch_name, bw = 10, delay = '1ms', loss = 5)

            index = index + hosts


def stream(net, hosts, path, duration):
    delay = 5
    server_command = 'cvlc ./samples/{path} --sout "#standard{{access=http,mux=ogg,dst=0.0.0.0:8080}}" --run-time {duration} vlc://quit &'.format(path = path, duration = str(duration + delay))
    client_command = 'cvlc http://10.0.0.254:8080 &'
    run_as_root = "sed -i 's/geteuid/getppid/' /usr/bin/vlc"

    info('*** Starting VLC server...\n')
    h0 = net.get('h0')
    h0.cmd(run_as_root)
    h0.cmd(server_command)

    info('*** Starting VLC clients...\n')
    time.sleep(delay)

    for h in range(hosts):
        host = net.get('h{}'.format(h + 1))
        host.cmd(client_command)

    info('*** VLC server and clients started\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--switches', help = 'Number of Switches')
    parser.add_argument('--hosts', help = 'Number of Hosts connected to each switch')
    parser.add_argument('--file', help = 'Audio file that will be streamed')
    parser.add_argument('--duration', help = 'Streaming duration')
    args = parser.parse_args()

    switches = 2
    hosts = 1
    file = 'audio.mp3'
    duration = 30

    if args.switches:
        switches = int(args.switches)

    if args.hosts:
        hosts = int(args.hosts)

    if args.file:
        file = args.file

    if args.duration:
        duration = int(args.duration)


    setLogLevel('info')
    topo = TreeTopology(switches = switches, hosts = hosts)
    net = Mininet(topo = topo, link = TCLink, host = CPULimitedHost)
    c = net.addController('c', controller = Controller, ip = '127.0.0.1', port = 6633)

    net.addNAT().configDefault()
    net.start()
    stream(net, hosts = hosts, path = file, duration = duration)
    CLI(net)

    net.stop()
    os.system('sudo mn -c')
    info('*** You\'ve successfully exited mininet\n')
