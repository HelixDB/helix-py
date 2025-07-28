from helix.instance import Instance

helix_instance = Instance("helixdb-cfg", 6969, verbose=True)
print("-" * 70 + '\n')

# Deploy
print("\n" + "-"*32 + "DEPLOY" + "-"*32)
print("Instance should already be running:")
helix_instance.deploy()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Stop
print("\n" + "-"*33 + "STOP" + "-"*33)
helix_instance.stop()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Start
print("\n" + "-"*31 + "REDEPLOY" + "-"*31)
helix_instance.deploy(redeploy=True)
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Delete
print("\n" + "-"*32 + "DELETE" + "-"*32)
helix_instance.delete()
print("-" * 70 + '\n')
print("Should not have any instances:")
helix_instance.status()
print("-" * 70 + '\n')

