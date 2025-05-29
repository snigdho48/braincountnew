from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from api.models import Withdrawal, TaskSubmissionRequest, Notification
from api.serializer import WithdrawalSerializer
from django.db.models import Sum
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class WithdrawalApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: WithdrawalSerializer(many=True)},
        description="Get withdrawal requests for the logged-in user, including total completed and pending tasks.",
        tags=["Withdrawal"],
    )
    def get(self, request):
        if not request.user.groups.filter(name__in=['supervisor', 'admin']).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')
        serializer = WithdrawalSerializer(withdrawals, many=True)
        # Count completed and pending tasks for this user
        completed = TaskSubmissionRequest.objects.filter(user=request.user, is_accepeted='COMPLETED').count()
        pending = TaskSubmissionRequest.objects.filter(user=request.user, is_accepeted='PENDING').count()
        rejected = TaskSubmissionRequest.objects.filter(user=request.user, is_accepeted='REJECTED').count()
        total_amount = Withdrawal.objects.filter(user=request.user,status= 'APPROVED').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_pending_amount = Withdrawal.objects.filter(user=request.user, status='PENDING').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_withdrawable_amount = Withdrawal.objects.filter(user=request.user, status='APPROVED').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        
        return Response({
            'withdrawals': serializer.data,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'rejected_tasks': rejected,
            'total_amount': total_amount,
            'total_pending_amount': total_pending_amount,
            'total_withdrawable_amount': total_withdrawable_amount
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        if not request.user.groups.filter(name__in=['supervisor']).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Amount must be a number.'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal = Withdrawal.objects.create(user=request.user, amount=amount, status='PENDING')
        # Send notification
        notif = Notification.objects.create(
            user=request.user,
            message=f"Withdrawal request of amount {amount} has been created and is pending approval.",
            type='withdrawal'
        )
        self.send_realtime_notification(request.user.id, {
            "message": notif.message,
            "type": notif.type,
            "created_at": str(notif.created_at),
            "is_read": notif.is_read,
        })
        serializer = WithdrawalSerializer(withdrawal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def send_realtime_notification(self, user_id, content):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "content": content,
            }
        )

    # Helper for status change notification (to be used in PATCH/PUT)
    def send_status_change_notification(self, withdrawal, old_status, new_status):
        Notification.objects.create(
            user=withdrawal.user,
            message=f"Your withdrawal request of amount {withdrawal.amount} status changed from {old_status} to {new_status}.",
            type='withdrawal'
        )
    

