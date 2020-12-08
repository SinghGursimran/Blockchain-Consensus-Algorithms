file = open('small.txt', 'r') 
op = file.readline()
total_nodes = 20
op_num = 1
while(op):
	print(op)
	data = op.split()
	if(data[0] == "send"):
		host, port = data[1], int(data[2])
		operation = Operation(op_num, data[3], int(data[4]), int(data[5]))
		node.broadcast(host, port, operation, type = "send")
	else:
		operation = Operation(op_num)
		node.broadcast(host, port, operation, type = "stake")
	while(Counter.d_ack.get(op_num,0) < total_nodes): continue
	print("Stage " + str(op_num) + " Completed")
	op_num += 1
	op = file.readline()