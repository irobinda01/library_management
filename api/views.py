from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import User, Book, Transaction
from .serializers import UserSerializer, BookSerializer, TransactionSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Book.objects.all()
        available = self.request.query_params.get('available')
        if available:
            queryset = queryset.filter(copies_available__gt=0)
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__icontains=author)
        isbn = self.request.query_params.get('isbn')
        if isbn:
            queryset = queryset.filter(isbn__icontains=isbn)
        return queryset

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        book = self.get_object()
        user = request.user
        if book.copies_available > 0:
            transaction = Transaction.objects.create(user=user, book=book)
            book.copies_available -= 1
            book.save()
            return Response({'message': 'Book checked out successfully'}, status=status.HTTP_200_OK)
        return Response({'message': 'No copies available'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        book = self.get_object()
        user = request.user
        try:
            transaction = Transaction.objects.get(user=user, book=book, return_date__isnull=True)
            transaction.return_date = timezone.now()
            transaction.save()
            book.copies_available += 1
            book.save()
            return Response({'message': 'Book returned successfully'}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({'message': 'No active checkout found for this book'}, status=status.HTTP_400_BAD_REQUEST)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)