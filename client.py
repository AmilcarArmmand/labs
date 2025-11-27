import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
print("2 + 3 =", proxy.add(2, 3))

