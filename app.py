import os
import random
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
AUG_FOLDER = 'static/augmented'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUG_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/augment', methods=['POST'])
def augment_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filename = file.filename
    orig_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(orig_path)
    
    # เปิดภาพต้นฉบับด้วย PIL
    img = Image.open(orig_path).convert('RGB')
    
    # กำหนดขนาดมาตรฐานสำหรับโมเดล (เช่น 416x416)
    img = img.resize((416, 416))
    
    generated_images = []
    
    # ล้างไฟล์เก่าในโฟลเดอร์ augmented (ถ้ามี)
    for f in os.listdir(AUG_FOLDER):
        os.remove(os.path.join(AUG_FOLDER, f))

    # 1. ภาพต้นฉบับ (บันทึกไว้ด้วย)
    base_name = os.path.splitext(filename)[0]
    orig_save_path = os.path.join(AUG_FOLDER, f"{base_name}_original.jpg")
    img.save(orig_save_path)
    generated_images.append(f"/{orig_save_path}")

    # 2. ทำ Data Augmentation หลากหลายรูปแบบ
    variations = [
        ("rot90", lambda im: im.rotate(90)),
        ("rot180", lambda im: im.rotate(180)),
        ("rot270", lambda im: im.rotate(270)),
        ("fliph", lambda im: im.transpose(Image.FLIP_LEFT_RIGHT)),
        ("flipv", lambda im: im.transpose(Image.FLIP_TOP_BOTTOM)),
        ("bright", lambda im: ImageEnhance.Brightness(im).enhance(1.4)),
        ("dark", lambda im: ImageEnhance.Brightness(im).enhance(0.6)),
        ("contrast", lambda im: ImageEnhance.Contrast(im).enhance(1.5)),
        ("blur", lambda im: im.filter(ImageFilter.BLUR)),
    ]

    for tag, transform_func in variations:
        aug_img = transform_func(img)
        save_name = f"{base_name}_{tag}.jpg"
        save_path = os.path.join(AUG_FOLDER, save_name)
        aug_img.save(save_path)
        generated_images.append(f"/{save_path}")

    return jsonify({
        'status': 'success',
        'message': f'สร้างรูปภาพจำลองสำเร็จทั้งหมด {len(generated_images)} รูป พร้อมนำไปใช้เทรน!',
        'images': generated_images
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)