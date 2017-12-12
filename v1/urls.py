from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from v1.api import host_api
from v1.api import script_api

urlpatterns = [
    url(r'^v1/machines/add$', host_api.AddOneHosts.as_view()),
    url(r'^v1/users/do$', host_api.UsersProfile.as_view()),
    url(r'^v1/script/execute$', script_api.ToolExecute.as_view()),
    url(r'^v1/return/log$',script_api.ReturnLog.as_view()),
    url(r'^v1/app/execute$',script_api.AppExecuteApi.as_view()),
    url(r'^v1/task/execute$',script_api.TaskExecute.as_view()),
	url(r'^v1/api/download$',script_api.DownloadApi.as_view()),
	url(r'^v1/api/execute$',script_api.ExecuteToolApi.as_view()),
	url(r'^v1/users/ssh$',host_api.UsersPostSsh.as_view()),
	url(r'v1/users/get$',host_api.UsersGetList.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
