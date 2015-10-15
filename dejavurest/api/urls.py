from django.conf.urls import include, url
from api import views as api_views

urlpatterns = [
    url(r'^list$', api_views.ListObjects.as_view(), name='list'),
    url(r'^add_record', api_views.RecordUploadView.as_view()),
	url(r'^match', api_views.VerifyObject.as_view()),
    url(r'^song_repo', api_views.DBCleanupView.as_view())
    
]

