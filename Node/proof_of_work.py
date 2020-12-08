"""
Created on Tue Dec  5 12:19:52 2020

@author: Gursimran Singh, Govind Sharma
"""

import datetime
import hashlib
import pickle
import json	

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
		self.nonce = nonce
		if(hash == None): self.hash = self.calculateHash()	
		else: self.hash = hash

	def calculateHash(self):
		info = str(self.timestamp) + str([str(transaction) for transaction in self.transactions]) + str(self.previousHash) + str(self.nonce)
		return hashlib.sha256(info.encode('utf-8')).hexdigest()

	# Proof of work algorithm
	def mineBlock(self, difficulty):
		self.hash = self.calculateHash()
		while(self.hash[:difficulty] != "0"*difficulty):
			self.nonce += 1
			self.hash = self.calculateHash()

class BlockChain(object):
	def __init__(self, ledger_path):
		self.ledger_path = ledger_path
		self.chain = None
		self.difficulty = 4
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
		print("mining block...")
		newBlock.mineBlock(self.difficulty)
		print("block mined:", newBlock.hash)
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