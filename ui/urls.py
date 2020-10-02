
from django.urls import path, re_path
from ui import views

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),
    path('', views.index, name='home'),
    path('graph', views.graph_data, name='graph')
]
