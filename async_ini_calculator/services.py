import time
import random
import requests
from datetime import datetime
from typing import Dict, Any
from django.conf import settings


class INICalculatorService:
    """Сервис для асинхронного расчета INI индекса"""
    
    def calculate_ini_index(self, biomarker_data: Dict[str, Any]) -> float:
        """
        Расчет INI индекса по формуле:
        1. Нормализация каждого значения относительно диапазона нормы
        2. Умножение на значимость биомаркера
        3. Суммирование и преобразование в проценты
        """
        total_score = 0.0
        
        for biomarker in biomarker_data.get('biomarkers', []):
            patient_value = biomarker.get('patient_value')
            min_value = biomarker.get('min_value')
            max_value = biomarker.get('max_value')
            significance = biomarker.get('significance', 1.0)
            
            if patient_value is None:
                continue
            
            # Нормализация значения
            value_range = max_value - min_value
            if value_range == 0:
                continue
            
            normalized_value = (patient_value - min_value) / value_range
            
            # Ограничение между 0 и 1
            normalized_value = max(0.0, min(1.0, normalized_value))
            
            # Добавление к общему score
            total_score += normalized_value * significance
        
        # Преобразование в проценты (0-100)
        ini_result = total_score * 100
        
        # Добавляем небольшую случайную вариацию для реалистичности
        variation = random.uniform(-5, 5)
        ini_result = max(0.0, min(100.0, ini_result + variation))
        
        return round(ini_result, 2)
    
    def simulate_calculation_with_delay(self, research_id: int, biomarker_ids: list) -> Dict[str, Any]:
        """
        Имитация расчета с задержкой 5-10 секунд
        """
        print(f"Starting INI calculation for research {research_id}...")
        
        # Случайная задержка от 5 до 10 секунд
        delay = random.uniform(5, 10)
        time.sleep(delay)
        
        # Имитация получения данных биомаркеров
        # В реальном приложении здесь был бы запрос к основному сервису
        simulated_data = {
            "research_id": research_id,
            "biomarker_ids": biomarker_ids,
            "biomarkers": self._generate_simulated_biomarkers(biomarker_ids)
        }
        
        # Расчет INI
        ini_result = self.calculate_ini_index(simulated_data)
        
        # Случайный успех/неуспех (90% успеха)
        success = random.random() > 0.1
        
        result = {
            "success": success,
            "ini_result": ini_result if success else None,
            "error_message": "Calculation failed due to insufficient data" if not success else None,
            "calculated_at": datetime.now().isoformat(),
            "delay_seconds": round(delay, 2)
        }
        
        print(f"INI calculation completed for research {research_id}: {result}")
        return result
    
    def _generate_simulated_biomarkers(self, biomarker_ids: list) -> list:
        """Генерация имитационных данных биомаркеров"""
        biomarkers = []
        
        # Стандартные медицинские биомаркеры с их диапазонами
        standard_biomarkers = [
            {"name": "Гемоглобин", "min": 120, "max": 180, "unit": "г/л", "significance": 0.25},
            {"name": "Альбумин", "min": 35, "max": 50, "unit": "г/л", "significance": 0.30},
            {"name": "Лейкоциты", "min": 4, "max": 9, "unit": "×10⁹/л", "significance": 0.15},
            {"name": "Лимфоциты", "min": 1.2, "max": 3.5, "unit": "×10⁹/л", "significance": 0.20},
            {"name": "Креатинин", "min": 60, "max": 110, "unit": "мкмоль/л", "significance": 0.10},
        ]
        
        for i, biomarker_id in enumerate(biomarker_ids[:len(standard_biomarkers)]):
            std_bio = standard_biomarkers[i % len(standard_biomarkers)]
            
            # Генерация случайного значения пациента в пределах нормы ± 20%
            range_mid = (std_bio["min"] + std_bio["max"]) / 2
            range_width = std_bio["max"] - std_bio["min"]
            
            # Случайное отклонение от нормы
            deviation = random.uniform(-0.3, 0.3)  # ±30%
            patient_value = range_mid + (deviation * range_width)
            
            biomarkers.append({
                "id": biomarker_id,
                "name": std_bio["name"],
                "patient_value": round(patient_value, 2),
                "min_value": std_bio["min"],
                "max_value": std_bio["max"],
                "measure_unit": std_bio["unit"],
                "significance": std_bio["significance"]
            })
        
        return biomarkers
    
    def send_result_to_main_service(self, research_id: int, calculation_result: Dict[str, Any]):
        """Отправка результата расчета в основной сервис"""
        if not calculation_result["success"]:
            print(f"Calculation failed for research {research_id}, not sending result")
            return
        
        url = f"{settings.MAIN_SERVICE_URL}/api/async/update-ini-result"
        
        payload = {
            "research_id": research_id,
            "ini_result": calculation_result["ini_result"],
            "secret_key": settings.MAIN_SERVICE_SECRET
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"Successfully sent INI result to main service for research {research_id}")
            else:
                print(f"Failed to send result: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending result to main service: {e}")


calculator_service = INICalculatorService()