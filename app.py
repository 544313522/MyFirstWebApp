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
    # 查询用户信息获取管理员状态
    user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
    is_admin = user_query.data[0]['is_admin'] if user_query.data else False
    
    return jsonify({
        "status": "success",
        "user": current_user,
        "authenticated": True,
        "is_admin": is_admin
    })

# 认证检查 API 路由
# 获取用户权限
@app.route('/api/users/<username>/permissions', methods=['GET'])
@jwt_required()
def get_user_permissions(username):
    current_user = get_jwt_identity()
    # 查询当前用户的管理员状态
    user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
    is_admin = user_query.data[0]['is_admin'] if user_query.data else False
    
    if not is_admin:
        return jsonify({"msg": "Unauthorized"}), 403
    
    # 查询用户权限
    permissions_query = supabase.table('user_permissions').select('*').eq('username', username).execute()
    
    # 如果没有权限记录，返回默认权限（所有非管理员功能可见）
    if not permissions_query.data:
        # 获取所有非管理员功能模块ID
        modules = {
            'youtube-downloader': True, 
            'whisper-ai': True, 
            'translator': True, 
            'summarizer': True, 
            'snake-game': True, 
            'spaceship': True, 
            'module-1': True, 
            'module-2': True, 
            'module-3': True, 
            'module-4': True
        }
        return jsonify(modules), 200
    
    # 移除不需要的字段并转换字段名
    permissions = {}
    raw_permissions = permissions_query.data[0]
    
    # 将数据库中的下划线格式转换为前端使用的连字符格式
    for key, value in raw_permissions.items():
        if key not in ['id', 'username']:
            # 将 youtube_downloader 转换为 youtube-downloader
            frontend_key = key.replace('_', '-')
            permissions[frontend_key] = value
    
    print(f"返回用户 {username} 的权限: {permissions}")  # 调试日志
    return jsonify(permissions), 200

# 更新用户权限
@app.route('/api/users/<username>/permissions', methods=['PUT'])
@jwt_required()
def update_user_permissions(username):
    current_user = get_jwt_identity()
    try:
        # 查询当前用户的管理员状态
        user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
        is_admin = user_query.data[0]['is_admin'] if user_query.data else False
        
        if not is_admin:
            return jsonify({"msg": "Unauthorized"}), 403
        
        data = request.get_json()
        
        # 检查用户是否存在
        user_exists = supabase.table('users').select('username').eq('username', username).execute()
        if not user_exists.data:
            return jsonify({"msg": "User not found"}), 404
        
        # 添加调试日志
        print(f"收到权限更新请求: 用户={username}, 数据={data}")
        
        # 检查是否已有权限记录
        permissions_query = supabase.table('user_permissions').select('*').eq('username', username).execute()
        
        try:
            if permissions_query.data:
                # 更新现有权限
                # 确保只更新权限字段，移除可能的其他字段
                update_data = {}
                for key, value in data.items():
                    # 只保留布尔值字段
                    if isinstance(value, bool) and key != 'username':
                        # 将连字符转换为下划线
                        db_key = key.replace('-', '_')
                        update_data[db_key] = value
                
                print(f"更新权限数据: {update_data}")
                result = supabase.table('user_permissions').update(update_data).eq('username', username).execute()
                print(f"更新结果: {result}")
            else:
                # 创建新权限记录
                insert_data = {'username': username}
                for key, value in data.items():
                    # 只保留布尔值字段
                    if isinstance(value, bool) and key != 'username':
                        # 将连字符转换为下划线
                        db_key = key.replace('-', '_')
                        insert_data[db_key] = value
                
                print(f"插入权限数据: {insert_data}")
                result = supabase.table('user_permissions').insert(insert_data).execute()
                print(f"插入结果: {result}")
            
            return jsonify({"msg": "Permissions updated successfully"}), 200
        except Exception as e:
            print(f"Supabase操作错误: {str(e)}")
            return jsonify({"msg": f"Database error: {str(e)}"}), 500
            
    except Exception as e:
        print(f"权限更新错误: {str(e)}")
        return jsonify({"msg": f"Error updating permissions: {str(e)}"}), 500

# 修改check-auth接口，返回用户权限
# 修改check-auth接口，确保权限字段名与前端匹配
@app.route('/api/check-auth')
@jwt_required()
def check_auth():
    current_user = get_jwt_identity()
    try:
        # 查询用户信息获取管理员状态
        user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
        
        # 确保 is_admin 是布尔类型
        is_admin = False
        if user_query.data:
            raw_value = user_query.data[0].get('is_admin')
            # 处理各种可能的值类型
            if isinstance(raw_value, bool):
                is_admin = raw_value
            elif isinstance(raw_value, str):
                is_admin = raw_value.lower() == 'true'
            elif isinstance(raw_value, (int, float)):
                is_admin = bool(raw_value)
        
        # 获取用户权限
        permissions = {}
        if not is_admin:  # 只有非管理员需要检查权限
            permissions_query = supabase.table('user_permissions').select('*').eq('username', current_user).execute()
            if permissions_query.data:
                # 移除不需要的字段
                raw_permissions = permissions_query.data[0]
                if 'id' in raw_permissions:
                    del raw_permissions['id']
                if 'username' in raw_permissions:
                    del raw_permissions['username']
                
                # 将下划线格式转换为连字符格式，以匹配前端菜单ID
                for key, value in raw_permissions.items():
                    # 将 youtube_downloader 转换为 youtube-downloader
                    frontend_key = key.replace('_', '-')
                    permissions[frontend_key] = value
        
        print(f"用户权限数据: {permissions}")  # 调试日志
        
        return jsonify({
            "status": "success",
            "msg": "Authorized", 
            "user": current_user,
            "is_admin": is_admin,
            "permissions": permissions,
            "authenticated": True
        }), 200
    except Exception as e:
        print(f"Auth check error: {str(e)}")  # 错误日志
        return jsonify({
            "status": "error",
            "msg": "Error checking authorization",
            "user": current_user,
            "is_admin": False,
            "authenticated": False
        }), 500

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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user_query = supabase.table('users').select('*').eq('username', username).execute()
    if not user_query.data or not check_password_hash(user_query.data[0]['password'], password):
        return jsonify({"msg": "Bad username or password"}), 401
    
    # 获取用户的管理员状态
    is_admin = user_query.data[0]['is_admin']
    
    # 生成访问令牌
    access_token = create_access_token(identity=username)
    response_data = {
        "access_token": access_token,
        "redirect": '/dashboard'  # 所有用户都重定向到仪表板
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
    try:
        # 查询当前用户的管理员状态
        user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
        
        # 使用相同的类型转换逻辑
        is_admin = False
        if user_query.data:
            raw_value = user_query.data[0].get('is_admin')
            if isinstance(raw_value, bool):
                is_admin = raw_value
            elif isinstance(raw_value, str):
                is_admin = raw_value.lower() == 'true'
            elif isinstance(raw_value, (int, float)):
                is_admin = bool(raw_value)
        
        if not is_admin:
            return jsonify({"msg": "Unauthorized"}), 403
        
        users = supabase.table('users').select('username,is_admin').execute()
        return jsonify(users.data), 200
    except Exception as e:
        print(f"Get users error: {str(e)}")  # 错误日志
        return jsonify({"msg": "Error fetching users"}), 500

@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    # 查询当前用户的管理员状态
    user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
    is_admin = user_query.data[0]['is_admin'] if user_query.data else False
    
    if not is_admin:
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
    # 查询当前用户的管理员状态
    user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
    is_admin = user_query.data[0]['is_admin'] if user_query.data else False
    
    if not is_admin:
        return jsonify({"msg": "Unauthorized"}), 403
    
    if username == 'admin':
        return jsonify({"msg": "Cannot delete admin user"}), 400
    
    result = supabase.table('users').delete().eq('username', username).execute()
    return jsonify({"msg": "User deleted successfully"}), 200

@app.route('/api/users/<username>/password', methods=['PUT'])
@jwt_required()
def update_user_password(username):
    current_user = get_jwt_identity()
    # 查询当前用户的管理员状态
    user_query = supabase.table('users').select('is_admin').eq('username', current_user).execute()
    is_admin = user_query.data[0]['is_admin'] if user_query.data else False
    
    if not is_admin:
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

# 在现有路由下添加
@app.route('/snake-game')
@jwt_required()
def snake_game():
    return render_template('snake_game.html')

# 应用入口点
if __name__ == '__main__':
    # 本地开发使用 5001 端口，Vercel 会自动分配端口
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port)