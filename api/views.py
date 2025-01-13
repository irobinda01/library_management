from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, User, Transaction
from .serializers import BookSerializer, UserSerializer, TransactionSerializer
from datetime import datetime, timedelta

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['copies_available']
    search_fields = ['title', 'author', 'isbn']

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        book = self.get_object()
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

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        book = self.get_object()
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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True)
    def borrowing_history(self, request, pk=None):
        user = self.get_object()
        transactions = Transaction.objects.filter(user=user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)