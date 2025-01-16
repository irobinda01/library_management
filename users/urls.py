from django.urls import path
from .views import UserListCreateAPIView, UserDetailAPIView, BorrowingHistoryAPIView

urlpatterns = [
    path('users', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<int:pk>/borrowing-history', BorrowingHistoryAPIView.as_view(), name='user-borrowing-history'),
]
