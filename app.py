# 导入所需的库和模块
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import timedelta
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 加载环境变量配置
load_dotenv()

# 初始化 Flask 应用
app = Flask(__name__, template_folder='templates')
# 启用跨域资源共享
CORS(app)

# JWT 配置
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # 从环境变量获取密钥
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Token 有效期为1小时
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Token 存储在请求头中
app.config['JWT_HEADER_NAME'] = 'Authorization'  # 请求头名称
app.config['JWT_HEADER_TYPE'] = 'Bearer'  # Token 类型

# 初始化 JWT 管理器
jwt = JWTManager(app)

# Supabase 数据库配置
SUPABASE_URL = os.getenv('SUPABASE_URL')  # 从环境变量获取数据库 URL
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # 从环境变量获取数据库密钥
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  # 创建数据库客户端

# 登录页面路由
@app.route('/')
def home():
    return render_template('login.html')

# 仪表板页面路由
@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

# 仪表板数据 API 路由
@app.route('/api/dashboard-data')
@jwt_required()  # 需要 JWT 认证
def dashboard_data():
    current_user = get_jwt_identity()  # 获取当前用户身份
    if current_user != 'admin':  # 验证是否为管理员
        return jsonify({"msg": "Unauthorized"}), 403
    return jsonify({
        "status": "success",
        "user": current_user,
        "authenticated": True
    })

# 认证检查 API 路由
@app.route('/api/check-auth')
@jwt_required()
def check_auth():
    current_user = get_jwt_identity()
    # 移除管理员检查，允许所有有效token的用户访问
    return jsonify({
        "msg": "Authorized", 
        "user": current_user,
        "is_admin": current_user == 'admin'
    }), 200

# 创建管理员账户路由
@app.route('/create-admin', methods=['POST'])
def create_admin():
    # 检查管理员是否已存在
    admin_query = supabase.table('users').select('*').eq('username', 'admin').execute()
    if len(admin_query.data) > 0:
        return jsonify({"msg": "Admin already exists"}), 400
    
    # 从环境变量获取管理员密码，如果未设置则返回错误
    admin_password = os.getenv("ADMIN_DEFAULT_PASSWORD")
    if not admin_password:
        return jsonify({"msg": "Admin password not configured"}), 500
    
    # 生成密码哈希
    hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
    # 创建管理员用户数据
    admin_user = {
        'username': 'admin',
        'password': hashed_password,
        'is_admin': True
    }
    
    # 将管理员数据插入数据库
    supabase.table('users').insert(admin_user).execute()
    return jsonify({"msg": "Admin user created successfully"}), 201

# 用户登录路由
@app.route('/login', methods=['POST'])
def login():
    # 获取登录表单数据
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 查询用户信息
    user_query = supabase.table('users').select('*').eq('username', username).execute()
    # 验证用户名和密码
    if not user_query.data or not check_password_hash(user_query.data[0]['password'], password):
        return jsonify({"msg": "Bad username or password"}), 401
    
    # 生成访问令牌
    access_token = create_access_token(identity=username)
    response_data = {
        "access_token": access_token,
        "redirect": '/dashboard' if username == 'admin' else '/'
    }
    return jsonify(response_data), 200

# 更新管理员密码路由
@app.route('/update-admin-password', methods=['POST'])
@jwt_required()
def update_admin_password():
    # 验证当前用户身份
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    
    # 从环境变量获取新密码，如果未设置则返回错误
    new_password = os.getenv("ADMIN_DEFAULT_PASSWORD")
    if not new_password:
        return jsonify({"msg": "Admin password not configured"}), 500
        
    # 生成新的密码哈希
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    # 更新数据库中的密码
    supabase.table('users').update({"password": hashed_password}).eq('username', 'admin').execute()
    
    return jsonify({"msg": "Admin password updated successfully"}), 200

# 删除管理员账户路由
@app.route('/delete-admin', methods=['POST'])
def delete_admin():
    # 从数据库中删除管理员账户
    result = supabase.table('users').delete().eq('username', 'admin').execute()
    return jsonify({"msg": "Admin user deleted successfully"}), 200

# 用户管理 API 路由
@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    
    # 获取所有用户列表，但不返回密码信息
    users = supabase.table('users').select('username,is_admin').execute()
    return jsonify(users.data), 200

@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    
    # 检查用户是否已存在
    user_query = supabase.table('users').select('*').eq('username', username).execute()
    if len(user_query.data) > 0:
        return jsonify({"msg": "Username already exists"}), 400
    
    # 生成密码哈希
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    # 创建新用户
    new_user = {
        'username': username,
        'password': hashed_password,  # 确保使用哈希后的密码
        'is_admin': is_admin
    }
    
    try:
        supabase.table('users').insert(new_user).execute()
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e:
        print(f"Error creating user: {e}")  # 添加错误日志
        return jsonify({"msg": "Error creating user"}), 500

@app.route('/api/users/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    
    if username == 'admin':
        return jsonify({"msg": "Cannot delete admin user"}), 400
    
    result = supabase.table('users').delete().eq('username', username).execute()
    return jsonify({"msg": "User deleted successfully"}), 200

@app.route('/api/users/<username>/password', methods=['PUT'])
@jwt_required()
def update_user_password(username):
    current_user = get_jwt_identity()
    if current_user != 'admin':
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password:
        return jsonify({"msg": "Missing new password"}), 400
    
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    supabase.table('users').update({"password": hashed_password}).eq('username', username).execute()
    
    return jsonify({"msg": "Password updated successfully"}), 200

@app.route('/users')
def users_page():
    return render_template('users.html')

# 应用入口点
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 在开发模式下运行应用，端口为 5001