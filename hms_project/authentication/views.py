from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def register_user(request):
    """User registration endpoint - TO BE IMPLEMENTED"""
    return Response(
        {"message": "Registration endpoint - coming soon!"}, 
        status=status.HTTP_501_NOT_IMPLEMENTED
    )

@api_view(['POST'])
def login_user(request):
    """User login endpoint - TO BE IMPLEMENTED"""
    return Response(
        {"message": "Login endpoint - coming soon!"}, 
        status=status.HTTP_501_NOT_IMPLEMENTED
    )
