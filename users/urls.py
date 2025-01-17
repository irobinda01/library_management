from django.urls import path
from .views import (
  UserListCreateAPIView, 
  UserDetailAPIView, 
  BorrowingHistoryAPIView,
  BookListCreateAPIView,
  BookDetailAPIView,
  BookCheckoutAPIView,
  BookReturnAPIView,
  LoginView
)

urlpatterns = [
    path('login', LoginView.as_view(), name='user-login'),
    path('users', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<int:pk>/borrowing-history', BorrowingHistoryAPIView.as_view(), name='user-borrowing-history'),
    path('books', BookListCreateAPIView.as_view(), name='book-list-create'),
    path('books/<int:pk>', BookDetailAPIView.as_view(), name='book-detail'),
    path('books/<int:pk>/checkout', BookCheckoutAPIView.as_view(), name='book-checkout'),
    path('books/<int:pk>/return', BookReturnAPIView.as_view(), name='book-return'),
]
