from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.serializer import TokenAuth


class LoginApiView(APIView):
    serializer_class = TokenAuth

    @extend_schema(
        request=TokenAuth,
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        tags=["Auth"],
        description="User login endpoint that returns access token and user details.",
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = serializer.get_token(user)

        return Response({
            "status": "Login Successful",
            "username": user.username,
            "email": user.email,
            "access_token": str(token.access_token),
            "groups": user.groups.first().name if user.groups.exists() else None,
        }, status=status.HTTP_200_OK)


class LogoutApiView(APIView):
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Invalid or missing token"),
        },
        tags=["Auth"],
        description="Logs out a user by blacklisting the refresh token.",
    )
    def get(self, request, format=None):
        refresh_token = request.headers.get('Authorization')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token.split(' ')[1])
                token.blacklist()
                return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            except Exception:
                return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)
