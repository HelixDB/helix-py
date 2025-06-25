V::Embedding {
    label: String,
    vec: [F64]
}

N::Entity {
    label: String
}

E::Relationship {
    From: Entity,
    To: Entity,
    Properties: {
        label: String
    }
}

