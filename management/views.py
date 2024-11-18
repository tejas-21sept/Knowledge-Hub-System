from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_304_NOT_MODIFIED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Books, User
from .serializers import BooksSerializer, UserSignupSerializer
from rest_framework.decorators import action


class SignupView(APIView):
    """Handles user creation"""

    def post(self, request, *args, **kwargs):
        try:
            print(f"\nrequest.data - {request.data} \n")
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"msg": serializer.data},
                    status=HTTP_201_CREATED,
                )
            return Response(
                {
                    "error": f"Invalid data - {serializer.errors}.",
                    "status": HTTP_400_BAD_REQUEST,
                },
            )
        except Exception as e:
            return Response(
                {
                    "error": f"Something has happened - {e}.",
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SignoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token", None)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response(
                {
                    "msg": "user loggged out successfully.",
                },
                status=HTTP_304_NOT_MODIFIED,
            )
        except Exception as e:
            return Response(
                {
                    "error": f"Something has happened - {e}.",
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ForgetPasswordView(APIView):
    """Handles the forgetted password"""

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email", None)
            if email:
                try:
                    user = User.objects.get(email=email)
                    token = PasswordResetTokenGenerator().make_token(user)
                    reset_url = request.build_absolute_uri(
                        reverse(
                            "password_reset_confirm",
                            args=[user.pk, token],
                        )
                    )
                    print(f"\n reset_url - {reset_url}\n")
                    # send_mail(
                    #     "Password Reset Request",
                    #     f"Use the following link to reset your password: {reset_url}",
                    #     "no-reply@yourdomain.com",
                    #     [email],
                    # )
                    return Response(
                        {"message": "Password reset link sent"},
                        status=HTTP_200_OK,
                    )
                except User.DoesNotExist:
                    return Response(
                        {"error": "User not found"}, status=HTTP_400_BAD_REQUEST
                    )

            return Response({"error": "Invalid email is."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": f"Something went wrong - {e}"},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        new_password = request.data.get("new_password", None)
        print(f"\nnew_password - {new_password} \n")
        if not new_password:
            return Response(
                {"error": "New password is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=uid)
            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "Password reset successful"}, status=HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid or expired token"},
                    status=HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)


# 1. User Management
# Role-Based Access Control: Ensure different levels of access (e.g., admin, staff, user) with permissions assigned accordingly.


# 2. Book Management
# Add New Books: Allow admins/staff to add books with details like title, author, genre, ISBN, publication year, and available copies.
# Edit Book Details: Allow updates to book information if needed.
# Delete/Archive Books: Remove or archive books that are no longer available.
# View All Books: Display a list of all books in the library with pagination and search options.
# Search Books: Provide search filters like title, author, genre, and publication year.
# Book Availability: Check if a book is available or reserved and view the number of available copies.
# Manage Book Copies: Update the count of available copies, add new copies, or mark them as unavailable if lost or damaged.


class BooksViewset(ModelViewSet):
    queryset = Books.objects.filter(is_deleted=False)
    serializer_class = BooksSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "post",
        "put",
        "delete",
    ]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["genre", "publication_year"]
    search_fields = ["title", "isbn", "genre"]
    ordering_fields = ["title", "publication_year", "available_copies"]


# 3. Author Management
# Add New Author: Allow admins/staff to add author details.
# Edit Author Information: Update author details as needed.
# Link Books to Authors: Associate books with authors to establish relationships (M2M relationship).
# View Author Details: Show all books by a specific author and their information.
# 4. Membership Management
# Add Membership Types: Allow admins to add different membership plans (e.g., standard, premium).
# Update Membership Details: Update price or plan details as needed.
# Assign Membership to Users: Link a user to a specific membership type.
# View Membership Plans: Show available membership options and their benefits.
# Renew/Cancel Membership: Allow users to renew or cancel their membership.
# 5. Borrowing and Returning Books
# Borrow Book: Enable users to borrow a book if available. Update available copies accordingly.
# Return Book: Allow users to return borrowed books, updating available copies.
# Check Borrowing Status: Track which user has borrowed which book and the return deadline.
# Renew Borrowed Book: Allow users to extend the borrowing period if no reservation is pending.
# Track Late Returns and Fines: Automatically calculate and apply late fees for overdue books.
# 6. Reservation System
# Reserve Book: Allow users to place a reservation on an unavailable book.
# Cancel Reservation: Let users cancel their reservations if no longer interested.
# Notify on Availability: Notify users when a reserved book becomes available.
# View Reservations: List all reserved books by a user with expected availability dates.
# 7. Notifications and Alerts
# Due Date Reminders: Notify users about upcoming due dates for borrowed books.
# Overdue Notifications: Alert users if they are overdue and inform them of any fees.
# Reservation Availability: Notify users when a reserved book is ready for pickup.
# Membership Renewal Reminders: Notify users when their membership is close to expiration.
# 8. Inventory and Catalog Management
# Inventory Check: Allow staff to review and manage current inventory levels.
# Add/Remove Copies: Adjust the number of copies available for each book.
# Catalog Management: Organize books into categories or collections, such as genre, new arrivals, or bestsellers.
# Track Damaged/Lost Books: Manage records of books that are damaged or lost.
# 9. Reports and Analytics
# Borrowing Reports: Generate reports on most-borrowed books, borrowing trends, etc.
# User Activity Reports: Show user activity such as most active users, overdue fines, and borrowing history.
# Inventory Reports: Report on the current stock of books, including damaged or lost items.
# Financial Reports: Generate reports on revenue from memberships, fines, and fees.
# 10. Admin and Staff Operations
# Staff Management: Add, update, or remove staff users with specific roles and permissions.
# Manage User Permissions: Assign and modify permissions for staff to control access to various operations.
# Audit Logs: Track user and staff activity for security and audit purposes.
# System Configuration: Allow admins to configure system-wide settings (e.g., fine rates, borrowing limits).
