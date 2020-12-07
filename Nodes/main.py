"""
Created on Tue Dec  1 13:38:52 2020

@author: Gursimran Singh, Govind Sharma
"""

from connection import *
from proof_of_work import *

network = {
		'ugster501': '129.97.173.79', #This is the coordinator node. 
		'ugster503': '129.97.173.81',
		'ugster504': '129.97.173.82'
	}

ports = [5998, 5999]

hostname = socket.getfqdn()

def create_local_nodes():
	nodes = []
	host = network[hostname]
	for port in ports:
		node = Peer(host, port)
		node.start()
		nodes.append(node)
	return nodes

def stop_local_nodes(nodes):
	for node in nodes:
		node.stop()

def connect_with_all(node):
	for name, host in network.items():
		if(name == "ugster501"):  #Scheduler node
			node.connect_with_node(host, 5998)
			continue
		for port in ports:
			if node.host == host and node.port == port:
				print ("Skipping", name, port)
				continue
			try:
				print ("Connecting to", name, port)
				node.connect_with_node(host, port)
			except:
				print ('Could not connect {node.id} with {host}:{port}')

if __name__ == '__main__':
	nodes = create_local_nodes()
	# somehow wait till other local nodes are up
	for node in nodes:
		connect_with_all(node)

	# the following two things are to be read from a schedule file
	# create transactions at random intervals and broadcast
	txn = Transaction(hostname, "ugester502", 100)
	nodes[0].blockchain.createTransaction(txn)
	nodes[0].broadcast(txn, type='new_txn')

	# mine pending transactions at random intervals and broadcast
	block = nodes[0].blockchain.minePendingTransactions()
	nodes[0].broadcast(block, type='new_block')
	# after mining, this node should broadcast a reward txn
	txn = Transaction(None, nodes[0].id, nodes[0].blockchain.miningReward)
	nodes[0].blockchain.createTransaction(txn)
	nodes[0].broadcast(txn, type='new_txn')

	stop_local_nodes(nodes)