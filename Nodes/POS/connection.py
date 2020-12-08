"""
Created on Tue Dec 7 11:15:42 2020

@author: Gursimran Singh, Govind Sharma
"""

from p2pnetwork.node import Node
from dateutil import parser
from uuid import uuid4
import random
import socket
import os

from proof_of_stake import *

class Operation():
    def __init__(stage, to_host = "", to_port = 0, amount = 0):
        self.stage = stage
        self.to_host = to_host
        self.to_port = to_port
        self.amount = amount

class Peer(Node):
    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)

        self.stake = random.randint(1,100)

        # add host and port to id as well
        self.id = f'{socket.getfqdn()}:{port}'
        self.ledger_path = f'{self.id}.ledger'

        # create genesis block
        gen = Block(datetime.datetime.now(), [], '0')
        #Initializing Ledger with the genesis (start) block. 
        ledger_data = {
            'blocks': [gen],
            'pending_txns': []
        }
        with open(self.ledger_path, 'wb') as f:
            pickle.dump(ledger_data, f)

        # load blockchain
        self.blockchain = BlockChain(self.ledger_path)
        print(f"Peer {self.id} Started")

    def broadcast(self, obj, stage, type):
        payload = {'type': type, 'stage': stage}
        if type == 'new_txn':
            payload['obj'] = obj.__dict__ 
        elif type == 'new_block':
            d = obj.__dict__
            d['timestamp'] = d['timestamp'].__str__()
            d['transactions'] = [txn.__dict__ for txn in d["transactions"]]
            payload['obj'] = d
        elif type == 'stake':
        	payload['stake'] = self.stake
        payload = json.dumps(payload)

        for node in self.nodes_outbound:
            if(type == "ack" or type == "stake"): 
                if("ugster501" in node.id): self.send_to_node(node, payload)
            else: 
                if("ugster501" not in node.id): self.send_to_node(node, payload)

    def node_message(self, node, data):
        print(self.id, " - node_message from " + node.id + ": " + str(data))

        with open(self.ledger_path, 'rb') as f:
            ledger_data = pickle.load(f)
        
        if data['type'] == 'new_txn':
            new_txn = Transaction(
                data['obj']["fromAddress"], 
                data['obj']["toAddress"], 
                data['obj']["amount"]
            )
            ledger_data['pending_txns'].append(new_txn)
            self.blockchain.pendingTransactions.append(new_txn)

            with open(self.ledger_path, 'wb') as f:
                pickle.dump(ledger_data, f)
            self.broadcast(None, data['stage'], type = 'ack') #no object to be send in acknowledgment

        elif data['type'] == 'new_block':
            txns = []
            for txn in data['obj']["transactions"]:
                txns.append(
                    Transaction(txn["fromAddress"], 
                    txn["toAddress"], 
                    txn["amount"])
                )
            new_block = Block(
                parser.parse(data['obj']['timestamp']), 
                txns, 
                data['obj']['previousHash'],
                data['obj']['nonce'],
                data['obj']['hash']    
            )
            ledger_data['blocks'].append(new_block)
            self.blockchain.chain.append(new_block)
            # empty out all pending transactions
            ledger_data['pending_txns'] = []
            self.blockchain.pendingTransactions = []
            with open(self.ledger_path, 'wb') as f:
                pickle.dump(ledger_data, f)

        elif data['type'] == 'send':
            txn = Transaction(self.id, f"{data['obj']['to_host']}:{data['obj']['to_port']}", data['obj']['amount'])
            self.blockchain.createTransaction(txn)
            self.broadcast(txn, data['obj']['stage'], type='new_txn')
            self.broadcast(None, data['obj']['stage'], type = 'ack') #no object to be send in acknowledgment

        elif data['type'] == 'mine':
            block = self.blockchain.minePendingTransactions()
            self.broadcast(block, data['obj']['stage'], type='new_block')
            # after mining, this node should broadcast a reward txn
            txn = Transaction(None, self.id, self.blockchain.miningReward)
            self.blockchain.createTransaction(txn)
            self.broadcast(txn, data['obj']['stage'], type='new_txn')
            self.broadcast(None, data['obj']['stage'], type = 'ack') #no object to be send in acknowledgment

        elif data['type'] == 'stake':
        	self.broadcast(None, data['obj']['stage'], type = 'stake') 

    
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
        # remove all the ledgers before stopping
        print(self.id, " - node is requested to stop!")
        os.remove(self.ledger_path)
        