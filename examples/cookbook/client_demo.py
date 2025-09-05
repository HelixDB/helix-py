from helix.client import Client
from datetime import datetime, timezone

client = Client(local=True, port=6969)

print("\n" + "-"*20 + "CREATE USERS" + "-"*20)
users = client.query("create_user", [
    {"name": "John", "age": 30, "email": "john@example.com", "now": datetime.now(timezone.utc).isoformat()},
    {"name": "Jane", "age": 25, "email": "jane@example.com", "now": datetime.now(timezone.utc).isoformat()}
])
print(users)
user1 = users[0]['user']
user2 = users[1]['user']
print("\n")

user1_id = user1['id']
user2_id = user2['id']

print("-"*20 + "GET USERS" + "-"*20)
for user in client.query("get_users")[0]['users']:
    print(user)
print("\n")

print("-"*20 + "CREATE FOLLOW" + "-"*20)
print("Jane follows John")
print(client.query("create_follow", {"follower_id": user1_id, "followed_id": user2_id, "now": datetime.now(timezone.utc).isoformat()}))
print("\n")

print("-"*20 + "CREATE POST" + "-"*20)
content1 = "Sample Post Content Hello World 1"
content2 = "Sample Post Content Hello World 2"
print(
    client.query(
        "create_post", [
            {"user_id": user1_id, "content": content1, "now": datetime.now(timezone.utc).isoformat()},
            {"user_id": user2_id, "content": content2, "now": datetime.now(timezone.utc).isoformat()}
        ]
    )[0]['post']
)
print("\n")

print("-"*20 + "GET POSTS" + "-"*20)
for post in client.query("get_posts")[0]['posts']:
    print(post)
print("\n")

print("-"*20 + "GET POSTS BY USER" + "-"*20)
print(f"Should get {content1}")
for post in client.query("get_posts_by_user", {"user_id": user1_id})[0]['posts']:
    print(post)
print("\n")

print("-"*20 + "GET FOLLOWED USERS" + "-"*20)
for user in client.query("get_followed_users", {"user_id": user1_id})[0]['followed']:
    print(user)
print("\n")

print("-"*20 + "GET FOLLOWED USERS POSTS" + "-"*20)
for post in client.query("get_followed_users_posts", {"user_id": user1_id})[0]['posts']:
    print(post)
print("\n")

print("Should have 1 instance not running after script ends")
print("Try running `helix instances` to see")

