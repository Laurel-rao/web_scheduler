import datetime

import django_filters

# Create your views here.
from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

# from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from schedulers.models import JobLog
from schedulers.views import utc_to_utc8


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 1000


class CustomJobLogSerializer(serializers.ModelSerializer):
    datetime = serializers.SerializerMethodField()

    def get_datetime(self, obj):
        return utc_to_utc8(obj.datetime)

    class Meta:
        model = JobLog
        fields = "__all__"


class JobLogViewSet(viewsets.ModelViewSet):
    model = JobLog
    pagination_class = BasePagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, ]
    filterset_fields = ('level', 'job_id', "type")
    serializer_class = CustomJobLogSerializer

    def get_queryset(self):
        # qs = super().get_queryset()  # 调用父类方法
        return JobLog.objects.filter().order_by('-datetime')
