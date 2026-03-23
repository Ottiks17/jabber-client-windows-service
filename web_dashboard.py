#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web Dashboard for Jabber Client
Real-time monitoring and management interface
"""

import os
import sys
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.logger import FileLogger
from sender.xmpp_sender import XmppSender

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jabber-client-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

logger = FileLogger()
sender = None
monitoring_thread = None
is_monitoring = True

def safe_isoformat(dt):
    """Safely convert datetime to ISO format"""
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)

def get_sender():
    """Get or create XMPP sender"""
    global sender
    if sender is None:
        import yaml
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            xmpp_config = config.get('xmpp', {})
            sender = XmppSender(
                server=xmpp_config.get('server', 'localhost'),
                username=xmpp_config.get('username', ''),
                password=xmpp_config.get('password', '')
            )
            sender.connect()
        except:
            sender = XmppSender()
            sender.connect()
    return sender

def monitor_service():
    """Background thread for monitoring service status"""
    global is_monitoring
    while is_monitoring:
        try:
            logs = logger.get_logs()
            recent_messages = logs[-10:] if logs else []
            
            total = len(logs)
            sent = sum(1 for log in logs if log.sent_time)
            delivered = sum(1 for log in logs if log.delivered_time)
            read = sum(1 for log in logs if log.read_time)
            
            service_status = 'unknown'
            try:
                import win32serviceutil
                status = win32serviceutil.QueryServiceStatus('JabberXMPPClient')
                if status[1] == 4:
                    service_status = 'running'
                elif status[1] == 1:
                    service_status = 'stopped'
                else:
                    service_status = 'starting'
            except:
                service_status = 'not_installed'
            
            messages_list = []
            for msg in recent_messages:
                msg_dict = {
                    'id': msg.id,
                    'type': msg.message_type,
                    'sender': msg.sender,
                    'recipient': msg.recipient,
                    'text': msg.text[:50] + '...' if len(msg.text) > 50 else msg.text,
                    'sent_time': safe_isoformat(msg.sent_time),
                    'delivered_time': safe_isoformat(msg.delivered_time),
                    'read_time': safe_isoformat(msg.read_time)
                }
                messages_list.append(msg_dict)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'service_status': service_status,
                'stats': {
                    'total': total,
                    'sent': sent,
                    'delivered': delivered,
                    'read': read
                },
                'recent_messages': messages_list
            }
            
            socketio.emit('update', data)
            
        except Exception as e:
            print(f"Monitor error: {e}")
        
        time.sleep(5)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/stats')
def get_stats():
    """Get current statistics"""
    try:
        logs = logger.get_logs()
        
        total = len(logs)
        sent = sum(1 for log in logs if log.sent_time)
        delivered = sum(1 for log in logs if log.delivered_time)
        read = sum(1 for log in logs if log.read_time)
        
        sources = {}
        for log in logs:
            source_type = log.message_type if log.message_type else 'unknown'
            sources[source_type] = sources.get(source_type, 0) + 1
        
        hourly = {}
        now = datetime.now()
        for i in range(24):
            hour = now - timedelta(hours=i)
            hourly[hour.strftime('%H:00')] = 0
        
        for log in logs:
            if log.created_at:
                try:
                    created = log.created_at
                    if isinstance(created, str):
                        created = datetime.fromisoformat(created)
                    if isinstance(created, datetime) and (now - created).days < 1:
                        hour_key = created.strftime('%H:00')
                        if hour_key in hourly:
                            hourly[hour_key] += 1
                except:
                    pass
        
        return jsonify({
            'total': total,
            'sent': sent,
            'delivered': delivered,
            'read': read,
            'by_source': sources,
            'hourly': hourly,
            'success_rate': (delivered / total * 100) if total > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/messages')
def get_messages():
    """Get messages with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        logs = logger.get_logs()
        total = len(logs)
        start = (page - 1) * per_page
        end = start + per_page
        
        messages = []
        reversed_logs = list(reversed(logs)) if logs else []
        
        for log in reversed_logs[start:end]:
            try:
                msg_data = {
                    'id': log.id,
                    'type': log.message_type if log.message_type else 'unknown',
                    'sender': log.sender if log.sender else 'unknown',
                    'recipient': log.recipient if log.recipient else 'unknown',
                    'text': log.text if log.text else '',
                    'created_at': safe_isoformat(log.created_at),
                    'sent_time': safe_isoformat(log.sent_time),
                    'delivered_time': safe_isoformat(log.delivered_time),
                    'read_time': safe_isoformat(log.read_time)
                }
                messages.append(msg_data)
            except Exception as e:
                print(f"Error processing message: {e}")
                continue
        
        return jsonify({
            'messages': messages,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/service/start', methods=['POST'])
def start_service():
    """Start Windows service"""
    try:
        import win32serviceutil
        win32serviceutil.StartService('JabberXMPPClient')
        return jsonify({'status': 'started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/service/stop', methods=['POST'])
def stop_service():
    """Stop Windows service"""
    try:
        import win32serviceutil
        win32serviceutil.StopService('JabberXMPPClient')
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/service/status')
def get_service_status():
    """Get Windows service status"""
    try:
        import win32serviceutil
        import win32service
        status = win32serviceutil.QueryServiceStatus('JabberXMPPClient')
        state = status[1]
        
        states = {
            1: 'stopped',
            2: 'starting',
            3: 'stopping',
            4: 'running'
        }
        
        return jsonify({
            'status': states.get(state, 'unknown'),
            'state_code': state
        })
    except:
        return jsonify({'status': 'not_installed'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'data': 'Connected to Jabber Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    monitoring_thread = threading.Thread(target=monitor_service)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    
    print("=" * 50)
    print("Jabber Client Web Dashboard")
    print("=" * 50)
    print("Starting web server...")
    print("Open in browser: http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
