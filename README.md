# MyFirstWebApp

[English](#english) | [中文](#chinese)

<a name="english"></a>
## 🌟 Overview
MyFirstWebApp is a Flask-based web application that provides user authentication and a multi-functional dashboard. Built with modern web technologies, it offers a secure and scalable platform for various utility tools.

## ✨ Features
- **User Authentication System**
  - JWT token authentication
  - Role-based access control (Admin/User)
  - Secure password storage
  - Multi-admin support

- **User Management (Admin Features)**
  - Create new users (with admin privileges option)
  - Delete users (with admin account protection)
  - Password reset functionality
  - User list and permission management

- **Utility Modules (In Development)**
  - YouTube Downloader
  - Whisper AI Integration
  - Translation Tools
  - Text Summarization

## 🛠 Tech Stack
### Backend
- Python 3.x
- Flask
- Flask-JWT-Extended
- Supabase

### Frontend
- HTML5
- Bootstrap 4.5
- Vanilla JavaScript

## 📋 Prerequisites
- Python 3.x
- pip
- Supabase Account

## 🚀 Installation
1. Clone the repository
   ```bash
   git clone <repository_url>
   cd MyFirstWebApp
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. Run the application
   ```bash
   python app.py
   ```
   The application will be available at http://localhost:5001

## 📖 Usage Guide
1. Visit `/create-admin` endpoint to create the first admin account
2. Log in with admin credentials
3. Create additional users through the user management interface
4. Regular users can access all features except user management

## 🔜 Roadmap
- [ ] Implement YouTube download functionality
- [ ] Integrate Whisper AI for speech recognition
- [ ] Add translation features
- [ ] Implement text summarization
- [ ] Add user activity logging
- [ ] Enhance UI/UX

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

<a name="chinese"></a>
## 🌟 项目概述
MyFirstWebApp 是一个基于 Flask 的 Web 应用程序，提供用户认证和多功能仪表板。它采用现代 Web 技术构建，为各种实用工具提供了一个安全且可扩展的平台。

## ✨ 功能特点
- **用户认证系统**
  - JWT token 认证
  - 基于角色的访问控制（管理员/用户）
  - 安全的密码存储
  - 支持多管理员

- **用户管理（管理员功能）**
  - 创建新用户（可设置管理员权限）
  - 删除用户（保护管理员账户）
  - 密码重置功能
  - 用户列表及权限管理

- **功能模块（开发中）**
  - YouTube 下载器
  - Whisper AI 集成
  - 翻译工具
  - 文本摘要

## 🛠 技术栈
### 后端
- Python 3.x
- Flask
- Flask-JWT-Extended
- Supabase

### 前端
- HTML5
- Bootstrap 4.5
- 原生 JavaScript

## 📋 环境要求
- Python 3.x
- pip
- Supabase 账户

## 🚀 安装步骤
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
   # 编辑 .env 文件，填入相应的配置
   ```

4. 运行应用
   ```bash
   python app.py
   ```
   应用将在 http://localhost:5001 启动

## 📖 使用说明
1. 访问 `/create-admin` 接口创建首个管理员账户
2. 使用管理员账户登录系统
3. 在用户管理界面创建其他用户
4. 普通用户登录后可以访问除用户管理外的其他功能

## 🔜 开发计划
- [ ] 实现 YouTube 下载功能
- [ ] 集成 Whisper AI 语音识别
- [ ] 添加翻译功能
- [ ] 实现文本摘要功能
- [ ] 添加用户操作日志
- [ ] 优化用户界面

## 🤝 贡献指南
欢迎提交贡献！请随时提交 Pull Request。

## 📄 许可证
本项目采用 MIT 许可证 - 详见 LICENSE 文件。