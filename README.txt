========================================
 校园二手闲置市场 - 安装与启动说明
========================================
技术栈:Python 3.12 + FastAPI + MySQL 8.x + Vue 3 + Axios
(实际开发使用的Python为3.13,兼容)

一、环境准备
----------------------------------------
1. 安装 Python 3.12+(命令行输入 python --version 能正常显示)
2. 安装 Node.js 18+(命令行输入 node --version 能正常显示)
3. 安装并启动 MySQL 8.x 服务

二、初始化数据库(只需做一次)
----------------------------------------
方法1(命令行):
  mysql -u root -p < backend\schema.sql
  输入root密码后自动建库、建表、插入预置账号和示例数据。

方法2(图形界面):
  用 Navicat / MySQL Workbench 打开 backend\schema.sql,直接执行。

执行后将得到:
  数据库 secondhand
  预置账号 user1 / 123456、user2 / 123456
  12条示例物品数据

三、启动后端(FastAPI,端口8000)
----------------------------------------
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py

(.venv是本项目专属的虚拟环境,依赖只装在里面,不污染全局Python;
 直接用 .venv\Scripts\ 下的完整路径运行,无需执行activate激活。)

看到 "Uvicorn running on http://127.0.0.1:8000" 即启动成功。
接口文档(可选):浏览器打开 http://127.0.0.1:8000/docs

注意:backend\main.py 中 DB_CONFIG 的数据库密码默认为 123456,
如你的MySQL密码不同,请修改 main.py 第40行附近的 password 字段。

四、启动前端(Vue 3,端口5173)
----------------------------------------
cd frontend
npm install
npm run dev

看到 "Local: http://localhost:5173/" 后,浏览器打开:
  http://localhost:5173

五、功能演示顺序建议
----------------------------------------
1. 登录页:用 user1 / 123456 登录(或注册新账号,加分项)
2. 首页:浏览列表、搜索关键词(如"iPad")、点分类标签筛选、翻页(每页5条)
3. 点击物品进详情页
4. 导航栏"发布闲置":填写信息,可点"AI生成描述"按钮自动生成文案
5. 导航栏"我的管理":编辑、删除、一键"标记已售/重新上架"
6. 退出登录后,发布/管理页面会跳回登录页(未登录不能发布)

六、目录结构
----------------------------------------
campus-market/
├── backend/
│   ├── main.py           全部后端接口
│   ├── schema.sql        建库建表脚本
│   └── requirements.txt  Python依赖
├── frontend/
│   ├── src/components/   5个页面组件
│   ├── src/api.js        axios封装
│   └── package.json
└── README.txt            本文件
