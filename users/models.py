from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from isbnlib import is_isbn10, is_isbn13

# Create your models here.
class User(AbstractUser):
  date_of_membership = models.DateField(auto_now_add=True)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ['-date_joined']

  def __str__(self):
    return self.username
  

class Book(models.Model):
  title = models.CharField(max_length=200)
  author = models.CharField(max_length=200)
  isbn = models.CharField(max_length=13, unique=True)
  published_date = models.DateField()
  copies_available = models.IntegerField(validators=[MinValueValidator(0)])
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['title']

  def clean(self):
    if not (is_isbn10(self.isbn) or is_isbn13(self.isbn)):
      raise ValidationError({'isbn': 'Invalid ISBN number'})

  def __str__(self):
    return f"{self.title} by {self.author}"
  

class Transaction(models.Model):
  CHECKOUT = 'CO'
  RETURN = 'RE'
  TRANSACTION_TYPES = [(CHECKOUT, 'Checkout'), (RETURN, 'Return')]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)
  transaction_date = models.DateTimeField(auto_now_add=True)
  due_date = models.DateField(null=True, blank=True)

  class Meta:
    ordering = ['-transaction_date']

  def __str__(self):
    return f"{self.user.username}"