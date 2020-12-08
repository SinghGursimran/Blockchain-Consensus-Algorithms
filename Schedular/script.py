file = open('small.txt', 'r') 
op = file.readline()
total_nodes = 20
op_num = 1
while(op):
	print(op)
	data = op.split()
	host, port = data[1], int(data[2])
	if(data[0] == "send"):
		operation = Operation(op_num, data[3], int(data[4]), int(data[5]))
		node.broadcast(host, port, operation, type = "send")
	else:
		operation = Operation(op_num)
		node.broadcast(host, port, operation, type = "mine")
	while(Counter.d.get(op_num,0) < total_nodes): continue
	print("Stage " + str(op_num) + " Completed")
	op_num += 1
	op = file.readline()