#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API для Jabber клиента
Позволяет отправлять сообщения, получать статусы и управлять службой
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models import Message
from api.logger import FileLogger
from sender.xmpp_sender import XmppSender

app = Flask(__name__)
CORS(app)  # Разрешаем кросс-доменные запросы

# Инициализация компонентов
logger = FileLogger()
sender = None

# Конфигурация
CONFIG_FILE = 'config.yaml'

def get_sender():
    """Получить или создать XMPP отправителя"""
    global sender
    if sender is None:
        import yaml
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            xmpp_config = config.get('xmpp', {})
            sender = XmppSender(
                server=xmpp_config.get('server', 'localhost'),
                username=xmpp_config.get('username', ''),
                password=xmpp_config.get('password', '')
            )
            sender.connect()
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            sender = XmppSender()  # Эмуляция
            sender.connect()
    return sender

# ============= API Endpoints =============

@app.route('/', methods=['GET'])
def index():
    """Главная страница API"""
    return jsonify({
        'name': 'Jabber Client API',
        'version': '1.0.0',
        'description': 'REST API для отправки сообщений через XMPP',
        'endpoints': {
            '/api/health': 'GET - Проверка состояния',
            '/api/send': 'POST - Отправить сообщение',
            '/api/status/<message_id>': 'GET - Статус сообщения',
            '/api/logs': 'GET - Получить логи',
            '/api/stats': 'GET - Статистика',
            '/api/service/start': 'POST - Запустить службу',
            '/api/service/stop': 'POST - Остановить службу',
            '/api/service/status': 'GET - Статус службы'
        }
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'Jabber Client API'
    })

@app.route('/api/send', methods=['POST'])
def send_message():
    """
    Отправить сообщение через XMPP
    
    POST /api/send
    Body JSON:
    {
        "recipient": "user@jabber.local",
        "message": "Текст сообщения",
        "sender": "bot"  # опционально
    }
    """
    try:
        data = request.get_json()
        
        # Проверка обязательных полей
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        recipient = data.get('recipient')
        text = data.get('message')
        
        if not recipient:
            return jsonify({'error': 'recipient is required'}), 400
        
        if not text:
            return jsonify({'error': 'message is required'}), 400
        
        # Проверка длины сообщения
        if len(text) > 256:
            return jsonify({'error': 'Message exceeds 256 characters'}), 400
        
        # Создаем сообщение
        message = Message.create(
            source_type="api",
            sender=data.get('sender', 'api_user'),
            recipient=recipient,
            text=text
        )
        
        # Логируем получение
        logger.log_message_received(message)
        
        # Отправляем через XMPP
        xmpp_sender = get_sender()
        receipt = xmpp_sender.send_message(message)
        
        # Логируем отправку
        logger.log_message_sent(receipt, message)
        
        return jsonify({
            'status': 'sent',
            'message_id': message.id,
            'recipient': recipient,
            'sent_at': datetime.now().isoformat(),
            'delivered_at': receipt.delivered_at.isoformat() if receipt.delivered_at else None,
            'read_at': receipt.read_at.isoformat() if receipt.read_at else None,
            'error': receipt.error
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<message_id>', methods=['GET'])
def get_message_status(message_id):
    """Получить статус сообщения по ID"""
    try:
        logs = logger.get_logs()
        
        for log in logs:
            if log.id == message_id:
                return jsonify({
                    'message_id': log.id,
                    'message_type': log.message_type,
                    'sender': log.sender,
                    'recipient': log.recipient,
                    'text': log.text,
                    'created_at': log.created_at.isoformat(),
                    'sent_time': log.sent_time.isoformat() if log.sent_time else None,
                    'delivered_time': log.delivered_time.isoformat() if log.delivered_time else None,
                    'read_time': log.read_time.isoformat() if log.read_time else None
                }), 200
        
        return jsonify({'error': 'Message not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Получить все логи"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        logs = logger.get_logs()
        
        # Возвращаем последние N записей
        recent_logs = logs[-limit:] if limit else logs
        
        result = []
        for log in recent_logs:
            result.append({
                'id': log.id,
                'message_type': log.message_type,
                'sender': log.sender,
                'recipient': log.recipient,
                'text': log.text,
                'created_at': log.created_at.isoformat(),
                'sent_time': log.sent_time.isoformat() if log.sent_time else None,
                'delivered_time': log.delivered_time.isoformat() if log.delivered_time else None,
                'read_time': log.read_time.isoformat() if log.read_time else None
            })
        
        return jsonify({
            'total': len(result),
            'messages': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получить статистику"""
    try:
        logs = logger.get_logs()
        
        total = len(logs)
        sent = sum(1 for log in logs if log.sent_time)
        delivered = sum(1 for log in logs if log.delivered_time)
        read = sum(1 for log in logs if log.read_time)
        
        # Статистика по источникам
        sources = {}
        for log in logs:
            sources[log.message_type] = sources.get(log.message_type, 0) + 1
        
        return jsonify({
            'total_messages': total,
            'sent': sent,
            'delivered': delivered,
            'read': read,
            'by_source': sources,
            'last_24h': sum(1 for log in logs if log.created_at and 
                           (datetime.now() - log.created_at).days < 1)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/status', methods=['GET'])
def service_status():
    """Получить статус службы"""
    import win32serviceutil
    import win32service
    
    try:
        # Проверяем статус службы Windows
        status = win32serviceutil.QueryServiceStatus('JabberXMPPClient')
        state = status[1]
        
        states = {
            win32service.SERVICE_STOPPED: 'stopped',
            win32service.SERVICE_START_PENDING: 'starting',
            win32service.SERVICE_STOP_PENDING: 'stopping',
            win32service.SERVICE_RUNNING: 'running',
            win32service.SERVICE_CONTINUE_PENDING: 'continuing',
            win32service.SERVICE_PAUSE_PENDING: 'pausing',
            win32service.SERVICE_PAUSED: 'paused'
        }
        
        return jsonify({
            'service': 'JabberXMPPClient',
            'status': states.get(state, 'unknown'),
            'state_code': state
        }), 200
        
    except Exception as e:
        return jsonify({
            'service': 'JabberXMPPClient',
            'status': 'not_installed',
            'error': str(e)
        }), 200

@app.route('/api/service/start', methods=['POST'])
def start_service():
    """Запустить службу Windows"""
    import win32serviceutil
    
    try:
        win32serviceutil.StartService('JabberXMPPClient')
        return jsonify({'status': 'started', 'message': 'Service start requested'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/stop', methods=['POST'])
def stop_service():
    """Остановить службу Windows"""
    import win32serviceutil
    
    try:
        win32serviceutil.StopService('JabberXMPPClient')
        return jsonify({'status': 'stopped', 'message': 'Service stop requested'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk/send', methods=['POST'])
def send_bulk():
    """Отправить несколько сообщений"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'messages list is required'}), 400
        
        results = []
        xmpp_sender = get_sender()
        
        for msg_data in messages:
            recipient = msg_data.get('recipient')
            text = msg_data.get('message')
            
            if not recipient or not text:
                continue
            
            if len(text) > 256:
                results.append({
                    'recipient': recipient,
                    'status': 'error',
                    'error': 'Message exceeds 256 characters'
                })
                continue
            
            message = Message.create(
                source_type="api_bulk",
                sender=msg_data.get('sender', 'api_bulk'),
                recipient=recipient,
                text=text
            )
            
            logger.log_message_received(message)
            receipt = xmpp_sender.send_message(message)
            logger.log_message_sent(receipt, message)
            
            results.append({
                'message_id': message.id,
                'recipient': recipient,
                'status': 'sent' if not receipt.error else 'error',
                'error': receipt.error
            })
        
        return jsonify({
            'total': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Запускаем API сервер
    print("🚀 Запуск Jabber Client API сервера...")
    print("📍 Доступен по адресу: http://localhost:5000")
    print("📖 Документация: http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)
