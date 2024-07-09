from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationListCreateView, OrganisationDetailView,  AddUserToOrganisationView

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('api/users/<uuid:userId>', UserDetailView.as_view(), name='user-detail'),
    path('api/organisations', OrganisationListCreateView.as_view(), name='organisation-list'),
    path('api/organisations/<uuid:orgId>', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('api/organisations/<uuid:orgId>/users', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
    path('api/auth/register', RegisterView.as_view(), name='register3'),
    path('api/auth/login', LoginView.as_view(), name='login'),
]
