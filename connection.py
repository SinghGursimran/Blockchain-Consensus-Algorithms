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
		self.state = "BLOCK"
		self.remote_nodeid = None
		self.nodeid = self.factory.nodeid

	def connectionMade(self):
		print("Connection from", self.transport.getPeer())

	def connectionLost(self, reason):
		if self.remote_nodeid in self.factory.peers:
			self.factory.peers.pop(self.remote_nodeid)
		print(self.nodeid, "disconnected")

	def create_serializable_block(self, block):
		d = block.__dict__
		l = []
		d["timestamp"] = d["timestamp"].__str__()
		for transaction in d["transactions"]: l.append(transaction.__dict__)
		d["transactions"] = l
		return d

	def create_serializable_pt(self, pt):
		l = []
		for transaction in pt: l.append(transaction.__dict__)
		return proof_of_work.Block(None, l).__dict__

	def dataReceived(self, data):
		for line in data.splitlines():
			line = line.strip()
			if self.state == "BLOCK":
				self.handle_block(line)
				self.state = "READY"

	def send_block(self, block, pt):
		if(pt == None):
			dump = self.create_serializable_block(block)
		else:
			dump = self.create_serializable_pt(pt)
		dump['nodeid'] = self.nodeid 
		block = json.dumps(dump)
		print(dump)
		self.transport.write(block.encode('utf8'))

	def make_obj(self, d):
		transactions = []
		for transaction in d["transactions"]:
			trans = proof_of_work.Transaction(transaction["fromAdress"], transaction["toAdress"], transaction["amount"])
			transactions.append(trans)
		if(d["timestamp"] == None): return transactions, "pt"
		return proof_of_work.Block(parser.parse(d["timestamp"]), transactions, d["previousHash"], d["nonce"], d["hash"]), "block"

	def update_ledger_block(self, block):

		load_file = open('ledger', 'rb')
		ledger = pickle.load(load_file)
		load_file.close()

		ledger.append(block)

		save_ledger = open('ledger', 'wb')
		pickle.dump(ledger, save_ledger)
		save_ledger.close()

	def update_ledger_pt(self, pt):
		save_pt = open('pt', 'wb')
		pickle.dump(pt, save_pt)
		save_pt.close()

	def handle_block(self, block):
		block = json.loads(block)
		self.remote_nodeid = block["nodeid"]
		if self.remote_nodeid == self.nodeid:
			print("Connected to myself.")
			self.transport.loseConnection()
		else:
			self.factory.peers[self.remote_nodeid] = self
		ret, typ = self.make_obj(block)
		if(typ == "block"): self.update_ledger(ret)
		else: self.update_ledger_pt(ret)
		
class MyFactory(Factory):

	def generate_nodeid(self): return str(uuid4())

	def startFactory(self):
		self.peers = {}
		self.nodeid = self.generate_nodeid()

	def buildProtocol(self, addr):
		return MyProtocol(self)

def gotProtocol(protocol, block, pt):
	protocol.send_block(block, pt)
