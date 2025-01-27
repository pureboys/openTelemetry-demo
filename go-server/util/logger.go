package util

import (
	"context"
	"go.opentelemetry.io/contrib/bridges/otelzap"
	sdklog "go.opentelemetry.io/otel/sdk/log"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"os"
)

type SLogger struct {
	*zap.SugaredLogger
}

var SugaredLoggers SLogger

func Logger(loggerProvider *sdklog.LoggerProvider) {
	encoderConfig := zap.NewProductionEncoderConfig()
	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder        // 设置时间格式
	encoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder // 设置日志级别颜色
	core := zapcore.NewTee(
		zapcore.NewCore(zapcore.NewConsoleEncoder(encoderConfig), zapcore.AddSync(os.Stdout), zapcore.DebugLevel),
		otelzap.NewCore(ServiceName, otelzap.WithLoggerProvider(loggerProvider)),
	)

	zapLogger := zap.New(core)
	defer zapLogger.Sync()
	sugar := zapLogger.Sugar()
	SugaredLoggers = SLogger{sugar}
}

func (s SLogger) Debugw(ctx context.Context, msg string, keysAndValues ...any) {
	s.With("context", ctx).Debugw(msg, keysAndValues...)
}

func (s SLogger) Infow(ctx context.Context, msg string, keysAndValues ...any) {
	s.With("context", ctx).Infow(msg, keysAndValues...)
}

func (s SLogger) Warnw(ctx context.Context, msg string, keysAndValues ...any) {
	s.With("context", ctx).Warnw(msg, keysAndValues...)
}
func (s SLogger) Errorw(ctx context.Context, msg string, keysAndValues ...any) {
	s.With("context", ctx).Errorw(msg, keysAndValues...)
}
