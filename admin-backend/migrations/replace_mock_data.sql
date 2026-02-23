-- 替换模拟数据为真实用户数据（匿名化）
-- 执行时间: 2026-02-20
-- 目的: 将所有张三、李四等模拟数据替换为真实用户数据，但保持用户名匿名化

-- 1. 替换私有资源库中的模拟联系人
UPDATE private_resources
SET contact_name = '用户' || user_id,
    contact_phone = (SELECT phone FROM users WHERE id = private_resources.user_id)
WHERE contact_name IN ('张三', '李四', '王五', '测试用户', '赵六', '钱七', '孙八', '周九', '吴十')
  OR contact_name LIKE '测试%'
  OR contact_name LIKE '%测试%';

-- 2. 替换商家资源中的模拟联系人
UPDATE merchants
SET contact_person = '商家' || substr(id, -2, 2)
WHERE contact_person IN ('王经理', '李师傅', '张总', '刘大厨', '赵老师', '孙经理', '周主管', '吴总监')
  OR contact_person LIKE '%经理%'
  OR contact_person LIKE '%师傅%'
  OR contact_person LIKE '%总监%'
  OR contact_person LIKE '%主管%';

-- 3. 更新私有资源库的描述，移除测试相关字样
UPDATE private_resources
SET description = REPLACE(description, '测试', ''),
    resource_name = REPLACE(resource_name, '测试', '')
WHERE description LIKE '%测试%'
   OR resource_name LIKE '%测试%';

-- 4. 清理空字符串
UPDATE private_resources
SET description = '资源描述'
WHERE description = '' OR description IS NULL;

-- 验证更新结果
SELECT '=== 更新后的私有资源库数据 ===' as info;
SELECT id, user_id, resource_name, contact_name, contact_phone, description
FROM private_resources
LIMIT 10;

SELECT '=== 更新后的商家资源数据 ===' as info;
SELECT id, merchant_code, merchant_name, contact_person, contact_phone
FROM merchants
LIMIT 10;
