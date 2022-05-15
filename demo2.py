#!/usr/bin/python
"""
This is an example how to simulate a client server environment.
"""
from pydoc import cli
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import Link, TCLink
from mininet.log import info, setLogLevel

setLogLevel("info")
net = Containernet(link=TCLink)

net = Containernet(controller=Controller)
net.addController("c0")

# Server ve Host APIPA adresleriyle başlatılır. (Farklı subnette olduklarını farzedelim.)
info("--> Adding server and client container\n")

server = net.addDocker("server", dimage="aesaganda:server")
client = net.addDocker("client", dimage="aesaganda:client")
router = net.addHost("router")

# Farklı subnette olan Server ve Client Router'la birbirlerine bağlanır
info("--> Setup network\n")
Link(router, server, intfName1="r1-eth0", intfName2="h1-eth0")
Link(router, client, intfName1="r1-eth1", intfName2="h2-eth0")
net.addNAT().configDefault()
net.build()

# Changing router's inferface IPs
router.cmdPrint('ifconfig r1-eth0 192.168.10.1 netmask 255.255.255.0')
router.cmdPrint('ifconfig r1-eth1 192.168.20.1 netmask 255.255.255.0')

router.cmdPrint("echo 1 > /proc/sys/net/ipv4/ip_forward")

router.cmdPrint(
    "iptables -t nat -A POSTROUTING -o r1-eth1 -s 192.168.10.0/24 -j MASQUERADE")

router.cmdPrint("dhcpd -f -4 -cf /etc/dhcp/dhcpd.conf &")

server.cmdPrint("ifconfig h1-eth0 0")
#server.cmd("dhclient h1-eth0")
server.cmdPrint("ip addr add 192.168.1.2/24 brd + dev h1-eth0")
server.cmdPrint("ip route add default via 192.168.1.1")

client.cmdPrint("ifconfig h2-eth0 0")
client.cmdPrint("ip addr add 10.0.0.2/24 brd + dev h2-eth0")
client.cmdPrint("ip route add default via 10.0.0.1")


# info("--> Starting to execute commands\n")

# info('Execute: client.cmd("time curl 10.0.0.251")\n')
# info(client.cmd("time curl 10.0.0.251") + "\n")

# info('Execute: client.cmd("time curl 10.0.0.251/hello/42")\n')
# info(client.cmd("time curl 10.0.0.251/hello/42") + "\n")

CLI(net)

net.stop()
