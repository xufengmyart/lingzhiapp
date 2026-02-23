# 生产环境部署指南
## 目标: meiyueart.com
## 版本: v1.2.0
## 日期: 2026-02-15

---

## 部署准备

### 前置条件
- ✅ 有生产服务器（meiyueart.com）的SSH访问权限
- ✅ 有生产服务器的root权限或sudo权限
- ✅ 确保生产服务器已安装必要的环境（Python 3.x, Node.js, npm）
- ✅ 确保本地已完成前端构建

### 本地构建确认
```bash
# 确认前端构建已完成
ls -lh public/
```

预期输出应包含：
- index.html
- assets/index-*.css
- assets/index-*.js
- version.json

---

## 部署步骤

### 步骤1: 连接到生产服务器
```bash
ssh root@meiyueart.com
```

### 步骤2: 备份生产环境
```bash
# 创建备份目录
mkdir -p /var/www/backups/$(date +%Y%m%d_%H%M%S)

# 备份当前生产代码
cp -r /var/www/meiyueart.com /var/www/backups/$(date +%Y%m%d_%H%M%S)/

# 备份数据库
cp /var/www/meiyueart.com/admin-backend/lingzhi_ecosystem.db \
   /var/www/backups/$(date +%Y%m%d_%H%M%S)/lingzhi_ecosystem.db.backup
```

### 步骤3: 上传后端代码（在本地执行）
```bash
# 从本地上传到生产服务器
rsync -avz --delete \
    admin-backend/ \
    root@meiyueart.com:/var/www/meiyueart.com/admin-backend/
```

### 步骤4: 上传前端代码（在本地执行）
```bash
# 从本地上传到生产服务器
rsync -avz --delete \
    public/ \
    root@meiyueart.com:/var/www/meiyueart.com/public/
```

### 步骤5: 更新数据库（在生产服务器执行）
```bash
cd /var/www/meiyueart.com/admin-backend

# 检查表结构
python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 检查表是否存在
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='checkin_records'\")
if not cursor.fetchone():
    print('表不存在，需要创建')
else:
    # 检查字段
    cursor.execute('PRAGMA table_info(checkin_records)')
    columns = [col[1] for col in cursor.fetchall()]
    print('当前字段:', columns)
    if 'lingzhi_earned' not in columns:
        print('需要添加 lingzhi_earned 字段')
    else:
        print('表结构正确')

conn.close()
"

# 如果需要修复表结构
python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 重命名旧表
cursor.execute('ALTER TABLE checkin_records RENAME TO checkin_records_old')

# 创建新表
cursor.execute('''
    CREATE TABLE checkin_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        checkin_date DATE NOT NULL,
        lingzhi_earned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, checkin_date),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# 迁移数据
cursor.execute('''
    INSERT INTO checkin_records (user_id, checkin_date, lingzhi_earned, created_at)
    SELECT user_id, checkin_date, lingzhi_reward, created_at
    FROM checkin_records_old
''')

# 删除旧表
cursor.execute('DROP TABLE checkin_records_old')

conn.commit()
conn.close()
print('表结构更新完成')
"
```

### 步骤6: 停止现有服务（在生产服务器执行）
```bash
cd /var/www/meiyueart.com

# 停止Flask服务
pkill -f "python.*app.py" || true
pkill -f "gunicorn" || true

# 等待进程结束
sleep 3

# 确认进程已停止
ps aux | grep "python.*app.py" | grep -v grep
```

### 步骤7: 启动服务（在生产服务器执行）
```bash
cd /var/www/meiyueart.com/admin-backend

# 启动Flask服务
nohup python3 app.py > server.log 2>&1 &

# 等待服务启动
sleep 5

# 检查服务状态
ps aux | grep "python.*app.py" | grep -v grep

# 检查日志
tail -20 server.log
```

### 步骤8: 验证部署（在本地执行）
```bash
# 1. 测试健康检查
curl -s https://meiyueart.com/api/health
# 预期输出: {"status":"ok"}

# 2. 测试登录
curl -s -X POST https://meiyueart.com/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"123456"}' | python -m json.tool

# 3. 测试签到状态
TOKEN="从登录响应中获取的token"
curl -s https://meiyueart.com/api/checkin/status \
    -H "Authorization: Bearer $TOKEN" | python -m json.tool

# 4. 测试前端访问
curl -I https://meiyueart.com/
# 检查版本号: app-version 应该是 20260215-1037
```

---

## 验证清单

### 后端验证
- ✅ 健康检查API响应正常
- ✅ 登录API响应正常
- ✅ 签到状态API响应正常
- ✅ 签到执行API响应正常
- ✅ 智能体对话API响应正常

### 前端验证
- ✅ 网站可以访问
- ✅ 版本号更新为 20260215-1037
- ✅ "灵值元宇宙智能体"文字显示正常
- ✅ 签到功能正常
- ✅ 智能体对话功能正常

### 数据库验证
- ✅ 签到表结构正确（包含lingzhi_earned字段）
- ✅ 签到数据可以正常保存
- ✅ 连续签到计算正确

---

## 回滚方案

如果部署出现问题，执行以下回滚步骤：

```bash
# 1. 连接到生产服务器
ssh root@meiyueart.com

# 2. 停止服务
cd /var/www/meiyueart.com
pkill -f "python.*app.py" || true

# 3. 恢复备份
BACKUP_DATE="20260215_1030"  # 替换为实际的备份日期
cp -r /var/www/backups/$BACKUP_DATE/meiyueart.com/* /var/www/meiyueart.com/

# 4. 恢复数据库
cp /var/www/backups/$BACKUP_DATE/lingzhi_ecosystem.db.backup \
   /var/www/meiyueart.com/admin-backend/lingzhi_ecosystem.db

# 5. 重启服务
cd /var/www/meiyueart.com/admin-backend
nohup python3 app.py > server.log 2>&1 &

# 6. 验证恢复
curl -s https://meiyueart.com/api/health
```

---

## 注意事项

1. **SSH访问**: 确保有生产服务器的SSH访问权限
2. **备份**: 部署前必须备份生产环境
3. **停机时间**: 预计停机时间约5-10分钟
4. **测试**: 部署后必须进行完整的功能测试
5. **日志**: 检查服务器日志确认服务正常启动

---

## 联系方式

如有问题，请联系：
- 技术支持: [待补充]
- 紧急联系: [待补充]

---

**部署完成后，请更新部署档案记录。**
