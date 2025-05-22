-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS smart_home_db;

-- 连接到数据库
\c smart_home_db;

-- 创建枚举类型
CREATE TYPE device_type AS ENUM (
    '灯光',
    '空调',
    '冰箱',
    '电视',
    '安防摄像头',
    '智能门锁',
    '智能音箱',
    '其他'
);

CREATE TYPE security_event_type AS ENUM (
    '入侵检测',
    '火灾报警',
    '燃气泄漏',
    '水浸检测',
    '门窗异常开启',
    '其他'
);

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    house_area FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建设备表
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    device_type device_type NOT NULL,
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    location VARCHAR(100),
    status BOOLEAN DEFAULT TRUE,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建使用记录表
CREATE TABLE IF NOT EXISTS usage_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    device_id INTEGER REFERENCES devices(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration FLOAT,
    power_consumption FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建安防事件表
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type security_event_type NOT NULL,
    description TEXT,
    location VARCHAR(100),
    is_handled BOOLEAN DEFAULT FALSE,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户反馈表
CREATE TABLE IF NOT EXISTS feedbacks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_devices_owner ON devices(owner_id);
CREATE INDEX idx_usage_records_user ON usage_records(user_id);
CREATE INDEX idx_usage_records_device ON usage_records(device_id);
CREATE INDEX idx_security_events_user ON security_events(user_id);
CREATE INDEX idx_feedbacks_user ON feedbacks(user_id);

-- 添加一些示例数据
INSERT INTO users (name, email, hashed_password, phone, address, house_area)
VALUES 
('张三', 'zhangsan@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '13800138000', '北京市海淀区', 120.5),
('李四', 'lisi@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '13900139000', '上海市浦东新区', 85.3),
('王五', 'wangwu@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '13700137000', '广州市天河区', 150.0);

INSERT INTO devices (name, device_type, model, serial_number, location, owner_id)
VALUES
('客厅灯', '灯光', 'Philips Hue', 'PH001', '客厅', 1),
('卧室空调', '空调', 'Gree Smart', 'GS001', '主卧', 1),
('智能冰箱', '冰箱', 'Samsung Family Hub', 'SF001', '厨房', 1),
('客厅电视', '电视', 'Sony Bravia', 'SB001', '客厅', 2),
('门口摄像头', '安防摄像头', 'Hikvision Pro', 'HP001', '前门', 2),
('智能门锁', '智能门锁', 'Xiaomi Smart Lock', 'XS001', '前门', 3);

-- 添加使用记录示例数据
INSERT INTO usage_records (user_id, device_id, start_time, end_time, duration, power_consumption)
VALUES
(1, 1, '2023-05-01 18:00:00', '2023-05-01 22:00:00', 240, 0.5),
(1, 2, '2023-05-01 20:00:00', '2023-05-02 08:00:00', 720, 2.4),
(2, 4, '2023-05-01 19:00:00', '2023-05-01 23:30:00', 270, 1.2),
(3, 6, '2023-05-01 22:00:00', '2023-05-01 22:01:00', 1, 0.01);

-- 添加安防事件示例数据
INSERT INTO security_events (user_id, event_type, description, location)
VALUES
(2, '入侵检测', '检测到可疑人员在门口逗留', '前门'),
(1, '火灾报警', '厨房烟雾浓度超标', '厨房'),
(3, '门窗异常开启', '窗户在无人操作的情况下被打开', '客厅');

-- 添加用户反馈示例数据
INSERT INTO feedbacks (user_id, title, content, rating)
VALUES
(1, '空调控制不稳定', '有时候设置温度后空调不响应，需要多次操作', 3),
(2, '摄像头画面清晰度高', '门口摄像头的画面非常清晰，夜视效果也很好', 5),
(3, '门锁反应速度慢', '有时候需要等待3-5秒才能解锁，希望能提高响应速度', 2);