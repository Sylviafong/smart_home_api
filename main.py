from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud

# 创建数据库表
models.Base.metadata.create_all(bind=models.engine)

app = FastAPI(title="智能家居系统API", description="智能家居系统的后端API服务")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户相关路由
@app.post("/users/", response_model=schemas.User, tags=["用户管理"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User], tags=["用户管理"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, tags=["用户管理"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

# 设备相关路由
@app.post("/devices/", response_model=schemas.Device, tags=["设备管理"])
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    return crud.create_device(db=db, device=device)

@app.get("/devices/", response_model=list[schemas.Device], tags=["设备管理"])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return devices

@app.get("/devices/{device_id}", response_model=schemas.Device, tags=["设备管理"])
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return db_device

# 使用记录相关路由
@app.post("/usage_records/", response_model=schemas.UsageRecord, tags=["使用记录"])
def create_usage_record(usage_record: schemas.UsageRecordCreate, db: Session = Depends(get_db)):
    return crud.create_usage_record(db=db, usage_record=usage_record)

@app.get("/usage_records/", response_model=list[schemas.UsageRecord], tags=["使用记录"])
def read_usage_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usage_records = crud.get_usage_records(db, skip=skip, limit=limit)
    return usage_records

# 安防事件相关路由
@app.post("/security_events/", response_model=schemas.SecurityEvent, tags=["安防事件"])
def create_security_event(security_event: schemas.SecurityEventCreate, db: Session = Depends(get_db)):
    return crud.create_security_event(db=db, security_event=security_event)

@app.get("/security_events/", response_model=list[schemas.SecurityEvent], tags=["安防事件"])
def read_security_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    security_events = crud.get_security_events(db, skip=skip, limit=limit)
    return security_events

# 用户反馈相关路由
@app.post("/feedbacks/", response_model=schemas.Feedback, tags=["用户反馈"])
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    return crud.create_feedback(db=db, feedback=feedback)

@app.get("/feedbacks/", response_model=list[schemas.Feedback], tags=["用户反馈"])
def read_feedbacks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feedbacks = crud.get_feedbacks(db, skip=skip, limit=limit)
    return feedbacks

# 数据分析相关路由
@app.get("/analytics/device_usage_frequency/", tags=["数据分析"])
def analyze_device_usage_frequency(db: Session = Depends(get_db)):
    return crud.analyze_device_usage_frequency(db)

@app.get("/analytics/user_habits/", tags=["数据分析"])
def analyze_user_habits(db: Session = Depends(get_db)):
    return crud.analyze_user_habits(db)

@app.get("/analytics/area_impact/", tags=["数据分析"])
def analyze_area_impact(db: Session = Depends(get_db)):
    return crud.analyze_area_impact(db)

# 数据可视化相关路由
@app.get("/visualization/device_usage/", tags=["数据可视化"])
def visualize_device_usage(db: Session = Depends(get_db)):
    return crud.get_device_usage_data(db)

@app.get("/visualization/security_events/", tags=["数据可视化"])
def visualize_security_events(db: Session = Depends(get_db)):
    return crud.get_security_events_data(db)

@app.get("/visualization/user_feedback/", tags=["数据可视化"])
def visualize_user_feedback(db: Session = Depends(get_db)):
    return crud.get_user_feedback_data(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)