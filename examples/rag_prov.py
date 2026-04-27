from provo import ProvOntologyGraph

prov = ProvOntologyGraph(
    default_namespace="https://example.org/rag-ingestion#",
    default_namespace_abbreviation="rag",
    lang="en",
)

# -------------------------
# Agents
# -------------------------
script = prov.add_agent("rag-ingestion-script", label="RAG ingestion script")
developer = prov.add_agent("developer", label="Pipeline developer")
unstructured_agent = prov.add_agent(
    "unstructured-partitioner", label="Unstructured partitioner"
)
embedder_agent = prov.add_agent(
    "scads-embedding-service", label="SCADS embedding service"
)
milvus_agent = prov.add_agent("milvus-client", label="Milvus client")

script.acted_on_behalf_of(developer)

# -------------------------
# Global entities
# -------------------------
kb_root = prov.add_entity("knowledge-base-dir", label="knowledge_base directory")
out_root = prov.add_entity(
    "unstructured-outputs-dir", label="unstructured_outputs directory"
)
collection_entity = prov.add_entity(
    "my-rag-collection", label="Milvus collection: my_rag_collection"
)

# -------------------------
# Activity: ensure collection
# -------------------------
ensure_collection = prov.add_activity(
    "ensure-collection", label="Ensure Milvus collection exists"
)
ensure_collection.used(collection_entity)
ensure_collection.was_associated_with(milvus_agent)
ensure_collection.was_associated_with(script)

prepared_collection = prov.add_entity(
    "prepared-collection", label="Prepared Milvus collection"
)
prepared_collection.was_generated_by(ensure_collection)
prepared_collection.was_derived_from(collection_entity)
prepared_collection.was_attributed_to(milvus_agent)

# -------------------------
# Per-file example
# -------------------------
source_pdf = prov.add_entity("source-doc-1", label="Input document")
source_pdf.was_attributed_to(developer)

partition_activity = prov.add_activity(
    "partition-doc-1", label="Partition input document"
)
partition_activity.used(source_pdf)
partition_activity.used(kb_root)
partition_activity.was_associated_with(unstructured_agent)
partition_activity.was_associated_with(script)

partitioned_elements = prov.add_entity(
    "partitioned-elements-doc-1", label="Partitioned elements"
)
partitioned_elements.was_generated_by(partition_activity)
partitioned_elements.was_derived_from(source_pdf)
partitioned_elements.was_attributed_to(unstructured_agent)

write_json_activity = prov.add_activity(
    "write-json-doc-1", label="Write extracted elements JSON"
)
write_json_activity.used(partitioned_elements)
write_json_activity.used(out_root)
write_json_activity.was_associated_with(script)

elements_json = prov.add_entity("elements-json-doc-1", label="Extracted elements JSON")
elements_json.was_generated_by(write_json_activity)
elements_json.was_derived_from(partitioned_elements)
elements_json.was_attributed_to(script)

embed_activity = prov.add_activity("embed-doc-1", label="Embed extracted texts")
embed_activity.used(partitioned_elements)
embed_activity.was_associated_with(embedder_agent)
embed_activity.was_associated_with(script)

embeddings_entity = prov.add_entity(
    "embeddings-doc-1", label="Embeddings for extracted texts"
)
embeddings_entity.was_generated_by(embed_activity)
embeddings_entity.was_derived_from(partitioned_elements)
embeddings_entity.was_attributed_to(embedder_agent)

insert_activity = prov.add_activity("insert-doc-1", label="Insert vectors into Milvus")
insert_activity.used(partitioned_elements)
insert_activity.used(embeddings_entity)
insert_activity.used(prepared_collection)
insert_activity.was_associated_with(milvus_agent)
insert_activity.was_associated_with(script)
insert_activity.was_informed_by(embed_activity)

indexed_records = prov.add_entity(
    "indexed-records-doc-1", label="Indexed Milvus records"
)
indexed_records.was_generated_by(insert_activity)
indexed_records.was_derived_from(partitioned_elements)
indexed_records.was_derived_from(embeddings_entity)
indexed_records.was_attributed_to(milvus_agent)

updated_collection = prov.add_entity(
    "updated-collection-doc-1", label="Updated Milvus collection state"
)
updated_collection.was_generated_by(insert_activity)
updated_collection.was_derived_from(prepared_collection)
updated_collection.was_derived_from(indexed_records)

analysis_activity = prov.add_activity(
    "analyze-outputs", label="Analyze unstructured outputs directory"
)
analysis_activity.used(out_root)
analysis_activity.used(elements_json)
analysis_activity.was_associated_with(script)

analysis_df_entity = prov.add_entity(
    "analysis-dataframe", label="Output analysis dataframe"
)
analysis_df_entity.was_generated_by(analysis_activity)
analysis_df_entity.was_derived_from(elements_json)
analysis_df_entity.was_attributed_to(script)


prov.export_as_mermaid_flowchart("ex.md")
