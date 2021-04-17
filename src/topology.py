#!/usr/bin/python

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel, info, error
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
    run_as_root = "sed -i 's/geteuid/getppid/' /usr/bin/vlc"
    server_command = 'cvlc {path} --sout "#rtp{{dst=10.0.0.{host_number},port=500{host_number}}}" --run-time {duration} vlc://quit &'
    client_command = 'cvlc rtp://@:500{host_number} &'

    info('*** Starting VLC servers...\n')
    h0 = net.get('h0')
    h0.cmd(run_as_root)

    for h in range(hosts):
        h0.cmd(server_command.format(path = path, host_number = h + 1, duration = str(duration + delay)))

    info('*** Starting VLC clients...\n')
    time.sleep(delay)

    for h in range(hosts):
        host = net.get('h{}'.format(h + 1))
        host.cmd(client_command.format(host_number = h + 1))

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
    file = './samples/audio.mp3'
    duration = 30

    if args.switches:
        switches = int(args.switches)

    if args.hosts:
        hosts = int(args.hosts)

    if args.file:
        file = args.file
        if not os.path.isfile(file):
            error('File doesn\'t exist\n')
            exit()

    if args.duration:
        duration = int(args.duration)

    setLogLevel('info')
    topo = TreeTopology(switches = switches, hosts = hosts)
    net = Mininet(topo = topo, controller=Controller, link = TCLink, host = CPULimitedHost)

    net.addNAT().configDefault()
    net.start()
    stream(net, hosts = hosts, path = file, duration = duration)
    CLI(net)

    net.stop()
    os.system('sudo mn -c')
    info('*** You\'ve successfully exited mininet\n')
