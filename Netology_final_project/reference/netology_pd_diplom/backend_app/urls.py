from django.urls import path, include

app_name = 'backend'
urlpatterns = [
    path('', include('backend.api.urls')),
]
