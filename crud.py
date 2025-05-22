from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from datetime import datetime, timedelta
import models
import schemas
import hashlib
from typing import List, Dict, Any

# 用户相关CRUD操作
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # 简单密码哈希，生产环境应使用更安全的方法如bcrypt
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        address=user.address,
        house_area=user.house_area,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 设备相关CRUD操作
def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()

def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(
        name=device.name,
        device_type=device.device_type,
        model=device.model,
        serial_number=device.serial_number,
        location=device.location,
        status=device.status,
        owner_id=device.owner_id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

# 使用记录相关CRUD操作
def get_usage_record(db: Session, record_id: int):
    return db.query(models.UsageRecord).filter(models.UsageRecord.id == record_id).first()

def get_usage_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UsageRecord).offset(skip).limit(limit).all()

def create_usage_record(db: Session, usage_record: schemas.UsageRecordCreate):
    # 计算使用时长（如果未提供）
    duration = usage_record.duration
    if usage_record.end_time and not duration:
        # 计算时长（分钟）
        delta = usage_record.end_time - usage_record.start_time
        duration = delta.total_seconds() / 60
    
    db_record = models.UsageRecord(
        user_id=usage_record.user_id,
        device_id=usage_record.device_id,
        start_time=usage_record.start_time,
        end_time=usage_record.end_time,
        duration=duration,
        power_consumption=usage_record.power_consumption
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 安防事件相关CRUD操作
def get_security_event(db: Session, event_id: int):
    return db.query(models.SecurityEvent).filter(models.SecurityEvent.id == event_id).first()

def get_security_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SecurityEvent).offset(skip).limit(limit).all()

def create_security_event(db: Session, security_event: schemas.SecurityEventCreate):
    occurred_at = security_event.occurred_at or datetime.now()
    db_event = models.SecurityEvent(
        user_id=security_event.user_id,
        event_type=security_event.event_type,
        description=security_event.description,
        location=security_event.location,
        is_handled=security_event.is_handled,
        occurred_at=occurred_at
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# 用户反馈相关CRUD操作
def get_feedback(db: Session, feedback_id: int):
    return db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()

def get_feedbacks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(
        user_id=feedback.user_id,
        title=feedback.title,
        content=feedback.content,
        rating=feedback.rating,
        is_resolved=feedback.is_resolved
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# 数据分析功能
def analyze_device_usage_frequency(db: Session):
    """分析设备使用频率"""
    # 查询每个设备的使用次数、总时长和平均时长
    results = db.query(
        models.Device.id.label('device_id'),
        models.Device.name.label('device_name'),
        models.Device.device_type.label('device_type'),
        func.count(models.UsageRecord.id).label('usage_count'),
        func.sum(models.UsageRecord.duration).label('total_duration'),
        func.avg(models.UsageRecord.duration).label('avg_duration')
    ).join(models.UsageRecord).group_by(models.Device.id).all()
    
    # 转换为响应格式
    response = []
    for r in results:
        response.append({
            "device_id": r.device_id,
            "device_name": r.device_name,
            "device_type": str(r.device_type.value),
            "usage_count": r.usage_count,
            "total_duration": float(r.total_duration or 0),
            "avg_duration": float(r.avg_duration or 0)
        })
    
    return response

def analyze_user_habits(db: Session):
    """分析用户使用习惯"""
    # 获取所有用户
    users = get_users(db)
    response = []
    
    for user in users:
        # 查询用户最常使用的设备
        preferred_devices_query = db.query(
            models.Device.name,
            func.count(models.UsageRecord.id).label('usage_count')
        ).join(models.UsageRecord).filter(
            models.UsageRecord.user_id == user.id
        ).group_by(models.Device.name).order_by(desc('usage_count')).limit(3).all()
        
        preferred_devices = [device.name for device in preferred_devices_query]
        
        # 查询用户使用模式（按小时统计）
        usage_patterns_query = db.query(
            extract('hour', models.UsageRecord.start_time).label('hour'),
            func.count(models.UsageRecord.id).label('count')
        ).filter(models.UsageRecord.user_id == user.id).group_by('hour').all()
        
        usage_patterns = {}
        for pattern in usage_patterns_query:
            usage_patterns[f"{int(pattern.hour)}:00"] = pattern.count
        
        # 查询高峰使用时间
        peak_times_query = db.query(
            extract('hour', models.UsageRecord.start_time).label('hour')
        ).filter(models.UsageRecord.user_id == user.id).group_by('hour').order_by(desc('hour')).limit(3).all()
        
        peak_usage_times = [f"{int(time.hour)}:00" for time in peak_times_query]
        
        response.append({
            "user_id": user.id,
            "user_name": user.name,
            "preferred_devices": preferred_devices,
            "usage_patterns": usage_patterns,
            "peak_usage_times": peak_usage_times
        })
    
    return response

def analyze_area_impact(db: Session):
    """分析房屋面积对使用行为的影响"""
    # 定义面积范围
    area_ranges = [
        (0, 50, "小于50平米"),
        (50, 100, "50-100平米"),
        (100, 150, "100-150平米"),
        (150, float('inf'), "大于150平米")
    ]
    
    response = []
    
    for min_area, max_area, range_name in area_ranges:
        # 查询该面积范围内的用户
        users = db.query(models.User).filter(
            and_(models.User.house_area >= min_area, models.User.house_area < max_area)
        ).all()
        
        if not users:
            continue
        
        user_ids = [user.id for user in users]
        
        # 计算平均设备数量
        device_count_query = db.query(
            func.count(models.Device.id).label('device_count')
        ).filter(models.Device.owner_id.in_(user_ids)).group_by(models.Device.owner_id).all()
        
        avg_device_count = sum([r.device_count for r in device_count_query]) / len(device_count_query) if device_count_query else 0
        
        # 查询最受欢迎的设备类型
        popular_devices_query = db.query(
            models.Device.device_type,
            func.count(models.Device.id).label('count')
        ).filter(models.Device.owner_id.in_(user_ids)).group_by(models.Device.device_type).order_by(desc('count')).limit(3).all()
        
        popular_devices = [str(device.device_type.value) for device in popular_devices_query]
        
        # 计算平均使用时长
        avg_duration_query = db.query(
            func.avg(models.UsageRecord.duration).label('avg_duration')
        ).filter(models.UsageRecord.user_id.in_(user_ids)).first()
        
        avg_usage_duration = float(avg_duration_query.avg_duration or 0)
        
        response.append({
            "house_area_range": range_name,
            "avg_device_count": avg_device_count,
            "popular_devices": popular_devices,
            "avg_usage_duration": avg_usage_duration
        })
    
    return response

# 数据可视化功能
def get_device_usage_data(db: Session) -> Dict[str, Any]:
    """获取设备使用数据用于可视化"""
    # 按设备类型统计使用次数
    device_type_usage = db.query(
        models.Device.device_type,
        func.count(models.UsageRecord.id).label('count')
    ).join(models.UsageRecord).group_by(models.Device.device_type).all()
    
    # 按设备类型统计使用时长
    device_type_duration = db.query(
        models.Device.device_type,
        func.sum(models.UsageRecord.duration).label('total_duration')
    ).join(models.UsageRecord).group_by(models.Device.device_type).all()
    
    # 准备可视化数据
    labels = [str(dt.device_type.value) for dt in device_type_usage]
    
    datasets = [
        {
            "label": "使用次数",
            "data": [dt.count for dt in device_type_usage],
            "backgroundColor": "rgba(54, 162, 235, 0.5)"
        },
        {
            "label": "使用时长(分钟)",
            "data": [float(dt.total_duration or 0) for dt in device_type_duration],
            "backgroundColor": "rgba(255, 99, 132, 0.5)"
        }
    ]
    
    return {"labels": labels, "datasets": datasets}

def get_security_events_data(db: Session) -> Dict[str, Any]:
    """获取安防事件数据用于可视化"""
    # 按事件类型统计
    event_type_counts = db.query(
        models.SecurityEvent.event_type,
        func.count(models.SecurityEvent.id).label('count')
    ).group_by(models.SecurityEvent.event_type).all()
    
    # 按月份统计事件数量（最近6个月）
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_counts = db.query(
        extract('month', models.SecurityEvent.occurred_at).label('month'),
        extract('year', models.SecurityEvent.occurred_at).label('year'),
        func.count(models.SecurityEvent.id).label('count')
    ).filter(models.SecurityEvent.occurred_at >= six_months_ago).group_by('month', 'year').order_by('year', 'month').all()
    
    # 准备可视化数据
    type_labels = [str(et.event_type.value) for et in event_type_counts]
    type_data = [et.count for et in event_type_counts]
    
    month_labels = [f"{int(m.year)}-{int(m.month)}" for m in monthly_counts]
    month_data = [m.count for m in monthly_counts]
    
    return {
        "labels": type_labels,
        "datasets": [
            {
                "label": "事件类型分布",
                "data": type_data,
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.5)",
                    "rgba(54, 162, 235, 0.5)",
                    "rgba(255, 206, 86, 0.5)",
                    "rgba(75, 192, 192, 0.5)",
                    "rgba(153, 102, 255, 0.5)",
                    "rgba(255, 159, 64, 0.5)"
                ]
            },
            {
                "label": "月度事件趋势",
                "data": month_data,
                "labels": month_labels,
                "borderColor": "rgba(54, 162, 235, 1)",
                "backgroundColor": "rgba(54, 162, 235, 0.1)",
                "type": "line"
            }
        ]
    }

def get_user_feedback_data(db: Session) -> Dict[str, Any]:
    """获取用户反馈数据用于可视化"""
    # 按评分统计反馈数量
    rating_counts = db.query(
        models.Feedback.rating,
        func.count(models.Feedback.id).label('count')
    ).group_by(models.Feedback.rating).order_by(models.Feedback.rating).all()
    
    # 按月份统计反馈数量和平均评分
    monthly_stats = db.query(
        extract('month', models.Feedback.created_at).label('month'),
        extract('year', models.Feedback.created_at).label('year'),
        func.count(models.Feedback.id).label('count'),
        func.avg(models.Feedback.rating).label('avg_rating')
    ).group_by('month', 'year').order_by('year', 'month').all()
    
    # 准备可视化数据
    rating_labels = [f"{int(r.rating)}星" for r in rating_counts]
    rating_data = [r.count for r in rating_counts]
    
    month_labels = [f"{int(m.year)}-{int(m.month)}" for m in monthly_stats]
    count_data = [m.count for m in monthly_stats]
    rating_data = [float(m.avg_rating or 0) for m in monthly_stats]
    
    return {
        "labels": rating_labels,
        "datasets": [
            {
                "label": "评分分布",
                "data": rating_data,
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.5)",
                    "rgba(255, 159, 64, 0.5)",
                    "rgba(255, 206, 86, 0.5)",
                    "rgba(75, 192, 192, 0.5)",
                    "rgba(54, 162, 235, 0.5)"
                ]
            },
            {
                "label": "月度反馈数量",
                "data": count_data,
                "labels": month_labels,
                "borderColor": "rgba(75, 192, 192, 1)",
                "backgroundColor": "rgba(75, 192, 192, 0.1)",
                "type": "line"
            },
            {
                "label": "月度平均评分",
                "data": rating_data,
                "labels": month_labels,
                "borderColor": "rgba(153, 102, 255, 1)",
                "backgroundColor": "rgba(153, 102, 255, 0.1)",
                "type": "line",
                "yAxisID": "rating"
            }
        ]
    }