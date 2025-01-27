CREATE TABLE students (
                          id INT AUTO_INCREMENT PRIMARY KEY,  -- 自增主键
                          name VARCHAR(100) NOT NULL,         -- 学生姓名，不能为空
                          age INT NOT NULL,                   -- 学生年龄，不能为空
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认为当前时间
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间，默认为当前时间，并在更新时自动更新
);

INSERT INTO students (name, age) VALUES ('Alice', 20);
INSERT INTO students (name, age) VALUES ('Bob', 22);
INSERT INTO students (name, age) VALUES ('Charlie', 21);