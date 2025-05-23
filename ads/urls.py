from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ads', views.AdViewSet)
router.register(r'proposals', views.ExchangeProposalViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('ad_list', views.search_ads, name='ad_list'),
    path('create/', views.create_ad, name='create_ad'),
    path('<int:pk>/', views.ad_detail, name='ad_detail'),
    path('<int:pk>/edit/', views.edit_ad, name='edit_ad'),
    path('<int:pk>/delete/', views.delete_ad, name='delete_ad'),
    path('<int:pk>/propose/', views.send_proposal, name='send_proposal'),
    path('proposals/', views.exchange_proposals_list, name='proposal_list'),
    path('proposals/<int:pk>/', views.proposal_detail, name='proposal_detail'),
    path('proposals/<int:pk>/update/', views.update_exchange_proposal_status, name='update_proposal_status'),

    # REST API
    path('api/', include(router.urls)),
]