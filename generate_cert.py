from OpenSSL import crypto
import os

def generate_self_signed_cert():
    """Генерация самоподписанного SSL сертификата"""
    
    # Создаем ключ
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Создаем сертификат
    cert = crypto.X509()
    cert.get_subject().C = "RU"
    cert.get_subject().ST = "Moscow"
    cert.get_subject().L = "Moscow"
    cert.get_subject().O = "Jabber Robot"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # 1 год
    
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Сохраняем
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    print("✅ SSL сертификат создан: cert.pem, key.pem")

if __name__ == "__main__":
    generate_self_signed_cert()