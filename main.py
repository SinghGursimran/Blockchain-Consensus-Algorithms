"""
Created on Tue Dec  1 13:38:52 2020

@author: Gursimran Singh
"""

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from threading import Thread
import proof_of_work
import connection
import datetime
import pickle


if __name__ == '__main__':

	name = "ugester501"

	nodes = ["129.97.173.80:5998"]
	connections = []

	#Listener (Receiver) for the node.
	endpoint = TCP4ServerEndpoint(reactor, 5998)
	factory = connection.MyFactory()
	factory.startFactory()
	endpoint.listen(factory)

	#Initializing Ledger with the genesis (start) block. 
	save_ledger = open('ledger', 'wb')
	pickle.dump([proof_of_work.Block(datetime.datetime.now(), [], "0")], save_ledger)
	save_ledger.close()

	#Initializing pt with empty file. 
	save_pt = open('pt', 'wb')
	pickle.dump([], save_pt)
	save_pt.close()

	lending_system = proof_of_work.BlockChain() #Intializing the blockchain

	#Sender for the node
	for node in nodes:
		host, port = node.split(":")
		point = TCP4ClientEndpoint(reactor, host, int(port))
		d = connectProtocol(point, connection.MyProtocol(factory))
		connections.append(d)

	Thread(target=reactor.run, args=(False,)).start()

	while(1):
		op = input("Enter operation number\n1 Send \n2 MineBlock\n")
		if(int(op) == 1):
			to = input("Enter the name of destination node:")
			amount = input("Enter Amount:")
			lending_system.createTransaction(proof_of_work.Transaction(name, to, int(amount)))
			pt, block = proof_of_work.BlockChain.pendingTransactions, None
		elif(op == 2):
			block = lending_system.minePendingTransactions(name)
			pt = None
		else: 
			print("Wrong Opaeration, Enter Again\n")
			continue
		for connect in connections: connect.addCallback(connection.gotProtocol, block, pt)
	

	

