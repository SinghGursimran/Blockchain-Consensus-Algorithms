host, port = "ugster503", 5998
operation = Operation(8, "ugster504", 5998, 100)
node.broadcast(host, port, operation, type = "send")
while(Counter.d.get(8,0) < 4): continue
print("Stage 8 Completed")

host, port = "ugster504", 5999
operation = Operation(9)
node.broadcast(host, port, operation, type = "mine")

while(Counter.d.get(9,0) != 4): continue
print("Stage 9 Completed")