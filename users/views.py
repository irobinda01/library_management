from django.db import models
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Transaction, Book
from .serializers import UserSerializer, TransactionSerializer, BookSerializer
from datetime import datetime, timedelta

# Create your views here.

#USER VIEWS
class UserListCreateAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserDetailAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=204)
    
class BorrowingHistoryAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        transactions = Transaction.objects.filter(user=user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    

# BOOKS VIEWS
class BookListCreateAPIView(APIView):
  #permission_classes = [IsAuthenticated]

  def get(self, request):
    books = Book.objects.all()

    # Filtering based on `copies_available`
    copies_available = request.query_params.get('copies_available')
    if copies_available is not None:
      books = books.filter(copies_available=copies_available)

    # Searching based on `title`, `author`, or `isbn`
    search_query = request.query_params.get('search')
    if search_query:
      books = books.filter(
        models.Q(title__icontains=search_query) |
        models.Q(author__icontains=search_query) |
        models.Q(isbn__icontains=search_query)
      )

    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

  def post(self, request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


class BookDetailAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request, pk):
    book = get_object_or_404(Book, pk=pk)
    serializer = BookSerializer(book)
    return Response(serializer.data)

  def put(self, request, pk):
    book = get_object_or_404(Book, pk=pk)
    serializer = BookSerializer(book, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

  def delete(self, request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return Response(status=204)


class BookCheckoutAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user

    # Check if user already has this book checked out
    existing_checkout = Transaction.objects.filter(
      user=user,
      book=book,
      transaction_type=Transaction.CHECKOUT
    ).exists()

    if existing_checkout:
      return Response(
          {'error': 'You already have this book checked out'},
          status=status.HTTP_400_BAD_REQUEST
      )

    if book.copies_available <= 0:
      return Response(
          {'error': 'No copies available'},
          status=status.HTTP_400_BAD_REQUEST
      )

    # Create checkout transaction
    due_date = datetime.now().date() + timedelta(days=14)
    Transaction.objects.create(
      user=user,
      book=book,
      transaction_type=Transaction.CHECKOUT,
      due_date=due_date
    )

    # Update book copies
    book.copies_available -= 1
    book.save()

    return Response({'status': 'Book checked out successfully'})


class BookReturnAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user

    # Check if user has this book checked out
    checkout = Transaction.objects.filter(
      user=user,
      book=book,
      transaction_type=Transaction.CHECKOUT
    ).first()

    if not checkout:
      return Response(
        {'error': 'You have not checked out this book'},
        status=status.HTTP_400_BAD_REQUEST
      )

    # Create return transaction
    Transaction.objects.create(
      user=user,
      book=book,
      transaction_type=Transaction.RETURN
    )

    # Update book copies
    book.copies_available += 1
    book.save()

    return Response({'status': 'Book returned successfully'})