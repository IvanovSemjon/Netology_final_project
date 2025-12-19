"""
View для запуска Celery-задачи do_import из админки
"""
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.tasks.celery_tasks import do_import


@method_decorator(staff_member_required, name='dispatch')
class AdminImportView(APIView):
    """
    View для запуска импорта товаров из админки
    """
    
    def post(self, request):
        """
        Запуск асинхронного импорта товаров
        """
        url = request.data.get('url')
        
        if not url:
            return Response(
                {'error': 'URL не указан'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Запускаем асинхронную задачу
        task = do_import.delay(url)
        
        return Response({
            'message': 'Импорт запущен',
            'task_id': task.id,
            'status': 'started'
        })


@staff_member_required
@require_POST
@csrf_exempt
def start_import(request):
    """
    Функция-view для запуска импорта из админки (альтернативный вариант)
    """
    import json
    
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return JsonResponse({'error': 'URL не указан'}, status=400)
        
        # Запускаем асинхронную задачу
        task = do_import.delay(url)
        
        return JsonResponse({
            'message': 'Импорт запущен',
            'task_id': task.id,
            'status': 'started'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)