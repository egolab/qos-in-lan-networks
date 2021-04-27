#!/usr/bin/python

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel, warn
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
        self.addLink('s0', 'h0', bw = 2)
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
    iperf_server_cmd = 'iperf -s -p {port} -i 1 -S 0x20 &'
    iperf_client_cmd = 'iperf -c {ip} -p {port} -t {duration} -S 0x20 &'

    h0 = net.get('h0')

    for h in range(hosts):
        h0.cmd(iperf_server_cmd.format(port = iperf_start_port + hosts + h + 1))
        host = net.get('h{}'.format(h + hosts + 1))
        host.cmd(iperf_client_cmd.format(ip = h0.IP(), port = iperf_start_port + hosts + h + 1, duration = str(duration)))

    warn("*** Background started\n")

def stream(net, hosts, duration):
    warm_up = 5
    iperf_start_port = 8000
    iperf_server_cmd = 'iperf -s -p {port} -i 1 -u -S 0x10 -y C | tee results/h{host_id}.out &'
    iperf_client_cmd = 'iperf -c {ip} -p {port} -t {duration} -u -S 0x10 -b 200000 &'

    time.sleep(warm_up)

    h0 = net.get('h0')

    for h in range(hosts):
        h0.cmd(iperf_server_cmd.format(port = iperf_start_port + h + 1, host_id = h + 1))
        host = net.get('h{}'.format(h + 1))
        host.cmd(iperf_client_cmd.format(ip = h0.IP(), port = iperf_start_port + h + 1, duration = str(duration - warm_up)))

    warn("*** Streaming started\n")

def setUpQueue(net, queueType):
    h0 = net.get('h0')

    if queueType == 'fifo':
        h0.cmd('./src/fifo.sh')
    elif queueType == 'htb':
        h0.cmd('./src/htb.sh')
    elif queueType == 'sfq':
        h0.cmd('./src/sfq.sh')
    elif queueType == 'none':
        pass
    else :
        warn('*** Queue not defined!\n')
        tearDown(net)
        sys.exit(1)

    warn('*** Queue type: {queueType}\n'.format(queueType = queueType))

def terminateOutput(hosts, queueType):
    warn('*** Output files:\n')
    for h in range(hosts):
        warn('\tresults/h{host_id}.csv\n'.format(host_id = h + 1))
        os.system('./src/terminator.sh {host_id} {queue_type} > /dev/null 2>&1'.format(host_id = h + 1, queue_type = queueType))
        os.remove('results/h{host_id}.out'.format(host_id = h + 1))

def setUpTopology(switches, hosts):
    topo = TreeTopology(switches = switches, hosts = hosts)
    net = Mininet(topo = topo, link = TCLink, host = CPULimitedHost)
    c = net.addController('c', controller = Controller, ip = '127.0.0.1', port = 6633)
    net.addNAT().configDefault()
    net.start()
    return net

def tearDown(net):
    net.stop()
    os.system('sudo mn -c > /dev/null 2>&1')

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--switches', help = 'Number of Switches')
    parser.add_argument('--hosts', help = 'Number of Hosts connected to each switch')
    parser.add_argument('--duration', help = 'Streaming duration')
    parser.add_argument('--queue', help = 'Queue type [fifo]')
    args = parser.parse_args()

    switches = 2
    hosts = 1
    duration = 30
    queueType = 'fifo'

    if args.switches:
        switches = int(args.switches)

    if args.hosts:
        hosts = int(args.hosts)

    if args.duration:
        duration = int(args.duration)

    if args.queue:
        queueType = str(args.queue)

    return (switches, hosts, duration, queueType)


if __name__ == '__main__':

    (switches, hosts, duration, queueType) = parseArguments()

    setLogLevel('warning')

    net = setUpTopology(switches, hosts)

    setUpQueue(net, queueType)

    CLI(net)

    h0 = net.get('h0')
    h0.cmd('tcpdump -i {intf} -w jows-0.pcap &'.format(intf = h0.intf()))

    background(net, hosts = hosts, duration = duration)
    stream(net, hosts = hosts, duration = duration)

    warn("*** Processing...\n")
    time.sleep(duration + 5)

    warn("*** Closing...\n")

    tearDown(net)

    terminateOutput(hosts, queueType)

    warn('*** Successfully exited mininet\n')
