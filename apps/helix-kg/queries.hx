QUERY insert_entity(entity_name_in: String) =>
    node <- AddN<Entity>({ entity_name: entity_name_in })
    RETURN node

QUERY get_entity(entity_name_in: String) =>
    node <- N<Entity>({entity_name: entity_name_in})
    RETURN node

QUERY insert_relationship(
    from_entity_label: String,
    to_entity_label: String,
    edge_name_in: String
) =>
    from_entity <- N<Entity>({entity_name: from_entity_label}) // TODO: need to handle multiple hits here too
    to_entity <- N<Entity>({entity_name: to_entity_label}) // TODO: need to handle multiple hits here too
    e <- AddE<Relationship>({ edge_name: edge_name_in })::From(from_entity)::To(to_entity)
    RETURN e
