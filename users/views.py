from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from django.core.cache import cache
from datetime import timedelta

class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        queryset = User.objects.all()
        keyword = self.request.query_params.get('keyword', None)
        
        if keyword:
            email_match = User.objects.filter(email=keyword.lower())
            if email_match.exists():
                return email_match
            queryset = queryset.filter(name__icontains=keyword)
        
        return queryset

class FriendRequestView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        from_user = request.user

        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'{from_user.id}_friend_requests'
        recent_requests = cache.get(cache_key, [])

        if len(recent_requests) >= 3 and (timezone.now() - recent_requests[-1]) < timedelta(minutes=1):
            return Response({'error': 'Too many friend requests. Try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()

        recent_requests.append(timezone.now())
        cache.set(cache_key, recent_requests[-3:], timeout=60)

        return Response({'status': 'Friend request sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_friend_request(request):
    request_id = request.data.get('request_id')
    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    except FriendRequest.DoesNotExist:
        return Response({'error': 'Friend request does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.status != 'pending':
        return Response({'error': 'Invalid friend request'}, status=status.HTTP_400_BAD_REQUEST)

    friend_request.status = 'accepted'
    friend_request.save()

    return Response({'status': 'Friend request accepted'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_friend_request(request):
    request_id = request.data.get('request_id')
    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    except FriendRequest.DoesNotExist:
        return Response({'error': 'Friend request does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.status != 'pending':
        return Response({'error': 'Invalid friend request'}, status=status.HTTP_400_BAD_REQUEST)

    friend_request.status = 'rejected'
    friend_request.save()

    return Response({'status': 'Friend request rejected'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    # Get all accepted friend requests for the authenticated user
    accepted_requests = FriendRequest.objects.filter(to_user=request.user, status='accepted')
    
    # Get the users who sent the accepted friend requests
    friends = [request.user]  # Start with the authenticated user
    for request in accepted_requests:
        friends.append(request.from_user)
    
    # Serialize the friends and return the response
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_requests(request):
    pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
    serializer = FriendRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)
