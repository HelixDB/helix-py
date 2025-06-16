from helix.instance import Instance

helix_instance = Instance("helixdb-cfg", "6969", verbose=True)
print("-" * 70 + '\n')

# Deploy
helix_instance.deploy()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Stop
helix_instance.stop()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Start
helix_instance.start()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')

# Delete
helix_instance.delete()
print("-" * 70 + '\n')
helix_instance.status()
print("-" * 70 + '\n')