# 校园二手闲置市场（Campus Market）

一个面向校园场景的二手闲置物品交易平台：支持注册登录、物品浏览/搜索/筛选/分页、发布与管理闲置，并集成 AI 一键生成物品描述。

## 功能特性

- 用户注册 / 登录（密码 SHA256 摘要存储）
- 物品列表：关键词搜索、分类筛选、分页（默认每页 5 条）
- 物品详情页
- 发布闲置，支持 AI 生成描述（未配置 AI 密钥时自动降级为本地模板）
- 我的管理：编辑、删除、一键标记已售 / 重新上架
- 未登录访问发布 / 管理页自动跳转登录

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | Python 3.12+ / FastAPI / Uvicorn / PyMySQL |
| 数据库 | MySQL 8.x |
| 前端 | Vue 3 / Vue Router / Axios / Vite |
| AI（可选） | DeepSeek 兼容的 OpenAI 风格接口 |

## 项目结构

```
campus-market/
├── backend/
│   ├── main.py            # 全部后端接口（9 个）
│   ├── schema.sql         # 建库建表 + 预置数据脚本
│   ├── requirements.txt   # Python 依赖
│   └── .env.example       # 环境变量示例
└── frontend/
    ├── src/
    │   ├── components/    # 5 个页面组件（登录/列表/详情/发布/我的管理）
    │   ├── api.js         # Axios 封装
    │   ├── App.vue
    │   └── main.js
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## 快速开始

### 1. 环境准备

- Python 3.12+（`python --version` 可正常输出）
- Node.js 18+（`node --version` 可正常输出）
- MySQL 8.x 服务已启动

### 2. 初始化数据库（只需一次）

命令行方式：

```bash
mysql -u root -p < backend/schema.sql
```

或用 Navicat / MySQL Workbench 打开 `backend/schema.sql` 直接执行。

执行后得到：

- 数据库 `secondhand`
- 预置账号：`user1 / 123456`、`user2 / 123456`
- 12 条示例物品数据（教材书籍 / 电子产品 / 生活用品 / 运动用品）

### 3. 配置环境变量（可选）

复制 `backend/.env.example` 为 `.env` 参考，按需设置环境变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DB_HOST` | `127.0.0.1` | 数据库地址 |
| `DB_USER` | `root` | 数据库用户 |
| `DB_PASSWORD` | 空 | 数据库密码 |
| `DB_NAME` | `secondhand` | 数据库名 |
| `AI_API_KEY` | 空 | AI 接口密钥，留空则用本地模板生成描述 |
| `AI_BASE_URL` | `https://api.deepseek.com/v1` | AI 接口地址 |
| `AI_MODEL` | `deepseek-chat` | AI 模型名 |

也可以直接修改 `backend/main.py` 中 `DB_CONFIG` 的默认值。

### 4. 启动后端（端口 8000）

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
.venv\Scripts\python main.py
```

> Linux / macOS 将上述路径换为 `.venv/bin/pip` 和 `.venv/bin/python`。

看到 `Uvicorn running on http://127.0.0.1:8000` 即启动成功，接口文档：http://127.0.0.1:8000/docs

### 5. 启动前端（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/register` | 注册 |
| POST | `/api/login` | 登录 |
| GET | `/api/items` | 物品列表（支持 `keyword` / `category` / `page` / `page_size`） |
| GET | `/api/items/{id}` | 物品详情 |
| POST | `/api/items` | 发布物品 |
| PUT | `/api/items/{id}` | 修改自己的物品 / 更新在售状态 |
| DELETE | `/api/items/{id}` | 删除自己的物品 |
| GET | `/api/my/items` | 我发布的物品 |
| POST | `/api/ai/description` | AI 生成物品描述 |

## 功能演示顺序建议

1. 登录页：用 `user1 / 123456` 登录（或注册新账号）
2. 首页：浏览列表、搜索关键词（如 “iPad”）、点分类标签筛选、翻页
3. 点击物品进入详情页
4. 导航栏 “发布闲置”：填写信息，可点 “AI 生成描述” 自动生成文案
5. 导航栏 “我的管理”：编辑、删除、一键 “标记已售 / 重新上架”
6. 退出登录后，发布 / 管理页面会跳回登录页

## 常见问题

- **数据库连接失败**：确认 MySQL 服务已启动，且 `DB_PASSWORD`（或 `main.py` 中的默认密码）与本机一致。
- **AI 生成描述返回模板文案**：未配置 `AI_API_KEY` 或 AI 接口异常时会自动降级为本地模板，属正常兜底行为。
- **前端请求报错**：确认后端已在 8000 端口运行；前后端跨域已在后端通过 CORS 中间件放开。
