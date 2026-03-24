# Jabber XMPP Client as Windows Service

## Описание проекта

Windows Service для автоматической отправки сообщений через протокол XMPP (Jabber). Сервис получает сообщения из двух источников:
- **Oracle Database** (через эмуляцию, готов к подключению)
- **REST API** (через эмуляцию, готов к подключению)

## Функциональность

✅ Работает как Windows Service  
✅ GUI для настройки параметров  
✅ Получение сообщений из Oracle и REST API  
✅ Отправка сообщений через XMPP  
✅ Логирование всех операций  
✅ Поддержка русских букв и спецсимволов  
✅ Ограничение сообщений 256 символов  

## Архитектура
## Установка

### 1. Клонирование репозитория
\\\ash
git clone https://github.com/ВАШ_ЛОГИН/jabber-client.git
cd jabber-client
\\\

### 2. Установка зависимостей
\\\ash
python -m pip install pyyaml pywin32
\\\

### 3. Настройка конфигурации
Создайте файл \config.yaml\:
\\\yaml
xmpp:
  server: "jabber.ru"
  username: "your_login@jabber.ru"
  password: "your_password"

oracle:
  enabled: true

rest:
  enabled: true
  api_url: "http://localhost:5000"
  api_key: "test-key-123"
\\\

### 4. Запуск в режиме GUI
\\\ash
python main.py
\\\

### 5. Установка как Windows Service
\\\ash
# От имени администратора
python jabber_service.py install
sc config JabberXMPPClient start= auto
sc start JabberXMPPClient
\\\

## Управление службой

\\\ash
# Статус
sc query JabberXMPPClient

# Остановка
net stop JabberXMPPClient

# Запуск
net start JabberXMPPClient

# Удаление
sc delete JabberXMPPClient
\\\

## Технологии

- Python 3.14+
- XMPP (эмуляция / готов к подключению slixmpp)
- Oracle Database (эмуляция / готов к подключению cx_Oracle)
- REST API (эмуляция)
- Windows Service (pywin32)
- GUI: tkinter

## Автор

Ваше имя / Организация

## Лицензия

MIT
# 🤖 Jabber Robot

Автоматическая система отправки уведомлений через XMPP (Jabber)

## 🚀 Быстрый старт

### 1. Установка
```bash
# Скачайте проект
git clone https://github.com/Ottiks17/jabber-client.git
cd jabber-client

# Запустите установщик
INSTALL.bat