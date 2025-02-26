from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import timedelta
from supabase import create_client, Client

app = Flask(__name__, template_folder='templates')
CORS(app)

# JWT配置
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

jwt = JWTManager(app)

# Supabase 配置
SUPABASE_URL = "https://bwfjfgisqshegxatwctb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3ZmpmZ2lzcXNoZWd4YXR3Y3RiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1Njg5NzEsImV4cCI6MjA1NjE0NDk3MX0.64RJOyjnDa9hjvqOg2nnho2HKPFSylHeseBfe6RthAo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
@jwt_required()
def dashboard_data():
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    return jsonify({
        "status": "success",
        "user": current_user,
        "authenticated": True
    })

@app.route('/api/check-auth')
@jwt_required()
def check_auth():
    current_user = get_jwt_identity()
    print(f"Checking auth for user: {current_user}")  # 调试日志
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    return jsonify({"msg": "Authorized", "user": current_user}), 200

@app.route('/create-admin', methods=['POST'])
def create_admin():
    admin_query = supabase.table('users').select('*').eq('username', 'admin').execute()
    if len(admin_query.data) > 0:
        return jsonify({"msg": "Admin already exists"}), 400
    
    hashed_password = generate_password_hash('123456', method='pbkdf2:sha256')
    admin_user = {
        'username': 'admin',
        'password': hashed_password,
        'is_admin': True
    }
    
    supabase.table('users').insert(admin_user).execute()
    return jsonify({"msg": "Admin user created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user_query = supabase.table('users').select('*').eq('username', username).execute()
    if not user_query.data or not check_password_hash(user_query.data[0]['password'], password):
        return jsonify({"msg": "Bad username or password"}), 401
    
    access_token = create_access_token(identity=username)
    response_data = {
        "access_token": access_token,
        "redirect": '/dashboard' if username == 'admin' else '/'
    }
    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)