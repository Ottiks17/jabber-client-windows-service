#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web Dashboard for Jabber Client with Send Form
"""

import os
import sys
from flask import Flask, render_template, jsonify, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models import Message
from api.logger import FileLogger
from sender.xmpp_sender import XmppSender

app = Flask(__name__)
logger = FileLogger()
sender = None

def get_sender():
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

# Создаем папку templates если нет
if not os.path.exists('templates'):
    os.makedirs('templates')

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/dashboard/stats')
def get_stats():
    logs = logger.get_logs()
    total = len(logs)
    sent = sum(1 for l in logs if l.sent_time)
    delivered = sum(1 for l in logs if l.delivered_time)
    read = sum(1 for l in logs if l.read_time)
    
    sources = {}
    for log in logs:
        sources[log.message_type] = sources.get(log.message_type, 0) + 1
    
    return jsonify({
        'total': total,
        'sent': sent,
        'delivered': delivered,
        'read': read,
        'by_source': sources
    })

@app.route('/api/dashboard/messages')
def get_messages():
    logs = logger.get_logs()
    recent = logs[-20:] if logs else []
    messages = []
    for log in reversed(recent):
        messages.append({
            'id': log.id,
            'type': log.message_type,
            'sender': log.sender,
            'recipient': log.recipient,
            'text': log.text[:100],
            'sent_time': log.sent_time.isoformat() if log.sent_time else None
        })
    return jsonify({'messages': messages})

@app.route('/api/send', methods=['POST'])
def send_message():
    """API endpoint for sending messages from web dashboard"""
    try:
        data = request.get_json()
        recipient = data.get('recipient')
        text = data.get('message')
        
        if not recipient or not text:
            return jsonify({'error': 'recipient and message required'}), 400
        
        if len(text) > 256:
            return jsonify({'error': 'Message exceeds 256 characters'}), 400
        
        message = Message.create(
            source_type="web_dashboard",
            sender=data.get('sender', 'web_user'),
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
            'sent_at': receipt.delivered_at.isoformat() if receipt.delivered_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Jabber Client Web Dashboard")
    print("=" * 50)
    print("Open: http://localhost:8080")
    print("")
    print("Features:")
    print("  - Real-time statistics")
    print("  - Message history")
    print("  - Send messages via form")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8080, debug=True)