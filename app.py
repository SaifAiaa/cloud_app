import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
# مفتاح سري لتشفير الجلسات (يمكنك تغييره إن أردت)
app.secret_key = os.environ.get('SECRET_KEY', 'cyber_security_cloud_key_2026')

# بيانات الدخول المعينة للدكتور (يمكنك تغييرها هنا)
USER_CREDENTIALS = {
    'DrKarim': 'Cloud@2026'  # اسم المستخدم: DrKarim | كلمة المرور: cloud@2026
}

# مجلد التخزين السحابي للصور المرفوعة
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# إنشاء مجلد التخزين تلقائياً إن لم يكن موجوداً
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pw:
            session['logged_in'] = True
            session['username'] = user
            return redirect(url_for('dashboard'))
        else:
            error = "اسم المستخدم أو كلمة المرور غير صحيحة!"
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # جلب قائمة الصور المرفوعة حالياً في التخزين السحابي
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('dashboard.html', username=session.get('username'), images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
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
