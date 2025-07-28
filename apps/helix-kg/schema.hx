V::Embedding {
    vec: [F64],
}

N::Entity {
    INDEX entity_name: String,
}

E::Chunk {
    From: Entity,
    To: Embedding,
    Properties: {
    }
}

E::Relationship {
    From: Entity,
    To: Entity,
    Properties: {
        edge_name: String,
    }
}

