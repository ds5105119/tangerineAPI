from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from posts.models import Category, Post
from accounts.models import (User)

"""
@registry.register_document
class PostDocument(Document):
    user = fields.ObjectField(
        properties={
            "handle": fields.TextField(),
            "username": fields.TextField(),
        }
    )
    category = fields.ObjectField(
        properties={
            "name": fields.TextField(),
        }
    )

    class Index:
        # Name of the Elasticsearch index
        name = "posts"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Post  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = ["mdx", "text"]
        related_models = [User, Category]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Configure how the index should be refreshed after an update.
        # See Elasticsearch documentation for supported options:
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/docs-refresh.html
        # This per-Document setting overrides settings.ELASTICSEARCH_DSL_AUTO_REFRESH.
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000
"""