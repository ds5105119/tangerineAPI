try:
    from rest_framework.pagination import PageNumberPagination
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class ChatRoomPagination(PageNumberPagination):
    """
    Pagination for Room
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 20


class ChatMemberPagination(PageNumberPagination):
    """
    Pagination for User
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 20


class ChatMessagePagination(PageNumberPagination):
    """
    Pagination for User
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 50
