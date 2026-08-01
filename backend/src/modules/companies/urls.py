from django.urls import path

from modules.companies.adapters.api.company_collection_view import CompanyCollectionView
from modules.companies.adapters.api.invitation_accept_view import InvitationAcceptView
from modules.companies.adapters.api.invitation_collection_view import InvitationCollectionView
from modules.companies.adapters.api.invitation_detail_view import InvitationDetailView
from modules.companies.adapters.api.membership_collection_view import MembershipCollectionView
from modules.companies.adapters.api.membership_detail_view import MembershipDetailView

urlpatterns = [
    path("companies", CompanyCollectionView.as_view(), name="company-collection"),
    path("invitations", InvitationCollectionView.as_view(), name="invitation-collection"),
    path("invitations/accept", InvitationAcceptView.as_view(), name="invitation-accept"),
    path(
        "invitations/<uuid:invitation_id>",
        InvitationDetailView.as_view(),
        name="invitation-detail",
    ),
    path("members", MembershipCollectionView.as_view(), name="membership-collection"),
    path(
        "members/<uuid:membership_id>",
        MembershipDetailView.as_view(),
        name="membership-detail",
    ),
]
