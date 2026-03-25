#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models import Message
from api.logger import FileLogger
from sender.real_xmpp_sender import RealXmppSender

app = Flask(__name__)
CORS(app)

logger = FileLogger()
sender = None

def get_sender():
    global sender
    if sender is None:
        import yaml
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            xmpp_config = config.get('xmpp', {})
            sender = RealXmppSender(
                server=xmpp_config.get('server', 'jabber.fr'),
                username=xmpp_config.get('username', ''),
                password=xmpp_config.get('password', '')
            )
            sender.connect()
        except Exception as e:
            print(f"Ошибка: {e}")
            sender = RealXmppSender()
            sender.connect()
    return sender

@app.route('/')
def index():
    return jsonify({
        'name': 'Jabber Client API',
        'version': '1.0.0',
        'endpoints': {
            '/api/health': 'GET - Health check',
            '/api/send': 'POST - Send message',
            '/api/logs': 'GET - Get logs',
            '/api/stats': 'GET - Statistics'
        }
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/send', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        recipient = data.get('recipient')
        text = data.get('message')
        
        if not recipient or not text:
            return jsonify({'error': 'recipient and message required'}), 400
        
        if len(text) > 256:
            return jsonify({'error': 'Message exceeds 256 characters'}), 400
        
        message = Message.create(
            source_type="api",
            sender=data.get('sender', 'api_user'),
            recipient=recipient,
            text=text
        )
        
        logger.log_message_received(message)
        receipt = get_sender().send_message(message)
        logger.log_message_sent(receipt, message)
        
        return jsonify({
            'status': 'sent',
            'message_id': message.id,
            'recipient': recipient,
            'sent_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        limit = request.args.get('limit', 50, type=int)
        logs = logger.get_logs()
        recent = logs[-limit:] if logs else []
        
        result = []
        for log in recent:
            result.append({
                'id': log.id,
                'type': log.message_type,
                'sender': log.sender,
                'recipient': log.recipient,
                'text': log.text,
                'sent_time': log.sent_time.isoformat() if log.sent_time else None,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        return jsonify({'total': len(result), 'messages': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        logs = logger.get_logs()
        total = len(logs)
        sent = sum(1 for log in logs if log.sent_time)
        
        sources = {}
        for log in logs:
            sources[log.message_type] = sources.get(log.message_type, 0) + 1
        
        return jsonify({
            'total_messages': total,
            'sent': sent,
            'by_source': sources
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Jabber Client API server...")
    print("Open: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)