"""
校园二手闲置市场 - FastAPI 后端
接口清单(共9个):
    POST   /api/register        注册(加分项1)
    POST   /api/login           登录(必做)
    GET    /api/items           物品列表,支持keyword搜索/分类筛选/分页(必做+加分项2/3)
    GET    /api/items/{id}      物品详情(必做)
    POST   /api/items           发布物品(必做)
    PUT    /api/items/{id}      修改自己的物品/更新状态(必做+加分项4)
    DELETE /api/items/{id}      删除自己的物品(必做)
    GET    /api/my/items        我发布的物品(必做)
    POST   /api/ai/description  AI生成物品描述(加分项5)
"""
import hashlib
import math
import os

import pymysql
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="校园二手闲置市场 API")

# 前端(5173端口)与后端(8000端口)源不同,属于跨域请求,必须放开CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接配置(每次请求新建连接,用完即关,简单可靠)
# 通过环境变量配置,未设置时使用默认值;参考 backend/.env.example
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "secondhand"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,  # 查询结果直接返回dict
}

# AI接口配置(加分项5):通过环境变量配置,未配置时自动降级为本地模板生成
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.deepseek.com/v1")
AI_MODEL = os.environ.get("AI_MODEL", "deepseek-chat")


def get_db():
    """获取一个新的数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def hash_password(password: str) -> str:
    """密码用SHA256摘要后存储,数据库中不保存明文"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ---------------- 请求体模型 ----------------

class UserIn(BaseModel):
    """登录/注册的请求体:前端把表单里的用户名密码原样传过来"""
    username: str
    password: str


class ItemIn(BaseModel):
    """发布物品的请求体,user_id由前端从localStorage带上(本课程的简易登录方案)"""
    title: str
    description: str = ""
    price: float = 0
    category: str = ""
    image_url: str = ""
    user_id: int


class ItemUpdate(BaseModel):
    """修改物品的请求体,所有字段可选,只更新传了的字段"""
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    image_url: str | None = None
    status: str | None = None  # 在售 / 已售
    user_id: int


class AiIn(BaseModel):
    """AI生成描述的请求体:只需要物品名称和分类两个信息"""
    title: str
    category: str = ""


# ---------------- 用户相关接口 ----------------

@app.post("/api/register")
def register(data: UserIn):
    """注册新用户(加分项1):用户名不能重复,密码SHA256后入库"""
    if not data.username.strip() or not data.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 先查重
            cursor.execute("SELECT id FROM users WHERE username=%s", (data.username.strip(),))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="用户名已存在")
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (data.username.strip(), hash_password(data.password)),
            )
        conn.commit()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username=%s", (data.username.strip(),))
            row = cursor.fetchone()
        return {"id": row["id"], "username": data.username.strip(), "message": "注册成功"}
    finally:
        conn.close()


@app.post("/api/login")
def login(data: UserIn):
    """登录(必做):校验通过后返回用户ID,前端存入localStorage保持登录态"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password FROM users WHERE username=%s",
                (data.username.strip(),),
            )
            user = cursor.fetchone()
        # 用户不存在或密码摘要不一致都统一报"用户名或密码错误",避免暴露用户是否存在
        if not user or user["password"] != hash_password(data.password):
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        return {"id": user["id"], "username": user["username"], "message": "登录成功"}
    finally:
        conn.close()


# ---------------- 物品相关接口 ----------------

# 列表/详情统一查询字段:created_at格式化成字符串,前端直接展示
ITEM_FIELDS = "id, title, description, price, category, image_url, status, user_id, DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i') AS created_at"


@app.get("/api/items")
def list_items(
    keyword: str = "",
    category: str = "",
    page: int = 1,
    page_size: int = 5,
):
    """物品列表(必做+加分项2/3):支持标题关键词搜索、分类筛选、分页(每页默认5条)"""
    # 防御性校验:页码至少为1,每页条数限制在1~50之间,防止恶意传参
    page = max(page, 1)
    page_size = min(max(page_size, 1), 50)

    # 按需要动态拼接WHERE条件:两个筛选都为空时查全表
    where = []
    params = []
    if keyword.strip():
        where.append("title LIKE %s")
        params.append(f"%{keyword.strip()}%")
    if category.strip():
        where.append("category=%s")
        params.append(category.strip())
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 先查总数,用于计算总页数
            cursor.execute(f"SELECT COUNT(*) AS total FROM items {where_sql}", params)
            total = cursor.fetchone()["total"]
            # 再查当前页数据,按发布时间倒序,最新的在最前
            cursor.execute(
                f"SELECT {ITEM_FIELDS} FROM items {where_sql} "
                f"ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
                (*params, page_size, (page - 1) * page_size),
            )
            rows = cursor.fetchall()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": math.ceil(total / page_size) if total else 0,
            "items": rows,
        }
    finally:
        conn.close()


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    """物品详情(必做)"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT {ITEM_FIELDS} FROM items WHERE id=%s", (item_id,))
            item = cursor.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="物品不存在")
        return item
    finally:
        conn.close()


@app.post("/api/items")
def create_item(data: ItemIn):
    """发布物品(必做):user_id由前端带上,代表当前登录用户"""
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="标题不能为空")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 校验user_id是否真实存在,防止前端传入非法用户
            cursor.execute("SELECT id FROM users WHERE id=%s", (data.user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail="用户不存在,请重新登录")
            cursor.execute(
                "INSERT INTO items (title, description, price, category, image_url, user_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (data.title.strip(), data.description, data.price, data.category, data.image_url, data.user_id),
            )
        conn.commit()
        new_id = cursor.lastrowid
        return {"id": new_id, "message": "发布成功"}
    finally:
        conn.close()


@app.put("/api/items/{item_id}")
def update_item(item_id: int, data: ItemUpdate):
    """修改自己的物品(必做)/更新在售状态(加分项4):只能改自己发布的物品"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM items WHERE id=%s", (item_id,))
            item = cursor.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="物品不存在")
            if item["user_id"] != data.user_id:
                raise HTTPException(status_code=403, detail="只能修改自己发布的物品")

            # 动态拼接SET子句:只更新请求里传了的字段,防止把没传的字段清空
            updates = {
                "title": data.title,
                "description": data.description,
                "price": data.price,
                "category": data.category,
                "image_url": data.image_url,
                "status": data.status,
            }
            set_sql = ", ".join(f"{k}=%s" for k, v in updates.items() if v is not None)
            values = [v for v in updates.values() if v is not None]
            if not values:
                raise HTTPException(status_code=400, detail="没有需要更新的字段")
            if data.status is not None and data.status not in ("在售", "已售"):
                raise HTTPException(status_code=400, detail="状态只能是:在售/已售")
            cursor.execute(f"UPDATE items SET {set_sql} WHERE id=%s", (*values, item_id))
        conn.commit()
        return {"message": "修改成功"}
    finally:
        conn.close()


@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, user_id: int):
    """删除自己的物品(必做):只能删除自己发布的物品"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM items WHERE id=%s", (item_id,))
            item = cursor.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="物品不存在")
            if item["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="只能删除自己发布的物品")
            cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
        conn.commit()
        return {"message": "删除成功"}
    finally:
        conn.close()


@app.get("/api/my/items")
def my_items(user_id: int, page: int = 1, page_size: int = 5):
    """我发布的物品(必做):按user_id过滤,同样支持分页"""
    page = max(page, 1)  # 页码至少为1,和列表接口保持一致
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM items WHERE user_id=%s", (user_id,))
            total = cursor.fetchone()["total"]
            cursor.execute(
                f"SELECT {ITEM_FIELDS} FROM items WHERE user_id=%s "
                f"ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
                (user_id, page_size, (page - 1) * page_size),
            )
            rows = cursor.fetchall()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": math.ceil(total / page_size) if total else 0,
            "items": rows,
        }
    finally:
        conn.close()


# ---------------- AI辅助接口(加分项5) ----------------

@app.post("/api/ai/description")
def ai_description(data: AiIn):
    """AI生成物品描述(加分项5):
    配置了AI_API_KEY环境变量时调用大模型接口;未配置时降级为本地模板生成,保证功能可演示。
    """
    prompt = (
        f"请为校园二手闲置物品写一段出售描述,80字以内,语气亲切自然。"
        f"物品名称:{data.title};分类:{data.category or '未分类'}。"
        f"只输出描述正文,不要任何解释。"
    )
    if AI_API_KEY:
        try:
            resp = requests.post(
                f"{AI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AI_API_KEY}"},
                json={
                    "model": AI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                },
                timeout=15,
            )
            content = resp.json()["choices"][0]["message"]["content"]
            return {"source": "ai", "description": content.strip()}
        except Exception:
            # 网络或接口异常时降级到模板,不让前端报错
            pass

    # 本地模板兜底:根据分类拼接一段通用的出售文案
    category_text = data.category or "闲置"
    return {
        "source": "template",
        "description": (
            f"【{category_text}】{data.title},自用闲置出,成色良好,功能正常。"
            f"校园内可当面交易验货,价格合理,诚心要可小刀,先到先得!"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
