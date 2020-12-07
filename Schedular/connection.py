"""
Created on Tue Dec  5 12:15:46 2020

@author: Gursimran Singh, Govind Sharma
"""

from p2pnetwork.node import Node
from uuid import uuid4
import socket
import os
import json

class Counter():

    d = {}

class Operation():
    def __init__(self, stage, to_host = "", to_port = 0, amount = 0):
        self.stage = stage
        self.to_host = to_host
        self.to_port = to_port
        self.amount = amount

class Peer(Node):
    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)
        self.id = f'{socket.getfqdn()}:{port}'
        print(f"Peer {self.id} Started")

    def broadcast(self, from_host, from_port, obj, type):
        payload = {'type': type}
        payload['obj'] = obj.__dict__
        payload = json.dumps(payload)
        for node in self.nodes_outbound:
            if(f'{from_host}:{from_port}' == node.id): self.send_to_node(node, payload)

    def node_message(self, node, data):
        print(self.id, " - node_message from " + node.id + ": " + str(data))

        if(data['type'] != "ack"): 
            print("unknown data received")
            return

        Counter.d[data["stage"]] = Counter.d.get(data["stage"],0) + 1
        print(Counter.d[data["stage"]])

    def outbound_node_connected(self, node):
        print(self.id, " - outbound_node_connected: " + node.id)
        
    def inbound_node_connected(self, node):
        print(self.id, " - inbound_node_connected: " + node.id)

    def inbound_node_disconnected(self, node):
        print(self.id, " - inbound_node_disconnected: " + node.id)

    def outbound_node_disconnected(self, node):
        print(self.id, " - outbound_node_disconnected: " + node.id)
        
    def node_disconnect_with_outbound_node(self, node):
        print(self.id, " - node wants to disconnect with oher outbound node: " + node.id)
        
    def node_request_to_stop(self):
        print(self.id, " - node is requested to stop!")
        