from django.urls import path

from modules.projects.adapters.api.client_collection_view import ClientCollectionView
from modules.projects.adapters.api.project_collection_view import ProjectCollectionView

urlpatterns = [
    path("clients", ClientCollectionView.as_view(), name="client-collection"),
    path("projects", ProjectCollectionView.as_view(), name="project-collection"),
]
