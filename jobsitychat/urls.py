from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include
from chat import views

handler404 = views.error404
handler500 = views.error500

urlpatterns = [
    #path('', include('chat.urls', namespace='chat')),
    path('admin/', admin.site.urls),
    path('jobsitychat/', include('chat.urls', namespace='chat')),
]

