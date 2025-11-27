from xmlrpc.server import SimpleXMLRPCServer

def add(x, y):
    return x + y

server = SimpleXMLRPCServer(("0.0.0.0", 8000))
print("RPC Server listening on port 8000...")
server.register_function(add, "add")
server.serve_forever()

