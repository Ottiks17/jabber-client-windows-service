from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Создание иконки приложения"""
    
    # Создаем изображение 256x256
    size = 256
    img = Image.new('RGB', (size, size), color='#6C5CE7')
    draw = ImageDraw.Draw(img)
    
    # Рисуем круг
    draw.ellipse([20, 20, size-20, size-20], fill='#FFFFFF', outline='#6C5CE7', width=5)
    
    # Рисуем букву J
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    
    draw.text((size//2-40, size//2-40), "JR", fill='#6C5CE7', font=font)
    
    # Сохраняем как ICO
    img.save('icon.ico', format='ICO', sizes=[(256, 256)])
    print("✅ Иконка создана: icon.ico")
    
    # Создаем также PNG версию
    img.save('icon.png', format='PNG')
    print("✅ PNG иконка создана: icon.png")

if __name__ == "__main__":
    create_icon()