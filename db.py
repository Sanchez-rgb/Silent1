"""数据库模型和初始化"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import hashlib
import secrets

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_vip = Column(Boolean, default=False)  # 会员状态
    vip_type = Column(String(20), default='free')  # free, monthly, yearly, enterprise
    expiry_date = Column(DateTime, nullable=True)  # 到期时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversion_records = relationship('ConversionRecord', back_populates='user')
    api_keys = relationship('ApiKey', back_populates='user')
    
    def is_subscription_active(self):
        """检查会员是否有效"""
        if not self.is_vip or not self.expiry_date:
            return False
        return datetime.utcnow() < self.expiry_date
    
    def get_remaining_conversions(self):
        """获取剩余转换次数"""
        if self.is_subscription_active():
            return float('inf')  # 无限次
        
        # 计算今日使用次数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = len([r for r in self.conversion_records 
                          if r.created_at >= today_start and r.status == 'completed'])
        
        return max(0, 3 - today_count)  # 免费版每天3次


class ConversionRecord(Base):
    """转换记录表"""
    __tablename__ = 'conversion_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    file_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    status = Column(String(20), default='pending')  # pending, completed, failed
    is_paid = Column(Boolean, default=False)  # 是否付费
    payment_amount = Column(Float, default=0.0)  # 支付金额
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship('User', back_populates='conversion_records')


class ApiKey(Base):
    """API密钥表"""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_name = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    monthly_quota = Column(Integer, default=1000)  # 每月额度
    used_count = Column(Integer, default=0)  # 当月已使用
    current_period_start = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship('User', back_populates='api_keys')
    
    def get_monthly_usage(self):
        """获取当月使用量"""
        if datetime.utcnow() >= self.current_period_start + timedelta(days=30):
            return 0
        return self.used_count
    
    def can_use(self):
        """检查是否还能使用"""
        return self.is_active and self.used_count < self.monthly_quota


class DailyUsage(Base):
    """每日使用统计（用于免费用户追踪）"""
    __tablename__ = 'daily_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(String(255), nullable=False, index=True)  # 可以是cookie或user_id
    usage_date = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)
    
    @staticmethod
    def get_daily_usage(identifier):
        """获取今日使用次数"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        usage = Session.query(DailyUsage).filter(
            DailyUsage.identifier == identifier,
            DailyUsage.usage_date >= today_start
        ).first()
        
        return usage.usage_count if usage else 0
    
    @staticmethod
    def increment_usage(identifier):
        """增加使用次数"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        usage = Session.query(DailyUsage).filter(
            DailyUsage.identifier == identifier,
            DailyUsage.usage_date >= today_start
        ).first()
        
        if usage:
            usage.usage_count += 1
        else:
            usage = DailyUsage(identifier=identifier, usage_count=1)
            Session.add(usage)
        
        Session.commit()


def init_db(db_path='sqlite:///word2pdf.db'):
    """初始化数据库"""
    global engine, Session
    
    engine = create_engine(db_path, echo=False)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    
    return Session


def get_session():
    """获取数据库会话"""
    global Session
    if Session is None:
        init_db()
    return Session()


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash


def generate_api_key():
    """生成API密钥"""
    return secrets.token_hex(32)


def create_test_user(phone='13800138000', password='123456'):
    """创建测试用户"""
    session = get_session()
    user = session.query(User).filter_by(phone=phone).first()
    
    if not user:
        user = User(
            phone=phone,
            password_hash=hash_password(password)
        )
        session.add(user)
        session.commit()
    
    return user


# 全局变量
engine = None
Session = None

# 初始化数据库
init_db()
