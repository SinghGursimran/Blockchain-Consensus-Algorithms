"""
Created on Tue Dec  1 13:38:52 2020

@author: Gursimran Singh, Govind Sharma
"""
from connection import *

network = {
		'ugster501': '129.97.173.79', #This is the coordinator node. 
		'ugster503': '129.97.173.81',
		'ugster504': '129.97.173.82'
	}

ports = [5998, 5999]

hostname = socket.getfqdn()

def create_local_nodes():
	host = network[hostname]
	node = Peer(host, 5998) #coordinator runs on port 5998
	node.start()
	return node

def connect_with_all(node):
	for name, host in network.items():
		if node.host == host:
				print ("Skipping - Coordinator", name)
				continue
		for port in ports:
			try:
				print ("Connecting to", name, port)
				node.connect_with_node(host, port)
			except:
				print ('Could not connect {node.id} with {host}:{port}')

if __name__ == '__main__':
	node = create_local_nodes()

	# somehow wait till other local nodes are up
	connect_with_all(node)

	#Send 100 from ugster503:5998 to ugster504:5998
	host, port = "ugster503", 5998
	operation = Operation(1, "ugster504", 5998, 100)
	node.broadcast(host, port, operation, type = "send")

	#Mine pending transactions at ugster504:5999
	host, port = "ugster504", 5999
	operation = Operation(2)
	node.broadcast(host, port, operation, type = "mine")
	
	node.stop()


