from profiles.models import Profile
from profiles.serializers import ProfileExternalSerializer

try:
    from django.shortcuts import get_object_or_404
    from rest_framework import status, viewsets
    from rest_framework.pagination import PageNumberPagination
    from rest_framework.permissions import AllowAny
    from rest_framework.response import Response
    from rest_framework.views import APIView
except ImportError:
    raise ImportError("django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS.")


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
            return Response({"error": "Handle is required"}, status=status.HTTP_400_BAD_REQUEST)

        profile = get_object_or_404(Profile.objects.select_related("user"), user__handle=handle)
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
