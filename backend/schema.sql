-- 校园二手闲置市场 数据库建表脚本
-- 数据库: secondhand  字符集: utf8mb4

CREATE DATABASE IF NOT EXISTS secondhand DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE secondhand;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    password   VARCHAR(100) NOT NULL COMMENT '密码(SHA256摘要)',
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 物品表
CREATE TABLE IF NOT EXISTS items (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    title       VARCHAR(100)  NOT NULL COMMENT '物品标题',
    description TEXT          COMMENT '详细描述',
    price       DECIMAL(10,2) DEFAULT 0 COMMENT '价格(元)',
    category    VARCHAR(50)   COMMENT '分类',
    image_url   VARCHAR(255)  COMMENT '图片URL',
    status      VARCHAR(20)   DEFAULT '在售' COMMENT '状态:在售/已售',
    user_id     INT           NOT NULL COMMENT '发布者ID',
    created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    CONSTRAINT fk_items_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='闲置物品表';

-- 预置测试账号(任务书要求 user1/123456、user2/123456)
INSERT INTO users (username, password) VALUES
('user1', SHA2('123456', 256)),
('user2', SHA2('123456', 256));

-- 示例数据
INSERT INTO items (title, description, price, category, image_url, status, user_id) VALUES
('高等数学教材(第七版)上册', '同济版高数教材,上册,九成新,有少量笔记不影响使用,期末复习神器。', 15.00, '教材书籍', '', '在售', 1),
('iPad Air 5 64G 蓝色', '大一入手,平时只用来上网课和记笔记,成色很好,带保护壳和笔,配件齐全。', 2999.00, '电子产品', '', '在售', 1),
('小米台灯Pro', '宿舍神器,亮度多档调节,大四毕业低价出,灯罩有一点小划痕。', 89.00, '生活用品', '', '在售', 2),
('篮球 斯伯丁74-602Y', '用了两个学期,气密性完好,皮面磨损正常,送打气筒和球袋。', 120.00, '运动用品', '', '已售', 2),
('考研英语真题黄皮书', '2025考研英语一黄皮书,只做了前三套, almost全新,附赠手写笔记。', 25.00, '教材书籍', '', '在售', 1),
('罗技G102游戏鼠标', '吃鸡利器,RGB炫光,用了一年,功能一切正常,换新鼠标所以出掉。', 79.00, '电子产品', '', '在售', 2),
('宿舍收纳箱三件套', '收纳箱三个,大小各一,搬宿舍神器,干净无破损,自提优先。', 35.00, '生活用品', '', '在售', 1),
('羽毛球拍 尤尼克斯双拍', '一对YY入门拍,送手胶和筒装球,适合新手,毕业清仓。', 150.00, '运动用品', '', '在售', 2),
('C语言程序设计 谭浩强', '大一C语言课教材,全新未拆封,买重复了低价转。', 20.00, '教材书籍', '', '在售', 2),
('Kindle Paperwhite 4', '泡面盖神器,8G内存,屏幕无划痕,带原装磁吸保护套,墨水屏阅读体验极佳。', 450.00, '电子产品', '', '在售', 1),
('折叠晾衣架', '宿舍阳台用折叠晾衣架,不锈钢材质,结实耐用,闲置出。', 18.00, '生活用品', '', '在售', 2),
('山地自行车 捷安特ATX660', '骑了一年,车况良好,刚做过保养,毕业急出,可小刀,校内自提。', 850.00, '运动用品', '', '在售', 1);
