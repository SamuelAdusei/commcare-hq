from __future__ import absolute_import
from __future__ import unicode_literals
from django.conf.urls import url

from custom.ucla.views import task_creation

urlpatterns = [
    url(r'ucla-task-creation/(?P<app_id>[\w-]+)/modules-(?P<module_id>[\w-]+)/forms-(?P<form_id>[\w-]+)/$',
        task_creation, name='ucla_task_creation')
]
