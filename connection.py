"""
Created on Tue Dec  5 12:15:46 2020

@author: Gursimran Singh
"""

from twisted.internet.protocol import Protocol, Factory
from dateutil import parser
from uuid import uuid4
import proof_of_work
import pickle
import json

class MyProtocol(Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.state = "POW"
        self.remote_nodeid = None
        self.nodeid = self.factory.nodeid

    def connectionMade(self):
        print("Connection from", self.transport.getPeer())

    def connectionLost(self, reason):
        if self.remote_nodeid in self.factory.peers:
            self.factory.peers.pop(self.remote_nodeid)
        print(self.nodeid, "disconnected")

    def create_serializable(self, block):
        d = block.__dict__
        l = []
        d["timestamp"] = d["timestamp"].__str__()
        for transaction in d["transactions"]: l.append(transaction.__dict__)
        d["transactions"] = l
        return d

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            if self.state == "POW":
                self.handle_pow(line)
                self.state = "READY"

    def send_pow(self, block):
        dump = self.create_serializable(block)
        dump['nodeid'] = self.nodeid 
        pow = json.dumps(dump)
        self.transport.write(pow.encode('utf8'))

    def make_obj(self, d):
    	timestamp = parser.parse(d["timestamp"])
    	transactions = []
    	for transaction in d["transactions"]:
    		trans = proof_of_work.Transaction(transaction["fromAdress"], transaction["toAdress"], transaction["amount"])
    		transactions.append(trans)
    	return proof_of_work.Block(timestamp, transactions, d["previousHash"], d["nonce"], d["hash"]) 

    def update_ledger(self, block):

        load_file = open('ledger', 'rb')
        ledger = pickle.load(load_file)
        load_file.close()

        ledger.append(block)

        save_ledger = open('ledger', 'wb')
        pickle.dump(ledger, save_ledger)
        save_ledger.close()

    def handle_pow(self, pow):
        pow = json.loads(pow)
       	self.remote_nodeid = pow["nodeid"]
        if self.remote_nodeid == self.nodeid:
        	print("Connected to myself.")
        	self.transport.loseConnection()
        else:
            self.factory.peers[self.remote_nodeid] = self
        block = self.make_obj(pow)
        self.update_ledger(block)
        
class MyFactory(Factory):

    def generate_nodeid(self): return str(uuid4())

    def startFactory(self):
        self.peers = {}
        self.nodeid = self.generate_nodeid()

    def buildProtocol(self, addr):
        return MyProtocol(self)

def gotProtocol(protocol, block):
    protocol.send_pow(block)
