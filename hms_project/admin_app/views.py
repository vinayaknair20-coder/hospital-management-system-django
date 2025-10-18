# admin_app/views.py - COMPLETE WITH BEST PRACTICES
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.db.models import Count, Q
from datetime import timedelta
import logging

from .models import Staff, Specialization, LoginLog
from .serializers import (
    StaffSerializer, 
    StaffUpdateSerializer, 
    SpecializationSerializer
)
from .permissions import IsAdmin

logger = logging.getLogger(__name__)


# ============ HELPER FUNCTIONS (DRY Principle) ============
def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', 'Unknown')


def create_login_log(username, log_type, message, ip_address, success=True):
    """Create login log entry (reusable)"""
    try:
        LoginLog.objects.create(
            username=username,
            log_type=log_type,
            message=message,
            ip_address=ip_address,
            success=success
        )
    except Exception as e:
        logger.error(f"Failed to create login log: {str(e)}")


# ============ AUTHENTICATION VIEWS ============
@api_view(['POST'])
    @permission_classes([AllowAny])
def login_view(request):
    """Staff Login with JWT authentication"""
    try:
        # Extract credentials
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        ip_address = get_client_ip(request)
        
        # Validate input
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(username) < 6 or len(password) < 6:
            return Response(
                {'error': 'Username and password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get staff
        try:
            staff = Staff.objects.get(username=username)
        except Staff.DoesNotExist:
            create_login_log(username, 'FAILED', 'User not found', ip_address, False)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if locked
        if staff.is_locked():
            return Response(
                {'error': f'Account locked. Try again after {staff.locked_until.strftime("%H:%M")}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if active
        if not staff.is_active:
            return Response({'error': 'Account disabled'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verify password
        if not check_password(password, staff.password):
            staff.failed_login_attempts += 1
            
            # Lock after 5 failed attempts
            if staff.failed_login_attempts >= 5:
                staff.locked_until = timezone.now() + timedelta(minutes=30)
                staff.save()
                create_login_log(username, 'LOCKED', 'Account locked due to failed attempts', ip_address, False)
                return Response(
                    {'error': 'Account locked for 30 minutes due to multiple failed attempts'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            staff.save()
            create_login_log(username, 'FAILED', f'Invalid password (attempt {staff.failed_login_attempts}/5)', ip_address, False)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Success! Reset failed attempts
        staff.failed_login_attempts = 0
        staff.locked_until = None
        staff.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(staff)
        refresh['username'] = staff.username
        refresh['role'] = staff.role
        
        create_login_log(username, 'SUCCESS', 'Successful login', ip_address, True)
        
        return Response({
            'message': 'Login successful',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'staff_id': staff.staff_id,
                'username': staff.username,
                'staff_name': staff.staff_name,
                'role': staff.role,
                'email': staff.Email
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({'error': 'Login failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
    @permission_classes([IsAuthenticated])
def logout_view(request):
    """Staff Logout"""
    try:
        username = request.user.username if hasattr(request.user, 'username') else 'Unknown'
        create_login_log(username, 'SUCCESS', 'User logged out', get_client_ip(request), True)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({'error': 'Logout failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============ STAFF MANAGEMENT ============
class StaffViewSet(viewsets.ModelViewSet):
    """Complete Staff Management"""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer    # 
    permission_classes = [IsAuthenticated]  # COMMENTED FOR TESTING
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'gender']
    search_fields = ['staff_name', 'username', 'Email', 'Phone_number']
    ordering = ['staff_name']
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return StaffUpdateSerializer
        return StaffSerializer
    
    def get_queryset(self):
        queryset = Staff.objects.all()
        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable staff member"""
        staff = self.get_object()
        staff.is_active = False
        staff.save()
        logger.info(f"Staff {staff.staff_name} disabled by {request.user.username}")
        return Response({
            'message': f'{staff.staff_name} disabled successfully',
            'staff_id': staff.staff_id,
            'is_active': False
        })
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable staff member"""
        staff = self.get_object()
        staff.is_active = True
        staff.failed_login_attempts = 0
        staff.locked_until = None
        staff.save()
        logger.info(f"Staff {staff.staff_name} enabled by {request.user.username}")
        return Response({
            'message': f'{staff.staff_name} enabled successfully',
            'staff_id': staff.staff_id,
            'is_active': True
        })
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Get staff by role"""
        role = request.query_params.get('role')
        if not role:
            return Response({'error': 'Role parameter required'}, status=400)
        
        staff = Staff.objects.filter(role=role, is_active=True)
        serializer = self.get_serializer(staff, many=True)
        return Response({
            'role': role,
            'count': staff.count(),
            'staff': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Admin dashboard statistics"""
        stats = {
            'total_staff': Staff.objects.count(),
            'active_staff': Staff.objects.filter(is_active=True).count(),
            'by_role': {}
        }
        
        for role_code, role_name in Staff.Roles.choices:
            stats['by_role'][role_code] = {
                'name': role_name,
                'total': Staff.objects.filter(role=role_code).count(),
                'active': Staff.objects.filter(role=role_code, is_active=True).count()
            }
        
        return Response(stats)


# ============ SPECIALIZATION MANAGEMENT ============
class SpecializationViewSet(viewsets.ModelViewSet):
    """Doctor Specialization Management"""
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer    # 
    permission_classes = [IsAuthenticated]  # COMMENTED FOR TESTING
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['specialization_name']
    ordering = ['specialization_name']
    
    def get_queryset(self):
        queryset = Specialization.objects.all()
        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
