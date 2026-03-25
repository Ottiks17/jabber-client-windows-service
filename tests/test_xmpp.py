#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки реального XMPP подключения
"""

import sys
import os
import yaml

# Добавляем путь к папке src
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from sender.real_xmpp_sender import RealXmppSender
from api.models import Message


def test_xmpp_connection():
    """Тестирование XMPP подключения"""
    print("=" * 50)
    print("Тестирование XMPP подключения")
    print("=" * 50)
    
    # Загружаем конфигурацию из корня проекта
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except:
        print("❌ Не найден файл config.yaml")
        return
    
    xmpp_config = config.get('xmpp', {})
    server = xmpp_config.get('server', 'localhost')
    username = xmpp_config.get('username', '')
    password = xmpp_config.get('password', '')
    
    print(f"\n📡 Настройки XMPP:")
    print(f"   Сервер: {server}")
    print(f"   Логин: {username}")
    print(f"   Пароль: {'*' * len(password) if password else '(не задан)'}")
    
    if not username or not password:
        print("\n❌ Не заданы логин или пароль. Проверьте config.yaml")
        return
    
    # Создаем отправителя
    sender = RealXmppSender(server, username, password)
    
    # Подключаемся
    print("\n🔌 Подключение...")
    if not sender.connect():
        print("\n❌ Не удалось подключиться!")
        print(f"   Ошибка: {sender.last_error if hasattr(sender, 'last_error') else 'Неизвестная ошибка'}")
        return
    
    print("\n✅ Подключение успешно!")
    
    # Отправляем тестовое сообщение себе
    print("\n📤 Отправка тестового сообщения...")
    
    test_message = Message.create(
        source_type="test",
        sender=username,
        recipient=username,
        text="Тестовое сообщение от Jabber Robot! 🤖"
    )
    
    receipt = sender.send_message(test_message)
    
    if receipt.error:
        print(f"❌ Ошибка отправки: {receipt.error}")
    else:
        print(f"✅ Сообщение отправлено!")
        print(f"   ID: {receipt.message_id}")
        print(f"   Время: {receipt.delivered_at}")
    
    # Отключаемся
    sender.disconnect()
    print("\n🔌 Отключено")
    
    print("\n" + "=" * 50)
    print("Тест завершен")
    print("=" * 50)


if __name__ == "__main__":
    test_xmpp_connection()