from uuid import UUID
from knox.auth import TokenAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from django.db import transaction
from events.api.v1.serializers import EventSerializer
from events.models import Event
from externals.nocodeapi.google_calendar import (
    nocodeapi_google_calendar_create_event,
    nocodeapi_google_calendar_edit_event,
    nocodeapi_google_calendar_delete_event
)
from account.models import CustomUser
from events.utils import get_event_info


class CreateEventView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer

    @transaction.atomic
    def post(self, request: Request) -> Response:
        """Create event view."""
        if not request.user.is_authenticated:
            return Response(
                {"message": "User not authenticated"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Need email confirmed
        if not request.user.email_confirmed:
            return Response(
                {"message": "email not confirmed, please check your mail for the confirmation mail"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save(
            attendee=[request.user.id], created_by=request.user)
        google_calendar_response = nocodeapi_google_calendar_create_event(
            serializer.data, request.user.email)
        response.google_calendar_event_id = google_calendar_response
        response.invitation_sent = True
        response.save()
        return Response({"message": "Event successfully created", "data": serializer.data}, status=status.HTTP_201_CREATED)


class EditEventView(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer

    @transaction.atomic
    def patch(self, request: Request, event_id: UUID) -> Response:
        """Edit an event."""
        if not request.user.is_authenticated:
            return Response({"message": "User not authenticated"}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"message": f"Event with id {event_id} does not exist"},
                            status=status.HTTP_201_CREATED)

        if event.created_by != request.user.id:
            return Response({"message": "You don't have permission to edit this event"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(instance=event, data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save(updated_by=request.user)
        google_calendar_response = nocodeapi_google_calendar_edit_event(
            event.__dict__, request.user.email)
        response.google_calendar_event_id = google_calendar_response
        response.save()
        return Response({"message": "Event successfully edited"}, status=status.HTTP_200_OK)


class RetrieveEventView(RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs) -> Response:
        try:
            event = Event.objects.all()
        except Event.DoesNotExist:
            return Response(
                {"message": f"Events does not exist"},
                status=status.HTTP_200_OK
            )
        data = get_event_info(event)
        return Response(data, status=status.HTTP_200_OK)


class JoinEventView(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer

    @transaction.atomic
    def patch(self, request: Request, event_id: UUID, user_id: UUID) -> Response:
        """Edit an event."""
        if not request.user.is_authenticated:
            return Response({"message": "User not authenticated"}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"message": f"Event with id {event_id} does not exist"},
                            status=status.HTTP_201_CREATED)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message": f"User with id {user_id} does not exist"},
                            status=status.HTTP_201_CREATED)
        if str(user_id) not in event.attendee:
            event.attendee += [str(user_id)]
            event.save()
            nocodeapi_google_calendar_edit_event(event.__dict__, user.email)
            return Response({"message": "Successfully registered for this event"}, status=status.HTTP_200_OK)
        else:
            event.attendee.remove(str(user_id))
            nocodeapi_google_calendar_delete_event(event.__dict__)
            event.save()
            return Response({"message": "You have successfully removed this event"}, status=status.HTTP_200_OK)
