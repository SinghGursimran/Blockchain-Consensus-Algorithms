"""
Created on Tue Dec  5 12:19:52 2020

@author: Gursimran Singh
"""

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

	chain = None
	pendingTransactions = []

	def __init__(self):
		self.difficulty = 4
		self.miningReward = 100

		load_file = open('ledger', 'rb')
		BlockChain.chain = pickle.load(load_file) #Initializing the block chain
		load_file.close()

		load_pt = open('pt', 'rb')
		BlockChain.pendingTransactions = pickle.load(load_pt) #Initializing the block chain
		load_pt.close()

	def getLatestBlock(self):
		return BlockChain.chain[-1]

	def minePendingTransactions(self, miningRewardAdress):
		
		newBlock = Block(datetime.datetime.now(), BlockChain.pendingTransactions)
		newBlock.previousHash = self.getLatestBlock().hash
		# you can check if transactions are valid here
		print("mining block...")
		newBlock.mineBlock(self.difficulty)
		print("block mined:", newBlock.hash)
		print("block succesfully mined.")
		BlockChain.chain.append(newBlock)

		save_ledger = open('ledger', 'wb')
		pickle.dump(BlockChain.chain, save_ledger)
		save_ledger.close()

		BlockChain.pendingTransactions = [Transaction(None, miningRewardAdress, self.miningReward)]
		return newBlock

	def createTransaction(self, transaction):
		BlockChain.pendingTransactions.append(transaction)

	def getBalanceOfAdress(self, adress):
		balance = 0
		for block in BlockChain.chain:
			for transaction in block.transactions:
				if transaction.fromAdress == adress:
					balance -= transaction.amount
				if transaction.toAdress == adress:
					balance += transaction.amount
		return balance

	def isBlockChainValid(self):
		for previousBlock, block in zip(BlockChain.chain, BlockChain.chain[1:]):
			if block.hash != block.calculateHash():
				return False
			if block.previousHash != previousBlock.hash:
				return False
		return True

	def showBlockChain(self):
		print("blockchain: fedecoin\n")
		for block in BlockChain.chain:
			print("block")
			print("timestamp:", block.timestamp)
			pprint("transactions:", block.transactions)
			print("previousHash:", block.previousHash)
			print("hash:", block.hash, "\n")

	def showAdressBalance(self, adress):
		print(adress, "balance:", self.getBalanceOfAdress(adress))