package util

import (
	"context"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/log/global"
	"go.opentelemetry.io/otel/propagation"
	sdklog "go.opentelemetry.io/otel/sdk/log"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
	"time"
)

func InitTracer() (*sdktrace.TracerProvider, error) {
	// 创建 OTLP 导出器
	traceExporter, err := otlptracegrpc.New(context.Background(), otlptracegrpc.WithInsecure())
	if err != nil {
		return nil, err
	}

	// 创建追踪器提供者
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(traceExporter),
		sdktrace.WithResource(resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceNameKey.String(ServiceName),
		)),
	)

	// 设置全局追踪器提供者
	otel.SetTracerProvider(tp)

	// 设置全局传播器
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	return tp, nil
}

func InitLogger() (*sdklog.LoggerProvider, error) {
	// 创建 OTLP 日志导出器
	logExporter, err := otlploggrpc.New(context.Background(), otlploggrpc.WithInsecure())
	if err != nil {
		return nil, err
	}
	mergeResource, _ := resource.Merge(resource.Default(),
		resource.NewWithAttributes(semconv.SchemaURL,
			semconv.ServiceName(ServiceName),
			semconv.ServiceVersion(ServiceVersion),
		))

	loggerProvider := sdklog.NewLoggerProvider(
		sdklog.WithProcessor(sdklog.NewBatchProcessor(logExporter)),
		sdklog.WithResource(mergeResource),
	)

	global.SetLoggerProvider(loggerProvider)
	return loggerProvider, nil
}

func InitMetric() (*sdkmetric.MeterProvider, error) {
	metricExporter, err := otlpmetricgrpc.New(context.Background(), otlpmetricgrpc.WithInsecure())
	if err != nil {
		return nil, err
	}
	mergeResource, _ := resource.Merge(resource.Default(),
		resource.NewWithAttributes(semconv.SchemaURL,
			semconv.ServiceName(ServiceName),
			semconv.ServiceVersion(ServiceVersion),
		))
	metricProvider := sdkmetric.NewMeterProvider(sdkmetric.WithResource(mergeResource), sdkmetric.WithReader(
		// 取样设置为1s一次
		sdkmetric.NewPeriodicReader(metricExporter, sdkmetric.WithInterval(time.Second)),
	))

	otel.SetMeterProvider(metricProvider)
	return metricProvider, nil
}
