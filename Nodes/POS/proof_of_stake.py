"""
Created on Tue Dec 8  00:20:24 2020

@author: Gursimran Singh, Govind Sharma
"""

import datetime
import hashlib
import pickle
import json	

#The main difference from POW is that their's no need to solve complex mathematical puzzle.
#Instead validators (minners) are selected based upon the stake put in by the validators.

class Transaction(object):

	def __init__(self, fromAddress, toAddress, amount):
		self.fromAddress = fromAddress if(fromAddress != None) else " "
		self.toAddress = toAddress
		self.amount = amount

	def __str__(self):
		return self.fromAddress + " " + self.toAddress + " " + str(self.amount)

class Block(object):

	def __init__(self, timestamp, transactions, previousHash="", nonce = 0, hash = None):
		self.timestamp = timestamp
		self.transactions = transactions
		self.previousHash = previousHash
		self.nonce = nonce #nonce is not used, just taking it as input to keep the code generic with proof of work.
		if(hash == None): self.hash = self.calculateHash()	
		else: self.hash = hash

	def calculateHash(self):
		info = str(self.timestamp) + str([str(transaction) for transaction in self.transactions]) + str(self.previousHash)
		self.hash = hashlib.sha256(info.encode('utf-8')).hexdigest()

class BlockChain(object):
	def __init__(self, ledger_path):
		self.ledger_path = ledger_path
		self.chain = None
		self.pendingTransactions = []
		self.miningReward = 100

		with open(self.ledger_path, 'rb') as f:
			ledger_data = pickle.load(f)
		self.chain = ledger_data['blocks']
		self.pendingTransactions = ledger_data['pending_txns']

	def getLatestBlock(self):
		return self.chain[-1]

	def minePendingTransactions(self):
		newBlock = Block(datetime.datetime.now(), self.pendingTransactions)
		newBlock.previousHash = self.getLatestBlock().hash
		# you can check if transactions are valid here
		print("validating block...")
		newBlock.calculateHash()
		print("block validated:", newBlock.hash)
		print("block succesfully mined.")
		self.chain.append(newBlock)

		with open(self.ledger_path, 'rb') as f:
			ledger_data = pickle.load(f)
		ledger_data['blocks'].append(newBlock)
		ledger_data['pending_txns'] = []
		self.pendingTransactions = []
		with open(self.ledger_path, 'wb') as f:
			pickle.dump(ledger_data, f)
		return newBlock

	def createTransaction(self, transaction):
		self.pendingTransactions.append(transaction)

	def getBalanceOfAddress(self, address):
		balance = 0
		for block in self.chain:
			for transaction in block.transactions:
				if transaction.fromAddress == address:
					balance -= transaction.amount
				if transaction.toAddress == address:
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
			print("transactions:", block.transactions)
			print("previousHash:", block.previousHash)
			print("hash:", block.hash, "\n")

	def showAddressBalance(self, address):
		print(address, "balance:", self.getBalanceOfAddress(address))