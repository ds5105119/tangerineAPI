try:
    from rest_framework.pagination import PageNumberPagination
except ImportError:
    raise ImportError(
        "django-rest-framework needs to be added to INSTALLED_APPS."
    )


class UserPagination(PageNumberPagination):
    """
    Pagination for UserViewSet
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 20
