Run the following commands on all systems:  
Step 1:   
kill -9 $(lsof -t -i tcp:5990)  
kill -9 $(lsof -t -i tcp:5991)  
kill -9 $(lsof -t -i tcp:5992)  
kill -9 $(lsof -t -i tcp:5993)  
kill -9 $(lsof -t -i tcp:5994)  
kill -9 $(lsof -t -i tcp:5995)  
kill -9 $(lsof -t -i tcp:5996)  
kill -9 $(lsof -t -i tcp:5997)  
kill -9 $(lsof -t -i tcp:5998)  
kill -9 $(lsof -t -i tcp:5999)  
clear  
python3  
  
Step 2:  
from main import *  
n = 5 #Select the number of nodes to run on single system  
   
On Nodes: nodes = create_local_nodes(n) #Creating n nodes on each system  
On Schedular: create_local_nodes() #Create single node for scheduling  
  
Step 3:  
for node in nodes:  
		connect_with_all(node, n) #Connecting nodes  
  
Step 3:  
On Schedular: exec(open('script.py').read()) #Starting script  
