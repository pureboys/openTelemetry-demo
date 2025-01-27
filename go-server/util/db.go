package util

import (
	"fmt"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
	"gorm.io/plugin/dbresolver"
	"gorm.io/plugin/opentelemetry/tracing"
)

var DB *gorm.DB

func DBInit() {
	var err error
	// 主数据库连接
	dsnMaster := "myuser:mypassword@tcp(127.0.0.1:3306)/mydb?charset=utf8mb4&parseTime=True&loc=Local"
	// 从数据库连接
	dsnSlave1 := "myuser:mypassword@tcp(127.0.0.1:3306)/mydb?charset=utf8mb4&parseTime=True&loc=Local"

	// 连接主数据库
	DB, err = gorm.Open(mysql.Open(dsnMaster), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		panic("failed to connect database")
	}
	// 使用 DBResolver 插件
	err = DB.Use(dbresolver.Register(dbresolver.Config{
		// 主数据库
		Sources: []gorm.Dialector{mysql.Open(dsnMaster)},
		// 从数据库
		Replicas: []gorm.Dialector{mysql.Open(dsnSlave1)},
		// 负载均衡策略
		Policy:            dbresolver.RoundRobinPolicy(),
		TraceResolverMode: true,
	}))
	if err != nil {
		fmt.Println(err)
	}
	err = DB.Use(tracing.NewPlugin())
	if err != nil {
		fmt.Println(err)
	}
}
