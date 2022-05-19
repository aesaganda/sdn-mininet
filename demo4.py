#!/usr/bin/env python

"""
Example to create a Mininet topology and connect it to the internet via NAT
"""

from http import client, server
from mininet.net import Containernet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.node import Docker
from mininet.topo import Topo
# from mininet.topolib import TreeNet


# class TreeTopo(Topo):
#     "Topology for a tree network with a given depth and fanout."

#     def build(self, depth=1, fanout=2):
#         # Numbering:  h1..N, s1..M
#         self.hostNum = 1
#         self.switchNum = 1
#         # Build topology
#         self.addTree(depth, fanout)

#     def addTree(self, depth, fanout):
#         """Add a subtree starting with node n.
#            returns: last node added"""
#         isSwitch = depth > 0
#         if isSwitch:
#             node = self.addSwitch('s%s' % self.switchNum)
#             self.switchNum += 1
#             for _ in range(fanout):
#                 child = self.addTree(depth - 1, fanout)
#                 self.addLink(node, child)
#         else:
#             node = self.addHost('h%s' % self.hostNum)
#             self.hostNum += 1
#         return node


class ContainerTreeTopo(Topo):
    "Topology for a container tree network with a given depth and fanout."

    def build(self, depth=1, fanout=2):
        # Numbering:  h1..N, s1..M
        self.hostNum = 1
        self.switchNum = 1
        # Build topology
        self.addTree(depth, fanout)

    def addTree(self, depth, fanout):
        """Add a subtree starting with node n.
           returns: last node added"""
        isSwitch = depth > 0
        if isSwitch:
            node = self.addSwitch('switch%s' % self.switchNum)
            self.switchNum += 1
            for _ in range(fanout):
                child = self.addTree(depth - 1, fanout)
                self.addLink(node, child)

        # Eklenme sırası çift sayı olan containerler client görevi üstlenir
        else:
            if(self.hostNum % 2 == 0):
                node = self.addHost('client%s' % self.hostNum,
                                    cls=Docker, dimage="aesaganda:client")
                self.hostNum += 1

        # Eklenme sırası tek sayı olan containerler server görevi üstlenir
            else:
                node = self.addHost('server%s' % self.hostNum,
                                    cls=Docker, dimage="aesaganda:server", dcmd="python app.py")
                self.hostNum += 1
        return node


# def TreeNet(depth=1, fanout=2, **kwargs):
#     "Convenience function for creating tree networks."
#     topo = TreeTopo(depth, fanout)
#     return Mininet(topo, **kwargs)


def TreeContainerNet(depth=1, fanout=2, **kwargs):
    "Convenience function for creating tree networks with Docker."
    topo = ContainerTreeTopo(depth, fanout)
    return Containernet(topo=topo, **kwargs)


if __name__ == '__main__':
    lg.setLogLevel('info')
    net = TreeContainerNet(depth=1, fanout=2, waitConnected=True)
    # Add NAT connectivity
    net.addNAT().configDefault()
    net.start()
    info("*** Hosts are running and should have internet connectivity\n")
    info("*** Type 'exit' or control-D to shut down network\n")

    info('*** Starting to execute commands\n')

    # info('Execute: client.cmd("time curl 10.0.0.2")\n')
    # info(h1.cmd("time curl 10.0.0.2") + "\n")

    # info('Execute: client.cmd("time curl 10.0.0.2/hello/42")\n')
    # info(h2.cmd("time curl 10.0.0.2/hello/42") + "\n")

    # info('Execute: client.cmd("time curl server")\n')
    # info(client.cmd("time curl 10.0.0.2") + "\n")

    # info('Execute: client.cmd("time curl server/hello/42")\n')
    # info(client.cmd("time curl 10.0.0.2/hello/42") + "\n")

    CLI(net)
    # Shut down NAT
    net.stop()
