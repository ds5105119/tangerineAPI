from rest_framework import permissions, viewsets

from .models import Report
from .permissions import IsAdminUser, IsOwnerOrReadOnly
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_permissions(self):
        if self.action in ["create", "list"]:
            self.permission_classes = [IsOwnerOrReadOnly]
        elif self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
