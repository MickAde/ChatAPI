from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from .models import User, Chat
from .serializers import *
from django.contrib.auth import authenticate
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


# Handles user registration
class RegisterView(APIView):
    def get(self, request):
        """
        Retrieves all registered users.
        Response: List of users serialized as JSON.
        """
        users = User.objects.all()  # Query all user records
        serializer = UserSerializer(users, many=True)  # Serialize multiple user instances
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Registers a new user.
        Validates the provided data, ensures username uniqueness, and saves the user.
        Response: Success or error message with appropriate status code.
        """
        data = request.data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=data['username']).exists():
                # Ensure username uniqueness
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()  # Save the new user to the database
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

        # Return validation errors
        return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Handles user login
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def get(self, request):
        """
        Provides a friendly message indicating the endpoint expects POST requests for login.
        """
        return Response({'message': 'Please send a POST with login credentials'}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Authenticates a user using provided username and password.
        Response: Authentication token upon success or error message upon failure.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                # Generate or retrieve a token for the authenticated user
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": str(token), "message": "Login successful"}, status=status.HTTP_200_OK)

        # Return error message if authentication fails
        return Response({"status": False, "data": serializer.errors, 'message': 'Invalid username or password'}, status=status.HTTP_200_OK)


# Handles AI chat interactions
class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        """
        Processes a user's message, deducts tokens, and provides an AI-generated response.
        Saves the chat interaction in the database.
        Response: AI-generated response, remaining tokens, and timestamp.
        """
        user = request.user  # Retrieve the authenticated user
        message = request.data.get('message')  # Extract the user's message from request data

        if not message:
            # Ensure the message is provided
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        if user.tokens < 100:
            # Check if the user has sufficient tokens
            return Response({"error": "Insufficient tokens"}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct 100 tokens for the interaction
        user.tokens -= 100
        user.save()

        # Generate a dummy AI response
        response = f"AI response to: {message}"

        # Save the chat interaction in the database
        chat = Chat.objects.create(user=user, message=message, response=response)

        # Return the response along with user token information
        return Response({
            "message": message,
            "response": response,
            "remaining_tokens": user.tokens,
            "timestamp": chat.timestamp,
        }, status=status.HTTP_201_CREATED)


# Handles token balance retrieval
class TokenBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        """
        Retrieves the token balance for the authenticated user.
        Response: Remaining tokens in the user's account.
        """
        user = request.user  # Retrieve the authenticated user
        
        if not user:
            # Ensure the user is authenticated
            raise AuthenticationFailed("Invalid token")

        # Return the user's remaining tokens
        return Response({"tokens": user.tokens}, status=status.HTTP_200_OK)
