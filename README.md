# MyFirstWebApp

一个基于 Flask 的 Web 应用程序，提供用户认证和多功能仪表板。

## 功能特点

- 用户认证系统
  - JWT token 认证
  - 管理员和普通用户角色区分
  - 安全的密码存储
  - 支持多管理员账户

- 用户管理（管理员功能）
  - 创建新用户（可设置管理员权限）
  - 删除用户（保护主管理员账户）
  - 重置用户密码
  - 查看用户列表及权限

- 功能模块（开发中）
  - YouTube 下载器
  - Whisper AI
  - 翻译工具
  - 文本摘要

## 技术栈

- 后端
  - Python 3.x
  - Flask
  - Flask-JWT-Extended
  - Supabase

- 前端
  - HTML5
  - Bootstrap 4.5
  - JavaScript (原生)

## 环境要求

- Python 3.x
- pip
- Supabase 账户

## 环境变量

需要在 `.env` 文件中配置以下环境变量：

```plaintext
JWT_SECRET_KEY=your_jwt_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_DEFAULT_PASSWORD=your_admin_password
```

## 安装步骤
1. 克隆项目
```bash
git clone <repository_url>
cd MyFirstWebApp
 ```

2. 安装依赖
```bash
pip install -r requirements.txt
 ```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入相应的值
 ```

4. 运行应用
```bash
python app.py
 ```

应用将在 http://localhost:5001 启动

## 使用说明
1. 首次运行时，访问 /create-admin 接口创建管理员账户
2. 使用管理员账户登录系统
3. 在用户管理界面创建其他用户
4. 普通用户登录后可以访问除用户管理外的其他功能
## 安全说明
- 所有密码都经过加密存储
- 使用 JWT 进行身份验证
- 接口访问权限严格控制
## 开发计划
- 实现 YouTube 下载功能
- 集成 Whisper AI 语音识别
- 添加翻译功能
- 实现文本摘要功能
- 添加用户操作日志
- 优化用户界面
```plaintext

这个 README.md 文件包含了项目的主要信息，包括功能特点、技术栈、安装步骤等。你可以根据需要进行补充和修改。
 ```
```