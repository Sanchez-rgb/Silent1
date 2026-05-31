"""Word转PDF服务 - 完整版"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Cookie, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
import shutil
import tempfile
import zipfile
import uuid
import hashlib
import secrets
import json

from db import (
    init_db, get_session, User, ConversionRecord, ApiKey, DailyUsage,
    hash_password, verify_password, generate_api_key
)
from converter import DocumentConverter, ConverterError

# 初始化数据库
init_db()

app = FastAPI(
    title="Word转PDF服务",
    description="专业的Word转PDF转换平台，支持免费试用和付费会员",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建临时目录
TEMP_DIR = tempfile.mkdtemp(prefix="w2p_")

# 定价配置
PRICING = {
    "per_conversion": 1.0,  # 单次付费
    "monthly": 9.9,          # 月度会员
    "yearly": 99.0,          # 年度会员
    "enterprise": 99.0,       # 企业版每月
}


# ==================== 工具函数 ====================

def get_client_id(cookie_client_id: Optional[str] = None) -> str:
    """获取客户端标识"""
    if cookie_client_id:
        return f"cookie:{cookie_client_id}"
    return f"ip:{uuid.getnode()}"


def check_usage_limit(client_id: str, user: Optional[User] = None) -> tuple:
    """检查使用限制"""
    # 已登录用户
    if user:
        if user.is_subscription_active():
            return True, "unlimited", "会员无限次"
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        session = get_session()
        today_count = session.query(ConversionRecord).filter(
            ConversionRecord.user_id == user.id,
            ConversionRecord.created_at >= today_start,
            ConversionRecord.status == 'completed'
        ).count()
        
        remaining = max(0, 3 - today_count)
        return remaining > 0, remaining, f"剩余{remaining}次"
    
    # 未登录用户 - 基于Cookie
    identifier = f"visitor:{client_id}"
    remaining = max(0, 3 - DailyUsage.get_daily_usage(identifier))
    return remaining > 0, remaining, f"剩余{remaining}次"


def record_usage(client_id: str, user: Optional[User] = None):
    """记录使用"""
    if user:
        # 用户已登录，在转换时记录
        pass
    else:
        identifier = f"visitor:{client_id}"
        DailyUsage.increment_usage(identifier)


# ==================== Pydantic模型 ====================

class LoginRequest(BaseModel):
    phone: str
    password: str

class RegisterRequest(BaseModel):
    phone: str
    password: str
    code: str = "123456"  # 简化验证码

class PaymentRequest(BaseModel):
    amount: float
    payment_type: str  # per_conversion, monthly, yearly, enterprise
    user_id: Optional[int] = None

class ApiKeyRequest(BaseModel):
    company_name: str
    quota: int = 1000


# ==================== API端点 ====================

@app.get("/")
async def root():
    """返回前端页面"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return {"message": "Word转PDF服务 API", "version": "2.0.0"}


@app.get("/api/status")
async def get_status(
    client_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """获取当前状态"""
    session = get_session()
    user = None
    
    # 检查是否是企业API用户
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        key = authorization.replace("Bearer ", "")
        api_key = session.query(ApiKey).filter_by(api_key=key, is_active=True).first()
    
    if api_key:
        return {
            "type": "enterprise",
            "company": api_key.company_name,
            "quota": api_key.monthly_quota,
            "used": api_key.used_count,
            "remaining": api_key.monthly_quota - api_key.used_count
        }
    
    # 检查普通用户
    return {
        "type": "free",
        "remaining": 3,
        "message": "免费用户每天3次"
    }


@app.post("/api/convert")
async def convert_document(
    file: UploadFile = File(...),
    client_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """转换文档"""
    session = get_session()
    
    # 检查文件类型
    if not file.filename.endswith(('.doc', '.docx')):
        raise HTTPException(status_code=400, detail="仅支持.doc和.docx文件")
    
    # 检查企业API
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        key = authorization.replace("Bearer ", "")
        api_key = session.query(ApiKey).filter_by(api_key=key, is_active=True).first()
        
        if api_key:
            if not api_key.can_use():
                raise HTTPException(status_code=403, detail="企业额度已用完")
            
            # 记录转换
            record = ConversionRecord(
                user_id=api_key.user_id,
                file_name=file.filename,
                original_filename=file.filename,
                status='pending'
            )
            session.add(record)
            api_key.used_count += 1
            session.commit()
    
    # 保存上传的文件
    file_id = str(uuid.uuid4())
    docx_path = os.path.join(TEMP_DIR, f"{file_id}.docx")
    
    with open(docx_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 转换
    try:
        converter = DocumentConverter()
        pdf_path = converter.convert_docx_to_pdf(docx_path, os.path.join(TEMP_DIR, f"{file_id}.pdf"))
        
        # 更新记录
        if record:
            record.status = 'completed'
            session.commit()
        
        # 删除原文件
        os.remove(docx_path)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=file.filename.replace('.doc', '').replace('.docx', '') + ".pdf",
            background=None
        )
        
    except ConverterError as e:
        if record:
            record.status = 'failed'
            session.commit()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        if record:
            record.status = 'failed'
            session.commit()
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


@app.post("/api/register")
async def register(request: RegisterRequest):
    """用户注册"""
    session = get_session()
    
    # 检查手机号是否已注册
    existing = session.query(User).filter_by(phone=request.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="手机号已注册")
    
    # 创建用户
    user = User(
        phone=request.phone,
        password_hash=hash_password(request.password)
    )
    session.add(user)
    session.commit()
    
    return {"success": True, "message": "注册成功", "user_id": user.id}


@app.post("/api/login")
async def login(request: LoginRequest):
    """用户登录"""
    session = get_session()
    
    user = session.query(User).filter_by(phone=request.phone).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    
    # 生成简单token
    token = secrets.token_hex(16)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "is_vip": user.is_vip,
            "vip_type": user.vip_type,
            "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None
        }
    }


@app.get("/api/user/info")
async def get_user_info(authorization: Optional[str] = Header(None)):
    """获取用户信息"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    
    session = get_session()
    token = authorization.replace("Bearer ", "")
    # 简化：直接用user_id
    try:
        user_id = int(token[:8], 16) % 100000
        user = session.query(User).filter_by(id=user_id).first()
    except:
        # 从数据库查询（实际应该用JWT）
        users = session.query(User).all()
        user = users[0] if users else None
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算今日使用次数
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = session.query(ConversionRecord).filter(
        ConversionRecord.user_id == user.id,
        ConversionRecord.created_at >= today_start,
        ConversionRecord.status == 'completed'
    ).count()
    
    return {
        "id": user.id,
        "phone": user.phone,
        "is_vip": user.is_subscription_active(),
        "vip_type": user.vip_type,
        "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None,
        "today_used": today_count,
        "daily_limit": 3
    }


@app.post("/api/create_payment")
async def create_payment(request: PaymentRequest):
    """创建支付（模拟）"""
    # 生成支付订单
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(4)}"
    
    # 模拟支付链接
    payment_url = f"/payment/simulate?order_id={order_id}&amount={request.amount}"
    
    return {
        "order_id": order_id,
        "payment_url": payment_url,
        "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={order_id}",
        "amount": request.amount,
        "status": "pending"
    }


@app.get("/payment/simulate")
async def simulate_payment(
    order_id: str,
    amount: float
):
    """模拟支付回调"""
    return {
        "status": "success",
        "order_id": order_id,
        "amount": amount,
        "message": "支付成功（模拟）",
        "payment_time": datetime.now().isoformat()
    }


@app.post("/api/payment_callback")
async def payment_callback(
    order_id: str,
    amount: float,
    status: str = "success"
):
    """支付回调"""
    if status != "success":
        return {"success": False, "message": "支付失败"}
    
    session = get_session()
    
    # 根据金额处理
    if amount == 1.0:
        # 单次付费 - 直接给1次额度（通过记录实现）
        return {"success": True, "message": "支付成功，获得1次转换额度"}
    
    elif amount == 9.9:
        # 月度会员
        # 简化：创建或更新测试用户
        user = session.query(User).first()
        if not user:
            user = User(phone="13800138000", password_hash=hash_password("123456"))
            session.add(user)
        
        user.is_vip = True
        user.vip_type = "monthly"
        user.expiry_date = datetime.utcnow() + timedelta(days=30)
        session.commit()
        
        return {"success": True, "message": "月度会员开通成功"}
    
    elif amount == 99.0:
        # 年度会员或企业版
        user = session.query(User).first()
        if not user:
            user = User(phone="13800138000", password_hash=hash_password("123456"))
            session.add(user)
        
        user.is_vip = True
        user.vip_type = "yearly"
        user.expiry_date = datetime.utcnow() + timedelta(days=365)
        session.commit()
        
        return {"success": True, "message": "年度会员开通成功"}
    
    return {"success": True, "message": "支付处理完成"}


@app.post("/api/enterprise/create_key")
async def create_api_key(
    request: ApiKeyRequest,
    authorization: Optional[str] = Header(None)
):
    """创建企业API密钥"""
    session = get_session()
    
    # 简化：直接创建（实际需要验证用户身份和VIP状态）
    user = session.query(User).first()
    if not user:
        user = User(phone="enterprise@test.com", password_hash=hash_password("enterprise123"))
        session.add(user)
        session.commit()
    
    api_key = generate_api_key()
    
    key_record = ApiKey(
        user_id=user.id,
        company_name=request.company_name,
        api_key=api_key,
        monthly_quota=request.quota
    )
    session.add(key_record)
    session.commit()
    
    return {
        "success": True,
        "api_key": api_key,
        "company_name": request.company_name,
        "monthly_quota": request.quota,
        "message": "请妥善保管API密钥"
    }


@app.get("/api/enterprise/usage")
async def get_enterprise_usage(
    authorization: Optional[str] = Header(None)
):
    """获取企业API使用情况"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="需要API密钥")
    
    session = get_session()
    key = authorization.replace("Bearer ", "")
    api_key = session.query(ApiKey).filter_by(api_key=key).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API密钥无效")
    
    return {
        "company_name": api_key.company_name,
        "monthly_quota": api_key.monthly_quota,
        "used_count": api_key.used_count,
        "remaining": api_key.monthly_quota - api_key.used_count,
        "period_start": api_key.current_period_start.isoformat()
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Word转PDF服务 v2.0.0")
    print("=" * 60)
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("=" * 60)
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
