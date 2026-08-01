from django.urls import path

from modules.companies.adapters.api.company_collection_view import CompanyCollectionView

urlpatterns = [
    path("companies", CompanyCollectionView.as_view(), name="company-collection"),
]
