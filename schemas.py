from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 枚举类型
class DeviceTypeEnum(str, Enum):
    LIGHT = "灯光"
    AIR_CONDITIONER = "空调"
    REFRIGERATOR = "冰箱"
    TV = "电视"
    SECURITY_CAMERA = "安防摄像头"
    DOOR_LOCK = "智能门锁"
    SPEAKER = "智能音箱"
    OTHER = "其他"

class SecurityEventTypeEnum(str, Enum):
    INTRUSION = "入侵检测"
    FIRE = "火灾报警"
    GAS_LEAK = "燃气泄漏"
    WATER_LEAK = "水浸检测"
    DOOR_OPEN = "门窗异常开启"
    OTHER = "其他"

# 用户模式
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    house_area: Optional[float] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 设备模式
class DeviceBase(BaseModel):
    name: str
    device_type: DeviceTypeEnum
    model: Optional[str] = None
    serial_number: str
    location: Optional[str] = None
    status: bool = True
    owner_id: int

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 使用记录模式
class UsageRecordBase(BaseModel):
    user_id: int
    device_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # 分钟
    power_consumption: Optional[float] = None  # kWh

class UsageRecordCreate(UsageRecordBase):
    pass

class UsageRecord(UsageRecordBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# 安防事件模式
class SecurityEventBase(BaseModel):
    user_id: int
    event_type: SecurityEventTypeEnum
    description: str
    location: Optional[str] = None
    is_handled: bool = False
    occurred_at: Optional[datetime] = None

class SecurityEventCreate(SecurityEventBase):
    pass

class SecurityEvent(SecurityEventBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# 用户反馈模式
class FeedbackBase(BaseModel):
    user_id: int
    title: str
    content: str
    rating: int = Field(..., ge=1, le=5)  # 评分1-5
    is_resolved: bool = False

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 数据分析响应模式
class DeviceUsageFrequency(BaseModel):
    device_id: int
    device_name: str
    device_type: str
    usage_count: int
    total_duration: float
    avg_duration: float

class UserHabit(BaseModel):
    user_id: int
    user_name: str
    preferred_devices: List[str]
    usage_patterns: dict
    peak_usage_times: List[str]

class AreaImpact(BaseModel):
    house_area_range: str
    avg_device_count: float
    popular_devices: List[str]
    avg_usage_duration: float

# 数据可视化响应模式
class DeviceUsageData(BaseModel):
    labels: List[str]  # 设备名称或类型
    datasets: List[dict]  # 包含数据点和显示设置

class SecurityEventData(BaseModel):
    labels: List[str]  # 事件类型或时间段
    datasets: List[dict]  # 包含数据点和显示设置

class UserFeedbackData(BaseModel):
    labels: List[str]  # 反馈类别或时间段
    datasets: List[dict]  # 包含数据点和显示设置