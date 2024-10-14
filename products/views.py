from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import User

from .models import Product
from .permissions import ProductPermission
from .serializers import ProductCreateUpdateSerializer, ProductRetrieveSerializer


class UserProductPagination(CursorPagination):
    """
    Pagination for Product views
    """

    page_size = 10
    ordering = "-created_at"
    page_size_query_param = None
    max_page_size = 10


class LatestProductsViaHandleViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    GET /products/latest/{handle}: return latest product via user
    /products/latest/{handle}/?page=2: return latest product via user and pagination
    """

    serializer_class = ProductRetrieveSerializer
    pagination_class = UserProductPagination
    permission_classes = (AllowAny,)
    lookup_field = "user"
    lookup_url_kwarg = "handle"
    lookup_value_regex = r"[a-z0-9_.]+"

    def get_queryset(self):
        handle = self.kwargs.get("handle")
        user = get_object_or_404(User, handle=handle)
        return Product.objects.filter(user=user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecommendProductsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    GET /products/recommend: return recommended products
    """

    serializer_class = ProductRetrieveSerializer
    pagination_class = UserProductPagination
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # Random 10 products for example
        # Implement recommendation logic later
        return Product.objects.all().order_by("?")[:10]


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /product/p/: Create a new product via data
    GET /product/p/: List all products
    GET /product/p/{uuid}: Get product[uuid] detail
    PUT /product/p/{uuid}: Update product[uuid]
    DELETE /product/p/{uuid}: Delete product[uuid]
    """

    permission_classes = (ProductPermission,)
    queryset = Product.objects.all()
    lookup_field = "uuid"
    pagination_class = UserProductPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductRetrieveSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise serializers.ValidationError("로그인이 필요합니다.")
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
