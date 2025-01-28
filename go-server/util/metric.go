package util

import (
	"github.com/gin-gonic/gin"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/metric"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
	"time"
)

type config struct{}

type Option interface {
	apply(*config)
}

// MetricMiddle 设置监控中间件
// @see https://github.com/open-telemetry/semantic-conventions/blob/main/docs/http/http-metrics.md
// @see https://opentelemetry.io/docs/languages/go/instrumentation/#using-counters
func MetricMiddle(service string, _ ...Option) gin.HandlerFunc {
	var meter = otel.Meter(service)
	apiCounter, _ := meter.Int64Counter(
		"http.server.active_requests",
		metric.WithDescription("Number of active HTTP server requests."),
		metric.WithUnit("{request}"),
	)

	histogram, _ := meter.Float64Histogram(
		"http.server.request.duration",
		metric.WithDescription("Duration of HTTP server requests."),
		metric.WithUnit("ms"),
	)

	return func(c *gin.Context) {
		r := c.Request
		attrs := metric.WithAttributes(semconv.HTTPRoute(c.FullPath()), semconv.HTTPRequestMethodKey.String(r.Method))

		start := time.Now()
		apiCounter.Add(r.Context(), 1, attrs)

		c.Next()

		duration := float64(time.Since(start)) / float64(time.Millisecond)
		histogram.Record(r.Context(), duration, attrs)
	}
}
