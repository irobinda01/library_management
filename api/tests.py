from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
from .models import Book, Transaction
import json

# Create your tests here.

User = get_user_model()

class BookTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='9780123456789',
            published_date='2023-01-01',
            copies_available=5
        )

        # URLs
        self.books_url = reverse('book-list')
        self.book_detail_url = reverse('book-detail', args=[self.book.id])

    def test_create_book(self):
        """Test creating a new book"""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9780987654321',
            'published_date': '2023-01-01',
            'copies_available': 3
        }
        response = self.client.post(self.books_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.get(isbn='9780987654321').title, 'New Book')

    def test_get_book_list(self):
        """Test retrieving a list of books"""
        response = self.client.get(self.books_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_book_detail(self):
        """Test retrieving a specific book"""
        response = self.client.get(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')

    def test_update_book(self):
        """Test updating a book"""
        data = {
            'title': 'Updated Book',
            'author': 'Test Author',
            'isbn': '9780123456789',
            'published_date': '2023-01-01',
            'copies_available': 5
        }
        response = self.client.put(self.book_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Book.objects.get(id=self.book.id).title, 'Updated Book')

    def test_delete_book(self):
        """Test deleting a book"""
        response = self.client.delete(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_search_books(self):
        """Test searching books"""
        response = self.client.get(f"{self.books_url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book')

class TransactionTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='9780123456789',
            published_date='2023-01-01',
            copies_available=5
        )

        # URLs
        self.checkout_url = reverse('book-checkout', args=[self.book.id])
        self.return_url = reverse('book-return-book', args=[self.book.id])

    def test_checkout_book(self):
        """Test checking out a book"""
        response = self.client.post(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, 4)
        self.assertTrue(Transaction.objects.filter(
            book=self.book,
            user=self.user,
            transaction_type=Transaction.CHECKOUT
        ).exists())

    def test_checkout_unavailable_book(self):
        """Test checking out a book with no copies available"""
        self.book.copies_available = 0
        self.book.save()
        response = self.client.post(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_already_borrowed(self):
        """Test checking out a book that's already checked out"""
        # First checkout
        self.client.post(self.checkout_url)
        # Second checkout attempt
        response = self.client.post(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book(self):
        """Test returning a book"""
        # First checkout the book
        self.client.post(self.checkout_url)
        initial_copies = self.book.copies_available
        
        # Then return it
        response = self.client.post(self.return_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, initial_copies + 1)
        self.assertTrue(Transaction.objects.filter(
            book=self.book,
            user=self.user,
            transaction_type=Transaction.RETURN
        ).exists())

    def test_return_not_borrowed_book(self):
        """Test returning a book that wasn't checked out"""
        response = self.client.post(self.return_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # URLs
        self.users_url = reverse('user-list')
        self.user_detail_url = reverse('user-detail', args=[self.user.id])
        self.borrowing_history_url = reverse('user-borrowing-history', args=[self.user.id])

    def test_create_user(self):
        """Test creating a new user"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.users_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_get_user_list(self):
        """Test retrieving a list of users"""
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_user_detail(self):
        """Test retrieving a specific user"""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_user(self):
        """Test updating a user"""
        data = {
            'username': 'testuser',
            'email': 'updated@example.com'
        }
        response = self.client.patch(self.user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.user.id).email, 'updated@example.com')

    def test_get_borrowing_history(self):
        """Test retrieving user's borrowing history"""
        # Create a book and some transactions
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='9780123456789',
            published_date='2023-01-01',
            copies_available=5
        )
        Transaction.objects.create(
            user=self.user,
            book=book,
            transaction_type=Transaction.CHECKOUT
        )
        
        response = self.client.get(self.borrowing_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ModelTests(TestCase):
    def test_book_str_representation(self):
        """Test the string representation of Book model"""
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='9780123456789',
            published_date='2023-01-01',
            copies_available=5
        )
        self.assertEqual(str(book), 'Test Book by Test Author')

    def test_transaction_str_representation(self):
        """Test the string representation of Transaction model"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='9780123456789',
            published_date='2023-01-01',
            copies_available=5
        )
        transaction = Transaction.objects.create(
            user=user,
            book=book,
            transaction_type=Transaction.CHECKOUT
        )
        self.assertEqual(
            str(transaction),
            'Checkout - Test Book by testuser'
        )