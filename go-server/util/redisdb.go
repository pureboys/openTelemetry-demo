package util

import (
	"github.com/redis/go-redis/extra/redisotel/v9"
	"github.com/redis/go-redis/v9"
)

var RedisDB *redis.Client

func RedInit() {
	RedisDB = redis.NewClient(&redis.Options{
		Addr:     "127.0.0.1:6379", // 主节点地址
		Password: "masterpassword", // Redis 密码
		DB:       0,                // 数据库编号
	})

	if err := redisotel.InstrumentTracing(RedisDB); err != nil {
		panic(err)
	}
}
