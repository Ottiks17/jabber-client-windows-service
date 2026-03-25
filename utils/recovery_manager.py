import json
import os
from datetime import datetime

class RecoveryManager:
    """Управление автоматическим восстановлением после сбоя"""
    
    def __init__(self, recovery_file="logs/recovery.json"):
        self.recovery_file = recovery_file
        self.ensure_logs_dir()
    
    def ensure_logs_dir(self):
        """Создание папки для логов"""
        os.makedirs(os.path.dirname(self.recovery_file), exist_ok=True)
    
    def save_state(self, core_state):
        """Сохранение состояния"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'version': '3.0',
            'is_running': core_state.get('is_running', False),
            'sources_enabled': core_state.get('sources_enabled', {}),
            'last_message_id': core_state.get('last_message_id', None),
            'last_check': datetime.now().isoformat()
        }
        
        try:
            with open(self.recovery_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")
            return False
    
    def restore_state(self):
        """Восстановление состояния после сбоя"""
        try:
            if os.path.exists(self.recovery_file):
                with open(self.recovery_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Проверяем актуальность состояния (не старше 1 часа)
                last_check = datetime.fromisoformat(state['last_check'])
                if (datetime.now() - last_check).seconds < 3600:
                    return state
        except Exception as e:
            print(f"Ошибка восстановления состояния: {e}")
        
        return None
    
    def clear_state(self):
        """Очистка сохраненного состояния"""
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
        except:
            pass
    
    def get_recovery_info(self):
        """Получить информацию о последнем восстановлении"""
        state = self.restore_state()
        if state:
            return {
                'has_recovery': True,
                'timestamp': state['timestamp'],
                'was_running': state['is_running']
            }
        return {'has_recovery': False}