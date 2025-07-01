from helix import Instance, Client

helix_instance = Instance("helixdb-cfg", 6969, verbose=True)
db = Client(local=True, port=6969)
