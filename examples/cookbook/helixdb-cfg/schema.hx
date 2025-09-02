N::User {
    name: String,
    age: U32,
    email: String,
    created_at: Date,
    updated_at: Date
}

N::Post {
    content: String,
    created_at: Date,
    updated_at: Date
}

E::Follows {
    From: User,
    To: User,
    Properties: {
        since: Date
    }
}

E::Created {
    From: User,
    To: Post,
    Properties: {
        created_at: Date
    }
}

