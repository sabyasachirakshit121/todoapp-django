from typing import Optional, Dict, Any
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.utils import timezone

from account.serializers import UserLoginSerializer, UserRegisterSerializer, UserChangePasswordSerializer
from account.utils import get_user_info


class UserRegistration(APIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    @transaction.atomic
    def post(self, request: Request) -> Response:
        """User register."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()

        update_last_login(None, user)
        # create token
        token_object, token = AuthToken.objects.create(user)
        user_data = get_user_info(user, token)

        return Response(user_data, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    @transaction.atomic
    def post(self, request: Request) -> Response:
        """User login."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['email']
        user.last_login = timezone.localtime()
        user.save(update_fields=['last_login'])
        # create token
        _, token = AuthToken.objects.create(user)

        user_data = get_user_info(user, token)

        return Response(user_data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = None

    @transaction.atomic
    def post(self, request: Request) -> Response:
        """User logout."""
        request._auth.delete()  # noqa
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class UserChangePasswordView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserChangePasswordSerializer

    @transaction.atomic
    def post(self, request: Request) -> Response:
        """User change password."""
        if not request.user.is_authenticated:  # pragma: no cover  # should not happen but mypy needs this
            raise AssertionError('User not authenticated')
        serializer = self.serializer_class(
            instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password_1'])
        request.user.save()

        return Response({}, status=status.HTTP_200_OK)
