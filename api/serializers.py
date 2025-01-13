from rest_framework import serializers
from .models import Book, User, Transaction

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_of_membership', 'is_active']
        read_only_fields = ['date_of_membership']

class TransactionSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'book', 'book_title', 'username', 'transaction_type', 'transaction_date', 'due_date']
        read_only_fields = ['transaction_date']