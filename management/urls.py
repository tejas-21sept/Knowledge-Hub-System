from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    BooksViewset,
    ForgetPasswordView,
    PasswordResetConfirmView,
    SignoutView,
    SignupView,
)

router = routers.DefaultRouter()
router.register("books", BooksViewset)

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("logout/", SignoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        ForgetPasswordView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/<int:uid>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # router.urls,
]

urlpatterns += router.urls
