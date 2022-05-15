#!/usr/bin/env python
from mininet.net import Containernet
from mininet.node import Docker, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Link, Intf

#################################


def startNAT(root, inetIntf='enp0s3', subnet='10.0/8'):
    """Start NAT/forwarding between Mininet and external network
    root: node to access iptables from
    inetIntf: interface for internet access
    subnet: Mininet subnet (default 10.0/8)="""

    # Identify the interface connecting to the mininet network
    localIntf = root.defaultIntf()
    print(localIntf)

    # Flush any currently active rules
    root.cmd('iptables -F')
    root.cmd('iptables -t nat -F')

    # Create default entries for unmatched traffic
    root.cmd('iptables -P INPUT ACCEPT')
    root.cmd('iptables -P OUTPUT ACCEPT')
    root.cmd('iptables -P FORWARD DROP')

    # Configure NAT
    root.cmd('iptables -I FORWARD -i', localIntf, '-d', subnet, '-j DROP')
    root.cmd('iptables -A FORWARD -i', localIntf, '-s', subnet, '-j ACCEPT')
    root.cmd('iptables -A FORWARD -i', inetIntf, '-d', subnet, '-j ACCEPT')
    root.cmd('iptables -t nat -A POSTROUTING -o ', inetIntf, '-j MASQUERADE')

    # Instruct the kernel to perform forwarding
    root.cmd('sysctl net.ipv4.ip_forward=1')


def stopNAT(root):
    """Stop NAT/forwarding between Mininet and external network"""
    # Flush any currently active rules
    root.cmd('iptables -F')
    root.cmd('iptables -t nat -F')

    # Instruct the kernel to stop forwarding
    root.cmd('sysctl net.ipv4.ip_forward=0')


def fixNetworkManager(root, intf):
    """Prevent network-manager from messing with our interface,
       by specifying manual configuration in /etc/network/interfaces
       root: a node in the root namespace (for running commands)
       intf: interface name"""
    cfile = '/etc/network/interfaces'
    line = '\niface %s inet manual\n' % intf
    config = open(cfile).read()
    if (line) not in config:
        print('*** Adding', line.strip(), 'to', cfile)
        with open(cfile, 'a') as f:
            f.write(line)
    # Probably need to restart network-manager to be safe -
    # hopefully this won't disconnect you
    root.cmd('service network-manager restart')


if '__main__' == __name__:
    net = Containernet(link=TCLink)
    # Create a node in root namespace
    root = Node('root', inNamespace=False)

    # Prevent network-manager from interfering with our interface
    fixNetworkManager(root, 'root-eth0')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    br1 = net.addHost('br1')
    br2 = net.addHost('br2')
    dhcp = net.addDocker('dhcp', ip='10.0.0.250/8', dimage="aesaganda:server")
    evil = net.addDocker('evil', ip='10.0.0.200/8', dimage="aesaganda:server")
    linkopts = {'delay': 10}
    link = net.addLink(root, br1)
    link.intf1.setIP('10.254', 8)
    net.addLink(h1, br1)
    net.addLink(evil, br1)
    net.addLink(br1, br2, cls=TCLink, **linkopts)
    net.addLink(dhcp, br2)
    net.addLink(h2, br2)
    net.start()
    startNAT(root)

    br1.cmd("ifconfig br1-eth0 0")
    br1.cmd("ifconfig br1-eth1 0")
    br1.cmd("ifconfig br1-eth2 0")
    br1.cmd("ifconfig br1-eth3 0")
    br1.cmd("brctl addbr br1")
    br1.cmd("brctl addif br1 br1-eth0")
    br1.cmd("brctl addif br1 br1-eth1")
    br1.cmd("brctl addif br1 br1-eth2")
    br1.cmd("brctl addif br1 br1-eth3")
    br1.cmd("ifconfig br1 up")
    br2.cmd("ifconfig br2-eth0 0")
    br2.cmd("ifconfig br2-eth1 0")
    br2.cmd("brctl addbr br2")
    br2.cmd("brctl addif br2 br2-eth0")
    br2.cmd("brctl addif br2 br2-eth1")
    br2.cmd("brctl addif br2 br2-eth2")
    br2.cmd("ifconfig br2 up")
    h1.cmd("ifconfig h1-eth0 0")
    h2.cmd("ifconfig h2-eth0 0")
    evil.cmd("ip route flush root 0/0")
    evil.cmd("route add -net 10.0.0.0/8 dev evil-eth0")
    evil.cmd("ip route add default via 10.0.0.254")
    dhcp.cmd("ip route flush root 0/0")
    dhcp.cmd("route add -net 10.0.0.0/8 dev dhcp-eth0")
    dhcp.cmd("ip route add default via 10.0.0.254")
    CLI(net)
    net.stop()
