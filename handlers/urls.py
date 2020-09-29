from django.urls import path,re_path
from . import views
from .views import HandlersListView, RegisterHandlerView

urlpatterns = [
    path("handlers", HandlersListView.as_view(), name="handlers"),
    path("add-handler", RegisterHandlerView.as_view(), name="add_handler"),
    path("add-handler/handler/<int:handler_id>", RegisterHandlerView.as_view(), name="edit_handler")
]
