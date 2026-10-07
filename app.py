import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cyber_cloud_key_2026')

# بيانات الدخول المعينة للدكتور
USER_CREDENTIALS = {
    'DrKarim': 'cloud2026'
}

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# قالب تسجيل الدخول
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - السحابة الشخصية</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(10px); padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 340px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }
        h2 { margin-bottom: 8px; color: #38bdf8; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #0284c7, #0369a1); border: none; color: white; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #0ea5e9; }
        .error { color: #f87171; font-size: 13px; margin-top: 10px; background: rgba(239, 68, 68, 0.1); padding: 8px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>☁️ Cloud Storage</h2>
        <p style="font-size: 13px; color: #94a3b8;">منصة تخزين سحابية آمنة</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="اسم المستخدم" required autocomplete="off">
            <input type="password" name="password" placeholder="كلمة المرور" required>
            <button type="submit">تسجيل الدخول للسحابة</button>
        </form>
    </div>
</body>
</html>
"""

# قالب لوحة التحكم الحديث الشامل
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة التخزين السحابي الحديثة</title>
    <style>
        :root {
            --bg-color: #090d16;
            --panel-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --primary: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(2, 132, 199, 0.1) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.08) 0%, transparent 40%);
            color: var(--text-main);
            margin: 0;
            padding: 30px;
            min-height: 100vh;
            box-sizing: border-box;
        }

        .container { max-width: 1100px; margin: 0 auto; }

        .header {
            display: flex; justify-content: space-between; align-items: center;
            background: var(--panel-bg); backdrop-filter: blur(12px);
            padding: 20px 30px; border-radius: 16px; border: 1px solid var(--border-color);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 30px;
        }

        .header h2 { margin: 0; font-size: 22px; color: #38bdf8; }

        .user-info { display: flex; align-items: center; gap: 15px; font-size: 14px; color: var(--text-muted); }
        .user-info b { color: #38bdf8; }

        .btn-logout {
            background: rgba(239, 68, 68, 0.2); color: #f87171;
            padding: 8px 18px; border-radius: 8px; text-decoration: none;
            font-size: 13px; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.4);
        }
        .btn-logout:hover { background: #ef4444; color: white; }

        .upload-card {
            background: var(--panel-bg); backdrop-filter: blur(12px);
            padding: 35px; border-radius: 16px; border: 1px solid var(--border-color);
            text-align: center; margin-bottom: 40px;
        }

        .upload-btn-wrapper {
            display: inline-block; cursor: pointer; border: 2px dashed rgba(56, 189, 248, 0.4);
            padding: 25px 40px; border-radius: 12px; background: rgba(2, 132, 199, 0.03); width: 100%; max-width: 450px; box-sizing: border-box;
        }

        .submit-btn {
            background: linear-gradient(135deg, #0284c7, #0369a1); border: none; color: white;
            padding: 12px 30px; border-radius: 10px; font-weight: bold; font-size: 15px; cursor: pointer; margin-top: 20px;
        }

        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }

        .img-card {
            background: var(--panel-bg); backdrop-filter: blur(12px); border-radius: 14px;
            overflow: hidden; border: 1px solid var(--border-color); transition: transform 0.3s;
        }
        .img-card:hover { transform: translateY(-5px); border-color: rgba(56, 189, 248, 0.4); }

        .img-container { width: 100%; height: 170px; overflow: hidden; background: #000; cursor: pointer; }
        .img-card img { width: 100%; height: 100%; object-fit: cover; }

        .img-info { padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; }
        .badge-view { font-size: 11px; background: rgba(56, 189, 248, 0.15); color: var(--primary); padding: 5px 10px; border-radius: 6px; cursor: pointer; }

        /* Modal */
        .modal {
            display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(8px); justify-content: center; align-items: center; flex-direction: column;
        }
        .modal-controls { position: absolute; top: 20px; display: flex; gap: 12px; z-index: 1001; }
        .modal-btn { background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); padding: 8px 16px; border-radius: 8px; cursor: pointer; }
        .modal-btn.close-btn { background: rgba(239, 68, 68, 0.7); }
        .modal-img-wrapper { max-width: 90%; max-height: 80vh; overflow: auto; margin-top: 50px; }
        .modal-content { max-width: 100%; max-height: 80vh; border-radius: 10px; transition: transform 0.25s ease; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🛡️ Cloud Storage Platform</h2>
            <div class="user-info">
                <span>المستخدم الحالي: <b>{{ username }}</b></span>
                <a href="{{ url_for('logout') }}" class="btn-logout">تسجيل خروج</a>
            </div>
        </div>

        <div class="upload-card">
            <h3>رفع ملف أو صورة جديدة</h3>
            <p>قم باختيار صورة من جهازك لتخزينها فوراً على السيرفر السحابي</p>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="file" name="file" id="file" required style="display:none;" onchange="document.getElementById('fileName').innerText = 'الملف المحدد: ' + this.files[0].name">
                <label class="upload-btn-wrapper" for="file">
                    <span style="font-size: 28px; display: block; margin-bottom: 8px;">📁</span>
                    <span style="color: var(--primary); font-weight: 600;">انقر لاختيار ملف من حاسوبك</span>
                    <p id="fileName" style="font-size: 12px; color: var(--text-muted); margin: 8px 0 0 0;"></p>
                </label>
                <br>
                <button type="submit" class="submit-btn">رفع الملف إلى السحابة</button>
            </form>
        </div>

        <div style="margin-bottom:20px;">📂 الصور والمستندات المخزنة في الكلاود:</div>
        <div class="gallery">
            {% for image in images %}
            <div class="img-card">
                <div class="img-container" onclick="openModal('{{ url_for('uploaded_file', filename=image) }}')">
                    <img src="{{ url_for('uploaded_file', filename=image) }}" alt="Cloud Image">
                </div>
                <div class="img-info">
                    <span style="font-size:12px; color:#94a3b8; overflow:hidden; text-overflow:ellipsis; max-width:140px; white-space:nowrap;">{{ image }}</span>
                    <span class="badge-view" onclick="openModal('{{ url_for('uploaded_file', filename=image) }}')">عرض وتكبير</span>
                </div>
            </div>
            {% else %}
            <p style="color: #64748b;">السحابة فارغة حالياً. قم برفع أول صورة!</p>
            {% endfor %}
        </div>
    </div>

    <div id="imageModal" class="modal">
        <div class="modal-controls">
            <button class="modal-btn" onclick="zoomIn()">🔍+ تكبير</button>
            <button class="modal-btn" onclick="zoomOut()">🔍- تصغير</button>
            <button class="modal-btn" onclick="resetZoom()">🔄 الحجم الأصلي</button>
            <button class="modal-btn close-btn" onclick="closeModal()">✖ إغلاق</button>
        </div>
        <div class="modal-img-wrapper">
            <img id="modalImg" class="modal-content" src="" alt="Zoomable Image">
        </div>
    </div>

    <script>
        let currentScale = 1;
        function openModal(imgUrl) {
            document.getElementById('imageModal').style.display = 'flex';
            document.getElementById('modalImg').src = imgUrl;
            resetZoom();
        }
        function closeModal() { document.getElementById('imageModal').style.display = 'none'; }
        function zoomIn() { currentScale += 0.25; applyZoom(); }
        function zoomOut() { if(currentScale > 0.5) { currentScale -= 0.25; applyZoom(); } }
        function resetZoom() { currentScale = 1; applyZoom(); }
        function applyZoom() { document.getElementById('modalImg').style.transform = `scale(${currentScale})`; }
        document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeModal(); });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة'
            
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    images = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    return render_template_string(DASHBOARD_TEMPLATE, username=session['user'], images=images)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
