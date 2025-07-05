from helix.client import Client, Query
from helix.types import Payload
from typing import List
from helix.instance import Instance

db = Client(local=True, port=6969)

class create_user(Query):
    def __init__(self, name:str, age:int, email:str, now:int):
        super().__init__()
        self.name = name
        self.age = age
        self.email = email
        self.now = now

    def query(self) -> List[Payload]:
        return [{"name": self.name, "age": self.age, "email": self.email, "now": self.now}]

    def response(self, response):
        return response

class get_users(Query):
    def __init__(self):
        super().__init__()

    def query(self) -> List[Payload]:
        return [{}]

    def response(self, response):
        return response

class create_follow(Query):
    def __init__(self, follower_id: str, followed_id: str, now: int):
        super().__init__()
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.now = now

    def query(self):
        return [{"follower_id": self.follower_id, "followed_id": self.followed_id, "now": self.now}]


    def response(self, response):
        return response

class create_post(Query):
    def __init__(self, user_id: str, content: str, now: int):
        super().__init__()
        self.user_id = user_id
        self.content = content
        self.now = now

    def query(self):
        return [{"user_id": self.user_id, "content": self.content, "now": self.now}]


    def response(self, response):
        return response

class get_posts(Query):
    def __init__(self):
        super().__init__()

    def query(self) -> List[Payload]:
        return [{}]

    def response(self, response):
        return response

class get_posts_by_user(Query):
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id

    def query(self) -> List[Payload]:
        return [{"user_id": self.user_id}]

    def response(self, response):
        return response

class get_followed_users(Query):
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id

    def query(self) -> List[Payload]:
        return [{"user_id": self.user_id}]

    def response(self, response):
        return response


class get_followed_users_posts(Query):
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id

    def query(self) -> List[Payload]:
        return [{"user_id": self.user_id}]

    def response(self, response):
        return response

print("\n" + "-"*20 + "CREATE USERS" + "-"*20)
user1 = db.query(create_user("John", 30, "john@example.com", 1722222222))
user2 = db.query(create_user("Jane", 25, "jane@example.com", 1722222222))
print(user1, "\n", user2)
print("\n")

user1_id = user1[0]['user'][0]['id']
user2_id = user2[0]['user'][0]['id']

print("-"*20 + "GET USERS" + "-"*20)
for user in db.query(get_users())[0]['users']:
    print(user)
print("\n")

print("-"*20 + "CREATE FOLLOW" + "-"*20)
print("Jane follows John")
print(db.query(create_follow(user1_id, user2_id, 1892222222)))
print("\n")

print("-"*20 + "CREATE POST" + "-"*20)
content1 = "Sample Post Content Hello World 1"
content2 = "Sample Post Content Hello World 2"
print(db.query(create_post(user1_id, content1, 1983333333))[0]['post'][0])
print(db.query(create_post(user2_id, content2, 1983333333))[0]['post'][0])
print("\n")

print("-"*20 + "GET POSTS" + "-"*20)
for post in db.query(get_posts())[0]['posts']:
    print(post)
print("\n")

print("-"*20 + "GET POSTS BY USER" + "-"*20)
print(f"Should get {content1}")
for post in db.query(get_posts_by_user(user1_id))[0]['posts']:
    print(post)
print("\n")

print("-"*20 + "GET FOLLOWED USERS" + "-"*20)
for user in db.query(get_followed_users(user1_id))[0]['followed']:
    print(user)
print("\n")

print("-"*20 + "GET FOLLOWED USERS POSTS" + "-"*20)
for post in db.query(get_followed_users_posts(user1_id))[0]['posts']:
    print(post)
print("\n")

print("Should have 1 instance not running after script ends")
print("Try running `helix instances` to see")
