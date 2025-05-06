from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'rahasia'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inisialisasi tabel-tabel di database
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        nama TEXT NOT NULL,
        password TEXT NOT NULL
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS biodata (
        email TEXT PRIMARY KEY,
        nama_lengkap TEXT,
        tanggal_lahir TEXT,
        umur INTEGER,
        tempat_tinggal TEXT,
        nik TEXT,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY(email) REFERENCES users(email)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS komoditas (
        email TEXT PRIMARY KEY,
        komoditas TEXT,
        luas TEXT,
        FOREIGN KEY(email) REFERENCES users(email)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS hasil_panen (
        email TEXT PRIMARY KEY,
        komoditas TEXT,
        bulan TEXT,
        hasil TEXT,
        FOREIGN KEY(email) REFERENCES users(email)
    )''')

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        nama = request.form['nama']
        password = request.form['password']
        with get_db_connection() as conn:
            conn.execute('INSERT INTO users (email, nama, password) VALUES (?, ?, ?)',
                         (email, nama, password))
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                                (email, password)).fetchone()
        if user:
            session['user'] = email
            return redirect('/home')
        return 'Login gagal'
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    email = session['user']
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        data_biodata = conn.execute('SELECT * FROM biodata WHERE email = ?', (email,)).fetchone()
        data_komoditas = conn.execute('SELECT * FROM komoditas WHERE email = ?', (email,)).fetchone()
        data_hasil = conn.execute('SELECT * FROM hasil_panen WHERE email = ?', (email,)).fetchone()
    return render_template('home.html', nama=user['nama'], biodata=data_biodata,
                           komoditas=data_komoditas, hasil=data_hasil)

@app.route('/biodata', methods=['GET', 'POST'])
def biodata_view():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        email = session['user']
        data = (
            email,
            request.form['nama_lengkap'],
            request.form['tanggal_lahir'],
            request.form['umur'],
            request.form['tempat_tinggal'],
            request.form['nik'],
            request.form['latitude'],
            request.form['longitude']
        )
        with get_db_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO biodata 
                (email, nama_lengkap, tanggal_lahir, umur, tempat_tinggal, nik, latitude, longitude) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
        return redirect('/home')
    return render_template('biodata.html')

@app.route('/komoditas', methods=['GET', 'POST'])
def komoditas():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        email = session['user']
        komoditas = request.form['komoditas']
        luas = request.form['luas']
        with get_db_connection() as conn:
            conn.execute('INSERT OR REPLACE INTO komoditas (email, komoditas, luas) VALUES (?, ?, ?)',
                         (email, komoditas, luas))
        return redirect('/home')
    return render_template('komoditas.html')

@app.route('/hasil_panen', methods=['GET', 'POST'])
def hasil_panen():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        email = session['user']
        komoditas = request.form['komoditas']
        bulan = request.form['bulan']
        hasil = request.form['hasil']
        with get_db_connection() as conn:
            conn.execute('INSERT OR REPLACE INTO hasil_panen (email, komoditas, bulan, hasil) VALUES (?, ?, ?, ?)',
                         (email, komoditas, bulan, hasil))
        return redirect('/home')
    return render_template('hasil_panen.html')

@app.route('/admin')
def admin_monitor():
    if 'user' not in session:
        return redirect('/login')
    with get_db_connection() as conn:
        biodata_all = conn.execute('SELECT * FROM biodata').fetchall()
        komoditas_all = conn.execute('SELECT * FROM komoditas').fetchall()
        hasil_all = conn.execute('SELECT * FROM hasil_panen').fetchall()
    return render_template('admin.html', biodata=biodata_all, komoditas=komoditas_all, hasil=hasil_all)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
