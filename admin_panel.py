#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Admin Panel for Jabber Client
Web interface for managing messages, users, and monitoring
"""

import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from functools import wraps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.logger import FileLogger
from api.models import Message
from sender.xmpp_sender import XmppSender

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jabber-admin-secret-key-2024'
CORS(app)

logger = FileLogger()

# Простая аутентификация (можно заменить на более сложную)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в админку"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Неверный логин или пароль')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    """Выход из админки"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Главная страница админки"""
    return render_template('admin.html')

@app.route('/api/admin/stats')
@login_required
def get_admin_stats():
    """Получить расширенную статистику"""
    logs = logger.get_logs()
    
    total = len(logs)
    sent = sum(1 for l in logs if l.sent_time)
    delivered = sum(1 for l in logs if l.delivered_time)
    read = sum(1 for l in logs if l.read_time)
    
    # Статистика по дням (последние 30 дней)
    daily_stats = {}
    now = datetime.now()
    for i in range(30):
        day = now - timedelta(days=i)
        day_key = day.strftime('%Y-%m-%d')
        daily_stats[day_key] = {'total': 0, 'sent': 0}
    
    for log in logs:
        if log.created_at:
            try:
                created = log.created_at
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                day_key = created.strftime('%Y-%m-%d')
                if day_key in daily_stats:
                    daily_stats[day_key]['total'] += 1
                    if log.sent_time:
                        daily_stats[day_key]['sent'] += 1
            except:
                pass
    
    # Статистика по часам
    hourly_stats = {}
    for i in range(24):
        hourly_stats[f'{i:02d}:00'] = 0
    
    for log in logs:
        if log.created_at:
            try:
                created = log.created_at
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                hour_key = created.strftime('%H:00')
                if hour_key in hourly_stats:
                    hourly_stats[hour_key] += 1
            except:
                pass
    
    # Статистика по пользователям
    users = {}
    for log in logs:
        recipient = log.recipient
        if recipient:
            users[recipient] = users.get(recipient, 0) + 1
    
    top_users = sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Статистика по источникам
    sources = {}
    for log in logs:
        source = log.message_type if log.message_type else 'unknown'
        sources[source] = sources.get(source, 0) + 1
    
    return jsonify({
        'total': total,
        'sent': sent,
        'delivered': delivered,
        'read': read,
        'success_rate': (delivered / total * 100) if total > 0 else 0,
        'daily_stats': daily_stats,
        'hourly_stats': hourly_stats,
        'top_users': top_users,
        'by_source': sources
    })

@app.route('/api/admin/messages')
@login_required
def get_admin_messages():
    """Получить все сообщения с фильтрацией"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        source_filter = request.args.get('source', '')
        status_filter = request.args.get('status', '')
        
        logs = logger.get_logs()
        
        # Фильтрация
        filtered_logs = []
        for log in logs:
            # Поиск по тексту
            if search and search.lower() not in log.text.lower():
                continue
            
            # Фильтр по источнику
            if source_filter and source_filter != log.message_type:
                continue
            
            # Фильтр по статусу
            if status_filter:
                if status_filter == 'sent' and not log.sent_time:
                    continue
                if status_filter == 'delivered' and not log.delivered_time:
                    continue
                if status_filter == 'read' and not log.read_time:
                    continue
                if status_filter == 'pending' and log.sent_time:
                    continue
            
            filtered_logs.append(log)
        
        # Пагинация
        total = len(filtered_logs)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_logs = filtered_logs[start:end]
        
        messages = []
        for log in reversed(paginated_logs):
            messages.append({
                'id': log.id,
                'type': log.message_type,
                'sender': log.sender,
                'recipient': log.recipient,
                'text': log.text,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'sent_time': log.sent_time.isoformat() if log.sent_time else None,
                'delivered_time': log.delivered_time.isoformat() if log.delivered_time else None,
                'read_time': log.read_time.isoformat() if log.read_time else None
            })
        
        return jsonify({
            'messages': messages,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/messages/<message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Удалить сообщение из лога"""
    try:
        logs = logger.get_logs()
        new_logs = [log for log in logs if log.id != message_id]
        
        # Сохраняем обновленный список
        with open('logs/messages.log', 'w', encoding='utf-8') as f:
            json.dump([vars(log) for log in new_logs], f, ensure_ascii=False, indent=2, default=str)
        
        logger.logs = new_logs
        return jsonify({'status': 'deleted'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/messages/clear', methods=['POST'])
@login_required
def clear_messages():
    """Очистить все логи"""
    try:
        with open('logs/messages.log', 'w', encoding='utf-8') as f:
            f.write('[]')
        
        logger.logs = []
        return jsonify({'status': 'cleared'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/service/restart', methods=['POST'])
@login_required
def restart_service():
    """Перезапустить Windows Service"""
    try:
        import win32serviceutil
        win32serviceutil.StopService('JabberXMPPClient')
        import time
        time.sleep(2)
        win32serviceutil.StartService('JabberXMPPClient')
        return jsonify({'status': 'restarted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export', methods=['GET'])
@login_required
def export_data():
    """Экспорт данных в CSV/JSON"""
    format_type = request.args.get('format', 'json')
    logs = logger.get_logs()
    
    if format_type == 'csv':
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Type', 'Sender', 'Recipient', 'Text', 'Created', 'Sent', 'Delivered', 'Read'])
        
        for log in logs:
            writer.writerow([
                log.id,
                log.message_type,
                log.sender,
                log.recipient,
                log.text,
                log.created_at,
                log.sent_time,
                log.delivered_time,
                log.read_time
            ])
        
        return output.getvalue(), 200, {'Content-Type': 'text/csv'}
    else:
        return jsonify([vars(log) for log in logs])

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("=" * 50)
    print("Jabber Admin Panel")
    print("=" * 50)
    print("Login: admin / admin123")
    print("Open: http://localhost:5001/admin")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)