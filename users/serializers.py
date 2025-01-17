from rest_framework import serializers
from .models import User, Transaction, Book

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'password', 'date_of_membership', 'is_active']
    read_only_fields = ['date_of_membership']

  def create(self, validated_data):
    password = validated_data.pop('password', None)
    instance = self.Meta.model(**validated_data)
    if password is not None:
      instance.set_password(password)
    instance.save()
    return instance


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