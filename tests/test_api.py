#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый клиент для Jabber API
"""

import requests
import json
import time

API_URL = "http://localhost:5000"

def test_health():
    """Тест проверки здоровья"""
    print("\n📊 Проверка API...")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Статус: {response.json()}")

def test_send_message():
    """Тест отправки сообщения"""
    print("\n📤 Отправка сообщения...")
    data = {
        "recipient": "user1@jabber.local",
        "message": "Привет! Это тестовое сообщение из API",
        "sender": "test_bot"
    }
    response = requests.post(f"{API_URL}/api/send", json=data)
    result = response.json()
    print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result.get('message_id')

def test_message_status(message_id):
    """Тест получения статуса"""
    print(f"\n📊 Статус сообщения {message_id}...")
    response = requests.get(f"{API_URL}/api/status/{message_id}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_get_logs():
    """Тест получения логов"""
    print("\n📝 Получение последних логов...")
    response = requests.get(f"{API_URL}/api/logs?limit=5")
    data = response.json()
    print(f"Всего сообщений: {data['total']}")
    for msg in data['messages']:
        print(f"  - {msg['message_type']}: {msg['sender']} -> {msg['recipient']}")

def test_stats():
    """Тест получения статистики"""
    print("\n📊 Статистика...")
    response = requests.get(f"{API_URL}/api/stats")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_bulk_send():
    """Тест массовой отправки"""
    print("\n📤 Массовая отправка...")
    data = {
        "messages": [
            {"recipient": "user1@jabber.local", "message": "Сообщение 1"},
            {"recipient": "user2@jabber.local", "message": "Сообщение 2"},
            {"recipient": "user3@jabber.local", "message": "Сообщение 3"}
        ]
    }
    response = requests.post(f"{API_URL}/api/bulk/send", json=data)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_service_status():
    """Тест статуса службы"""
    print("\n🔧 Статус службы...")
    response = requests.get(f"{API_URL}/api/service/status")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("=" * 50)
    print("Jabber API Test Client")
    print("=" * 50)
    
    try:
        test_health()
        test_service_status()
        test_stats()
        
        # Отправляем тестовое сообщение
        msg_id = test_send_message()
        
        # Ждем немного
        time.sleep(1)
        
        # Проверяем статус
        if msg_id:
            test_message_status(msg_id)
        
        # Смотрим логи
        test_get_logs()
        
        # Массовая отправка
        test_bulk_send()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка: API сервер не запущен!")
        print("Запустите сервер командой: python api_server.py")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
