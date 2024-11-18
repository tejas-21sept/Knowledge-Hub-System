from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class ModelBaseInfo(models.Model):
    """Base class for storing common fields"""

    created_at = models.DateTimeField(auto_now=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Books(ModelBaseInfo):
    """DB table for storing books details"""

    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255, unique=True, null=True, blank=True)
    publication_year = models.CharField(max_length=4, null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    available_copies = models.IntegerField()

    def __str__(self):
        return self.title


class Author(ModelBaseInfo):
    """Db Table for storing Authors details"""

    full_name = models.CharField(max_length=255)
    dob = models.DateTimeField(null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    book = models.ManyToManyField("Books", related_name="books_author")

    def __str__(self):
        return self.full_name


class UserManager(BaseUserManager):
    """Handles user creation"""

    def create_user(self, email, name, role, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email, name, role="admin", password=password, **extra_fields
        )


class User(AbstractBaseUser, ModelBaseInfo):
    """Custom User Model"""

    ROLE_CHOICES = [
        ("user", "Library User"),
        ("staff", "Library Staff"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email


class MembershipType(ModelBaseInfo):
    """DB model for membership types"""

    title = models.CharField(max_length=255)
    price = models.FloatField(unique=True)

    def __str__(self):
        return self.title


class Borrower(ModelBaseInfo):
    """DB table for storing borowwers details"""

    user = models.OneToOneField(
        "User",
        related_name="borrower_user",
        on_delete=models.CASCADE,
    )

    membership_type = models.OneToOneField(
        "MembershipType",
        related_name="borrower_membership",
        on_delete=models.CASCADE,
    )
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    borrowed_books_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.name


class BorrowedBook(ModelBaseInfo):
    """Tracks each book borrowed by a borrower with borrow and return dates"""

    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.book.title
