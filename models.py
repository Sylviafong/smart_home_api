from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from database import Base, engine

# 设备类型枚举
class DeviceType(enum.Enum):
    LIGHT = "灯光"
    AIR_CONDITIONER = "空调"
    REFRIGERATOR = "冰箱"
    TV = "电视"
    SECURITY_CAMERA = "安防摄像头"
    DOOR_LOCK = "智能门锁"
    SPEAKER = "智能音箱"
    OTHER = "其他"

# 安防事件类型枚举
class SecurityEventType(enum.Enum):
    INTRUSION = "入侵检测"
    FIRE = "火灾报警"
    GAS_LEAK = "燃气泄漏"
    WATER_LEAK = "水浸检测"
    DOOR_OPEN = "门窗异常开启"
    OTHER = "其他"

# 用户表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone = Column(String)
    address = Column(String)
    house_area = Column(Float)  # 房屋面积，单位平方米
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    devices = relationship("Device", back_populates="owner")
    usage_records = relationship("UsageRecord", back_populates="user")
    security_events = relationship("SecurityEvent", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")

# 设备表
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    device_type = Column(Enum(DeviceType))
    model = Column(String)
    serial_number = Column(String, unique=True)
    location = Column(String)  # 设备在家中的位置
    status = Column(Boolean, default=True)  # 设备状态：开/关
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    owner = relationship("User", back_populates="devices")
    usage_records = relationship("UsageRecord", back_populates="device")

# 使用记录表
class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Float)  # 使用时长，单位分钟
    power_consumption = Column(Float)  # 能耗，单位kWh
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    user = relationship("User", back_populates="usage_records")
    device = relationship("Device", back_populates="usage_records")

# 安防事件表
class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(Enum(SecurityEventType))
    description = Column(Text)
    location = Column(String)  # 事件发生位置
    is_handled = Column(Boolean, default=False)  # 是否已处理
    occurred_at = Column(DateTime, default=datetime.now)  # 事件发生时间
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    user = relationship("User", back_populates="security_events")

# 用户反馈表
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    rating = Column(Integer)  # 评分 1-5
    is_resolved = Column(Boolean, default=False)  # 是否已解决
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    user = relationship("User", back_populates="feedbacks")