from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Ticket, TicketReply
from .serializers import TicketSerializer, TicketReplySerializer, TicketStatusUpdateSerializer


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsResident(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'resident'


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsOwnerOrResident(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['owner', 'resident']


# --- RESIDENT VIEWS ---

class ResidentTicketListCreateView(generics.ListCreateAPIView):
    """Resident can list and create their own complaint tickets."""
    permission_classes = [IsResident]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(raised_by=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class ResidentTicketDetailView(generics.RetrieveAPIView):
    """Resident views a single ticket (with all replies)."""
    permission_classes = [IsResident]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(raised_by=self.request.user)


# --- OWNER VIEWS ---

class OwnerTicketListView(generics.ListAPIView):
    """Owner sees all tickets for their properties."""
    permission_classes = [IsOwner]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(property__owner=self.request.user)


class OwnerTicketStatusUpdateView(generics.UpdateAPIView):
    """Owner updates the status of a complaint ticket."""
    permission_classes = [IsOwner]
    serializer_class = TicketStatusUpdateSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return Ticket.objects.filter(property__owner=self.request.user)
        
    def perform_update(self, serializer):
        ticket = serializer.save()
        from accounts.models import Notification
        message = f"Your complaint '{ticket.title}' is now {ticket.get_status_display()}."
        if ticket.owner_response:
            message += f" Owner replied: {ticket.owner_response}"
        Notification.objects.create(user=ticket.raised_by, message=message)


# --- SHARED: REPLIES ---

class TicketReplyCreateView(generics.CreateAPIView):
    """Any authenticated user can add a reply to a ticket they're part of."""
    permission_classes = [IsOwnerOrResident]
    serializer_class = TicketReplySerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        ticket_pk = self.kwargs['ticket_pk']
        try:
            ticket = Ticket.objects.get(pk=ticket_pk)
        except Ticket.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Ticket not found.")
        # Ensure the user is associated with this ticket
        user = self.request.user
        if user.role == 'resident' and ticket.raised_by != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only reply to your own tickets.")
        if user.role == 'owner' and ticket.property.owner != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only reply to tickets on your property.")
        reply = serializer.save(ticket=ticket, author=user)
        
        from accounts.models import Notification
        if user.role == 'owner':
            Notification.objects.create(
                user=ticket.raised_by, 
                message=f"Owner replied to your complaint '{ticket.title}': {reply.message[:50]}..."
            )
        elif user.role == 'resident':
            Notification.objects.create(
                user=ticket.property.owner, 
                message=f"Resident replied to complaint '{ticket.title}': {reply.message[:50]}..."
            )


# --- SUPERADMIN ---

class AllTicketsListView(generics.ListAPIView):
    """Superadmin sees all tickets."""
    permission_classes = [IsSuperAdmin]
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
