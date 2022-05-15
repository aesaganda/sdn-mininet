#!/usr/bin/python
"""
This is an example how to simulate a client server environment.
"""
from pydoc import cli
from mininet.net import Containernet
from mininet.node import Controller, Switch
from mininet.cli import CLI
from mininet.link import Link, TCLink
from mininet.log import lg, info, setLogLevel
from mininet.topolib import TreeContainerNet, TreeNet


# def startNAT(nat, inetIntf="ens33", subnet="192.168.79/24"):
#     """Start NAT/forwarding between Mininet and external network
#     nat: node to access iptables from
#     inetIntf: interface for internet access
#     subnet: Mininet subnet (default 10.0/8)="""

#     # Identify the interface connecting to the mininet network
#     localIntf = nat.defaultIntf()
#     print(localIntf)

#     # Flush any currently active rules
#     nat.cmd("iptables -F")
#     nat.cmd("iptables -t nat -F")

#     # Create default entries for unmatched traffic
#     nat.cmd("iptables -P INPUT ACCEPT")
#     nat.cmd("iptables -P OUTPUT ACCEPT")
#     nat.cmd("iptables -P FORWARD DROP")

#     # Configure NAT
#     nat.cmd("iptables -I FORWARD -i", localIntf, "-d", subnet, "-j DROP")
#     nat.cmd("iptables -A FORWARD -i", localIntf, "-s", subnet, "-j ACCEPT")
#     nat.cmd("iptables -A FORWARD -i", inetIntf, "-d", subnet, "-j ACCEPT")
#     nat.cmd("iptables -t nat -A POSTROUTING -o ", inetIntf, "-j MASQUERADE")

#     # Instruct the kernel to perform forwarding
#     nat.cmd("sysctl net.ipv4.ip_forward=1")


# def stopNAT(nat):
#     """Stop NAT/forwarding between Mininet and external network"""
#     # Flush any currently active rules
#     nat.cmd("iptables -F")
#     nat.cmd("iptables -t nat -F")

#     # Instruct the kernel to stop forwarding
#     nat.cmd("sysctl net.ipv4.ip_forward=0")


if __name__ == "__main__":
    lg.setLogLevel("info")
    # net = TreeContainerNet(depth=1, fanout=2, waitConnected=True)
    net = Containernet(controller=Controller)
    net.addController("c0")

    server = net.addDocker(
        "server", dimage="aesaganda:server", ip="192.168.1.10", dcmd="python app.py")
    client = net.addDocker("client", ip="192.168.1.20",
                           dimage="aesaganda:client")
    host = net.addHost("host", ip="192.168.1.30")
    switch = net.addSwitch("s1")

    # Add NAT connectivity
    # nat = net.addNAT()

    info("--> Setup network\n")
    net.addLink(switch, server, intfName1="s1-eth0", intfName2="h1-eth0")
    net.addLink(switch, client, intfName1="s1-eth1", intfName2="h2-eth0")
    net.addLink(switch, host, intfName1="s1-eth2", intfName2="h3-eth0")
    # net.addLink(switch, nat, intfName1="s1-eth3", intfName2="nat0-eth0")

    net.start()


    info("*** Starting to execute commands\n")

    info('Execute: client.cmd("time curl server")\n')
    info(client.cmd("time curl server") + "\n")

    info('Execute: client.cmd("time curl server/hello/42")\n')
    info(client.cmd("time curl server/hello/42") + "\n")

    CLI(net)

    net.stop()
