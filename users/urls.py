from django.urls import path
from .views import UserSearchView, FriendRequestView, accept_friend_request, reject_friend_request, list_friends, list_pending_requests
from .views_auth import UserSignupView, CustomTokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('accept-friend-request/', accept_friend_request, name='accept-friend-request'),
    path('reject-friend-request/', reject_friend_request, name='reject-friend-request'),
    path('friends/', list_friends, name='list-friends'),
    path('pending-requests/', list_pending_requests, name='list-pending-requests'),
]
