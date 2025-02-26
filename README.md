# MyFirstWebApp

一个基于 Flask 的 Web 应用程序，提供用户认证和多功能仪表板。

## 功能特点

- 用户认证系统
  - JWT token 认证
  - 管理员和普通用户角色区分
  - 安全的密码存储

- 用户管理（仅管理员）
  - 创建新用户
  - 删除用户
  - 重置用户密码
  - 查看用户列表

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
