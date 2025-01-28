package main

import (
	"context"
	"github.com/gin-gonic/gin"
	"go-server/util"
	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"io"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

func main() {
	// 初始化日志和追踪
	tracerProvider, err := util.InitTracer()
	if err != nil {
		panic(err)
	}
	defer tracerProvider.Shutdown(context.Background())

	loggerProvider, err := util.InitLogger()
	if err != nil {
		panic(err)
	}
	util.Logger(loggerProvider)
	defer loggerProvider.Shutdown(context.Background())

	metricProvider, err := util.InitMetric()
	if err != nil {
		panic(err)
	}
	defer metricProvider.Shutdown(context.Background())

	util.DBInit()
	util.RedInit()

	r := gin.Default()
	// 添加 OpenTelemetry 中间件
	r.Use(otelgin.Middleware(util.ServiceName))
	r.Use(util.MetricMiddle(util.ServiceName))
	router(r)
	_ = r.Run(util.ServerPort)
}

func router(r *gin.Engine) {
	r.GET("/ping", ping)
	r.GET("/get_db", getDB)
	r.GET("/get_redis", getRedis)
	r.GET("/get_http", getHttp)
}

func getHttp(c *gin.Context) {
	reqUrl := "http://127.0.0.1:5000/"
	ctx := c.Request.Context()
	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		doRequest(ctx, reqUrl)
	}()
	go func() {
		defer wg.Done()
		doRequest(ctx, reqUrl)
	}()
	wg.Wait()
	c.JSON(http.StatusOK, gin.H{
		"data": "ok",
	})
}

func doRequest(ctx context.Context, url string) []byte {
	client := http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport), Timeout: time.Second * 5}
	req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	resp, err := client.Do(req)
	if err != nil {
		return nil
	}
	// 解析响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil
	}
	_ = resp.Body.Close()
	return body
}

func getRedis(c *gin.Context) {
	ctx := c.Request.Context()
	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		util.RedisDB.Set(ctx, "key1", "val1", 0)
	}()
	go func() {
		defer wg.Done()
		util.RedisDB.Set(ctx, "key2", "val2", 0)
	}()
	wg.Wait()
	c.JSON(http.StatusOK, gin.H{
		"data": util.RedisDB.Get(ctx, "key1").Val(),
	})
}

func getDB(c *gin.Context) {
	var result1 []map[string]interface{}
	var result2 []map[string]interface{}

	ctx := c.Request.Context()
	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		db1 := util.DB.WithContext(ctx)
		db1.Table("students").Find(&result1) // 读操作，自动选择从数据库
	}()
	go func() {
		defer wg.Done()
		db2 := util.DB.WithContext(ctx)
		db2.Table("students").Find(&result2) // 读操作，自动选择从数据库
	}()
	wg.Wait()
	c.JSON(http.StatusOK, gin.H{
		"data": gin.H{
			"result1": result1,
			"result2": result1,
		},
	})
}

func ping(c *gin.Context) {
	ctx := c.Request.Context()
	util.SugaredLoggers.Infow(ctx, "demo", "message", "hello world")

	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	randIntN := rng.Intn(2000) + 1000
	time.Sleep(time.Millisecond * time.Duration(randIntN))

	c.JSON(http.StatusOK, gin.H{
		"data": "ok",
	})
}
