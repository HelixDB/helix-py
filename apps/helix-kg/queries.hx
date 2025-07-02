QUERY insert_entity(label: String) =>
    node <- AddN<Entity>({ label: label })
    RETURN node

QUERY get_entity(label: String) =>
    node <- N<Entity>::WHERE(_::{label}::EQ(label))
    RETURN node

//QUERY delete_entity(label: String) =>

QUERY insert_relationship(
from_entity_label: String,
to_entity_label: String,
label: String) =>
    from_entity <- N<Entity>::WHERE(_::{label}::EQ(from_entity_label))
    to_entity <- N<Entity>::WHERE(_::{label}::EQ(to_entity_label))
    e <- AddE<Relationship>::From(from_entity)::To(to_entity)
    RETURN e

