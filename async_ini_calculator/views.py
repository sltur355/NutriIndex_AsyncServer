from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import threading
import time
import random
from datetime import datetime
import json
import requests


@method_decorator(csrf_exempt, name='dispatch')
class CalculateINIView(View):
    """
    API для запуска асинхронного расчета INI индекса
    """
    
    def post(self, request):
        """
        Запуск расчета INI индекса для исследования
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )
        
        research_id = data.get('research_id')
        biomarker_ids = data.get('biomarker_ids', [])
        secret_key = data.get('secret_key')
        
        # Базовая валидация
        if not research_id:
            return JsonResponse(
                {"error": "research_id is required"},
                status=400
            )
        
        if not biomarker_ids:
            return JsonResponse(
                {"error": "biomarker_ids is required"},
                status=400
            )
        
        # Проверка ключа
        expected_key = "nutriscan_async_key_2024"
        if secret_key != expected_key:
            return JsonResponse(
                {"error": "Invalid secret key"},
                status=401
            )
        
        # Запускаем расчет в отдельном потоке
        thread = threading.Thread(
            target=self._async_calculation,
            args=(research_id, biomarker_ids)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            "message": "INI calculation started asynchronously",
            "research_id": research_id,
            "status": "processing",
            "estimated_delay": "5-10 seconds",
            "timestamp": datetime.now().isoformat()
        }, status=202)
    
    def _async_calculation(self, research_id: int, biomarker_ids: list):
        """Асинхронный расчет INI"""
        print(f"🚀 Starting INI calculation for research {research_id}...")
        
        # Случайная задержка от 5 до 10 секунд
        delay = random.uniform(5, 10)
        time.sleep(delay)
        
        # Упрощенный расчет INI
        base_score = random.uniform(0.3, 0.8)
        biomarker_factor = min(len(biomarker_ids) / 10.0, 1.0)
        variation = random.uniform(-0.1, 0.1)
        
        ini_result = (base_score * biomarker_factor + variation) * 100
        ini_result = max(0.0, min(100.0, ini_result))
        ini_result = round(ini_result, 2)
        
        # Случайный успех/неуспех
        success = random.random() > 0.1
        
        result = {
            "success": success,
            "ini_result": ini_result if success else None,
            "calculated_at": datetime.now().isoformat(),
            "delay_seconds": round(delay, 2),
            "research_id": research_id
        }
        
        print(f"✅ INI calculation completed for research {research_id}: {result}")
        
        # Отправляем результат в основной сервис
        if success:
            self._send_result_to_main_service(research_id, ini_result)
    
    def _send_result_to_main_service(self, research_id: int, ini_result: float):
        """Отправка результата расчета в основной сервис"""
        # Для теста используем localhost
        url = "http://localhost:8081/api/async/update-ini-result"
        
        payload = {
            "research_id": research_id,
            "ini_result": ini_result,
            "secret_key": "nutriscan_async_key_2024"
        }
        
        print(f"📤 Sending result to: {url}")
        print(f"📤 Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            print(f"📤 Response status: {response.status_code}")
            print(f"📤 Response text: {response.text}")
            
            if response.status_code == 200:
                print(f"📤 Successfully sent INI result to main service for research {research_id}")
            else:
                print(f"❌ Failed to send result: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending result to main service: {e}")


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """
    Проверка здоровья сервиса
    """
    
    def get(self, request):
        return JsonResponse({
            "status": "healthy",
            "service": "NutriScan Async INI Calculator",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })


@method_decorator(csrf_exempt, name='dispatch')
class TestView(View):
    """
    Тестовый эндпоинт для проверки
    """
    
    def get(self, request):
        return JsonResponse({
            "message": "Django async service is running!",
            "endpoints": {
                "calculate_ini": "POST /api/async/calculate-ini/",
                "health": "GET /api/async/health/",
                "test": "GET /api/async/test/"
            },
            "timestamp": datetime.now().isoformat()
        })