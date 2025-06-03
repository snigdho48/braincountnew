from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from api.models import Withdrawal, Notification,TaskSubmission,Withdrawal_Task_Amount
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
        completed = TaskSubmission.objects.filter(user=request.user, approval_status='APPROVED').count()
        pending = TaskSubmission.objects.filter(user=request.user, approval_status='PENDING').count()
        rejected = TaskSubmission.objects.filter(user=request.user, approval_status='REJECTED').count()
        total_amount = Withdrawal.objects.filter(user=request.user,status= 'APPROVED').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_pending_amount = Withdrawal.objects.filter(user=request.user, status='PENDING').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_withdrawable_amount = completed -( withdrawals.aggregate(total_completed=Sum('task_count'))['total_completed'] or 0) 
        withdrwal_amount_per_task = Withdrawal_Task_Amount.objects.filter(is_active=True).first()
        
        return Response({
            'withdrawals': serializer.data,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'rejected_tasks': rejected,
            'total_amount': int(total_amount * withdrwal_amount_per_task.amount),
            'total_pending_amount': int(total_pending_amount * withdrwal_amount_per_task.amount),
            'total_withdrawable_amount': int(total_withdrawable_amount * withdrwal_amount_per_task.amount),
            'withdrwal_amount_per_task': withdrwal_amount_per_task.amount or 0
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        if not request.user.groups.filter(name__in=['supervisor']).exists():
            return Response({"error": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')
        # Count completed and pending tasks for this user
        completed = TaskSubmission.objects.filter(user=request.user, approval_status='APPROVED').count()
        total_withdrawable_amount = completed -( withdrawals.aggregate(total_completed=Sum('task_count'))['total_completed'] or 0) 
        withdrwal_amount_per_task = Withdrawal_Task_Amount.objects.filter(is_active=True).first()
        amount = total_withdrawable_amount * withdrwal_amount_per_task.amount
        task_count = withdrawals.aggregate(total_completed=Sum('task_count'))['total_completed'] or 0
        if not amount:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not task_count:
            return Response({'error': 'Task count is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Amount must be a number.'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal = Withdrawal.objects.create(user=request.user, amount=amount, status='PENDING',task_count=task_count)
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
    

