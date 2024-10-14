try:
    from rest_framework.pagination import CursorPagination
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class ChatRoomPagination(CursorPagination):
    """
    Pagination for Room
    """

    page_size = 20
    page_size_query_param = "page_size"
    ordering = "-updated_at"
    max_page_size = 20


class ChatMemberPagination(CursorPagination):
    """
    Pagination for User
    """

    page_size = 20
    page_size_query_param = "page_size"
    ordering = "-updated_at"
    max_page_size = 20


class ChatMessagePagination(CursorPagination):
    """
    Pagination for User
    """

    page_size = 50
    page_size_query_param = "page_size"
    ordering = "-created_at"
    max_page_size = 50
