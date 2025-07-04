QUERY create_user(name: String, age: U32, email: String, now: I32) =>
    user <- AddN<User>({name: name, age: age, email: email, created_at: now, updated_at: now})
    RETURN user

QUERY create_follow(follower_id: ID, followed_id: ID, now: I32) =>
    follower <- N<User>(follower_id)
    followed <- N<User>(followed_id)
    AddE<Follows>({since: now})::From(follower)::To(followed)
    RETURN "success"

QUERY create_post(user_id: ID, content: String, now: I32) =>
    user <- N<User>(user_id)
    post <- AddN<Post>({content: content, created_at: now, updated_at: now})
    AddE<Created>({created_at: now})::From(user)::To(post)
    RETURN post

QUERY get_users() =>
    users <- N<User>
    RETURN users

QUERY get_posts() =>
    posts <- N<Post>
    RETURN posts

QUERY get_posts_by_user(user_id: ID) =>
    posts <- N<User>(user_id)::Out<Created>
    RETURN posts

QUERY get_followed_users(user_id: ID) =>
    followed <- N<User>(user_id)::Out<Follows>
    RETURN followed

QUERY get_followed_users_posts(user_id: ID) =>
    followers <- N<User>(user_id)::Out<Follows>
    posts <- followers::Out<Created>::RANGE(0, 40)
    RETURN posts::{
        post: content,
        creatorID: _::In<Created>::ID,
    }

