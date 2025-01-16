from rest_framework import serializers
from .models import User, Transaction, Book

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username', 'date_of_membership', 'is_active']
    read_only_fields = ['date_of_membership']


class BookSerializer(serializers.ModelSerializer):
  class Meta:
    model = Book
    fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available', 'created_at', 'updated_at']
    read_only_fields = ['created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)

  class Meta:
    model = Transaction
    fields = ['id', 'user', 'username', 'transaction_type', 'transaction_date', 'due_date']
    read_only_fields = ['transaction_date']