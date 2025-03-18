from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from .serializers import TaskSerializer
from todo.models import Task
from .paginations import LargeResultsSetPagination
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class TaskModelViewSet(viewsets.ModelViewSet):
    """getting a list of tasks and creating new task"""

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = TaskSerializer
    pagination_class = LargeResultsSetPagination
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["complete"]
    search_fields = ["title"]
    ordering_fields = ["created_date"]
