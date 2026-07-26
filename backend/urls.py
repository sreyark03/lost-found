from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Lost & Found API',
        'endpoints': {
            'register': 'POST /api/register/',
            'login': 'POST /api/token/',
            'refresh': 'POST /api/token/refresh/',
            'lost_items': 'GET/POST /api/lost-items/',
            'found_items': 'GET/POST /api/found-items/',
            'claims': 'GET/POST /api/claims/',
            'review_claim': 'PATCH /api/claims/{id}/review/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend.api_urls')),
    path('', api_root),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)