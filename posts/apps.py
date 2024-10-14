from django.apps import AppConfig
from django.conf import settings

client = None
embedding_fn = None


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "posts"

    def ready(self):
        from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, exceptions, model

        global client, embedding_fn

        connections.connect(
            uri=settings.ZILLIZ_PUBLIC_ENDPOINT, token=settings.ZILLIZ_API_KEY, db_name="db_ab4310029252ada"
        )

        fields = [
            FieldSchema("pk", DataType.VARCHAR, is_primary=True, max_length=255),
            FieldSchema("vector", DataType.FLOAT_VECTOR, dim=768),
        ]
        schema = CollectionSchema(
            fields,
            enable_dynamic_field=True,
        )

        client = Collection("iih_tangerine_post", schema)

        try:
            client.create_index(
                field_name="vector",
                index_params={
                    "Index_type": "AUTOINDEX",
                    "Metric_type": "COSINE",
                },
            )
        except exceptions.SchemaNotReadyException:
            pass

        embedding_fn = model.DefaultEmbeddingFunction()
