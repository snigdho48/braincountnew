from rest_framework import status
import base64
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializer import TokenAuth
from rest_framework_simplejwt.tokens import RefreshToken


class LoginApiView(APIView):
    serializer_class = TokenAuth

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = serializer.get_token(user)
        
        
        
       

        return Response({
            "status": "Login Successful",
            "username": user.username,
            "email": user.email,
            "access_token":str(token.access_token),
            "groups" : user.groups.first().name,


        }, status=status.HTTP_200_OK)
        
        
class LogoutApiView(APIView):
    def get(self, request, format=None):
        refresh_token = request.headers.get('Authorization')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token.split(' ')[1])
                token.blacklist() 
                return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)
    