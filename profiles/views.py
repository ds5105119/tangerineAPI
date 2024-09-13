from profiles.models import Profile
from profiles.serializers import ProfileExternalSerializer

try:
    from django.db.models import Q
    from django.shortcuts import get_object_or_404
    from rest_framework import viewsets, status
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework.pagination import PageNumberPagination
    from rest_framework.permissions import AllowAny
    from rest_framework.views import APIView
except ImportError:
    raise ImportError(
        "django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS."
    )


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 20


class PublicProfileDetailView(APIView):
    """
    POST /profiles/detail/: handle을 통해 해당 Profile을 반환.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        handle = request.data.get("handle")
        if not handle:
            return Response(
                {"error": "Handle is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        profile = get_object_or_404(
            Profile.objects.select_related("user"), user__handle=handle
        )
        serializer = ProfileExternalSerializer(profile)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /profiles/{handle}/: handle을 통해 해당 Profile을 반환.
    GET /profiles/: User의 updated_at 순서로 정렬된 50개씩 페이지네이션된 Profile 리스트 반환.
    """

    permission_classes = [AllowAny]
    serializer_class = ProfileExternalSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Profile.objects.select_related("user").order_by("-user__updated_at")

    def retrieve(self, request, *args, **kwargs):
        handle = kwargs.get("pk")
        queryset = self.get_queryset()
        profile = get_object_or_404(queryset, user__handle=handle)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


def ProfileViewSet2():
    """
    GET /profiles/search/?q={query}: User의 handle을 검색하여 Profile들을 updated_at 순서로 정렬하고 20개씩 페이지네이션하여 반환
    """
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        queryset = self.get_queryset().filter(user__handle__icontains=query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
