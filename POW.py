"""
Created on Tue Dec  1 13:38:52 2020

@author: Gursimran Singh
"""

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from threading import Thread
from dateutil import parser
from pprint import pprint
from uuid import uuid4
import datetime
import hashlib
import pickle
import json


class Transaction(object):
	
	def __init__(self, fromAdress, toAdress, amount):
		self.fromAdress = fromAdress
		self.toAdress = toAdress
		self.amount = amount


class Block(object):

	def __init__(self, timestamp, transactions, previousHash="", nonce = 0, hash = None):
		self.timestamp = timestamp
		self.transactions = transactions
		self.previousHash = previousHash
		self.nonce = nonce
		if(hash == None): self.hash = self.calculateHash()	
		else: self.hash = hash

	def calculateHash(self):
		info = str(self.timestamp) + str(self.transactions) + str(self.previousHash) + str(self.nonce)
		return hashlib.sha256(info.encode('utf-8')).hexdigest()

	# Proof of work algorithm
	def mineBlock(self, difficulty):
		self.hash = self.calculateHash()
		while(self.hash[:difficulty] != "0"*difficulty):
			self.nonce += 1
			self.hash = self.calculateHash()

class BlockChain(object):

	def __init__(self):
		self.difficulty = 4
		self.pendingTransactions = []
		self.miningReward = 100

		load_file = open('ledger', 'rb')
		self.chain = pickle.load(load_file)
		load_file.close()

	def getLatestBlock(self):
		return self.chain[-1]

	def minePendingTransactions(self, miningRewardAdress):
		
		newBlock = Block(datetime.datetime.now(), self.pendingTransactions)
		newBlock.previousHash = self.getLatestBlock().hash
		# you can check if transactions are valid here
		print("mining block...")
		newBlock.mineBlock(self.difficulty)
		print("block mined:", newBlock.hash)
		print("block succesfully mined.")
		self.chain.append(newBlock)

		save_ledger = open('ledger', 'wb')
		pickle.dump(self.chain, save_ledger)
		save_ledger.close()

		self.pendingTransactions = [Transaction(None, miningRewardAdress, self.miningReward)]
		return newBlock

	def createTransaction(self, transaction):
		self.pendingTransactions.append(transaction)

	def getBalanceOfAdress(self, adress):
		balance = 0
		for block in self.chain:
			for transaction in block.transactions:
				if transaction.fromAdress == adress:
					balance -= transaction.amount
				if transaction.toAdress == adress:
					balance += transaction.amount
		return balance

	def isBlockChainValid(self):
		for previousBlock, block in zip(self.chain, self.chain[1:]):
			if block.hash != block.calculateHash():
				return False
			if block.previousHash != previousBlock.hash:
				return False
		return True

	def showBlockChain(self):
		print("blockchain: fedecoin\n")
		for block in self.chain:
			print("block")
			print("timestamp:", block.timestamp)
			pprint("transactions:", block.transactions)
			print("previousHash:", block.previousHash)
			print("hash:", block.hash, "\n")

	def showAdressBalance(self, adress):
		print(adress, "balance:", self.getBalanceOfAdress(adress))

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
    	d["timestamp"] = d["timestamp"].__str__()
    	l = []
    	for transaction in d["transactions"]:
    		l.append(transaction.__dict__)
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
    		trans = Transaction(transaction["fromAdress"], transaction["toAdress"], transaction["amount"])
    		transactions.append(trans)
    	return Block(timestamp, transactions, d["previousHash"], d["nonce"], d["hash"]) 

    def handle_pow(self, pow):
        pow = json.loads(pow)
       	self.remote_nodeid = pow["nodeid"]
        if self.remote_nodeid == self.nodeid:
        	print("Connected to myself.")
        	self.transport.loseConnection()
        else:
        	self.factory.peers[self.remote_nodeid] = self
        block = self.make_obj(pow)

        load_file = open('ledger', 'rb')
        ledger = pickle.load(load_file)
        load_file.close()

        ledger.append(block)

        save_ledger = open('ledger', 'wb')
        pickle.dump(ledger, save_ledger)
        save_ledger.close()

class MyFactory(Factory):
    def startFactory(self):
        self.peers = {}
        self.nodeid = generate_nodeid()

    def buildProtocol(self, addr):
        return MyProtocol(self)

def gotProtocol(protocol, block):
    """The callback to start the protocol exchange. Let the connecting nodes start the handshake."""
    protocol.send_pow(block)

if __name__ == '__main__':

	#Get the node id for this node in the p2p network
	generate_nodeid = lambda: str(uuid4())
	nodes = ["129.97.173.80:5998"]
	connections = []


	#Listener (Receiver) for the node.
	endpoint = TCP4ServerEndpoint(reactor, 5998)
	factory = MyFactory()
	factory.startFactory()
	endpoint.listen(factory)

	#Sender for the node
	for node in nodes:
		host, port = node.split(":")
		point = TCP4ClientEndpoint(reactor, host, int(port))
		d = connectProtocol(point, MyProtocol(factory))
		connections.append(d)

	#Initializing Ledger with the genesis (start) block
	save_ledger = open('ledger', 'wb')
	pickle.dump([Block(datetime.datetime.now(), [], "0")], save_ledger)
	save_ledger.close()
	
	Thread(target=reactor.run, args=(False,)).start()

	lending_system = BlockChain()
	lending_system.createTransaction(Transaction("adress1", "adress2", 100))
	lending_system.createTransaction(Transaction("adress2", "adress1", 50))
	block = lending_system.minePendingTransactions("fede_adress")
	for connection in connections:
		connection.addCallback(gotProtocol, block)

	