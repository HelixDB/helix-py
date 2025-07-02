from helix.instance import Instance

helix_instance = Instance("helixdb-cfg", 6969, verbose=True)
print("-" * 70 + '\n')

# Deploy
print("\n" + "-"*20 + "DEPLOY" + "-"*20)
print("Instance should already be running:")
helix_instance.deploy()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Stop
print("\n" + "-"*20 + "STOP" + "-"*20)
helix_instance.stop()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Start
print("\n" + "-"*20 + "START" + "-"*20)
helix_instance.start()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Delete
#print("\n" + "-"*20 + "DELETE" + "-"*20)
#helix_instance.delete()
#print("-" * 70 + '\n')
#print("Should not have any instances:")
#helix_instance.status()
#print("-" * 70 + '\n')

