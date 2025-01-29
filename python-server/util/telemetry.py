from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


# 设置 Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

service_name = "fastapi-app"

def init_trace():
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


def init_log():
    logging_level = logging.DEBUG
    logger_provider = LoggerProvider(resource=Resource.create({"service.name":service_name, }), )
    set_logger_provider(logger_provider)
    exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler(level=logging_level, logger_provider=logger_provider)

    logging.basicConfig(level=logging_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", )
    # Attach OTLP handler to root logger
    logging.getLogger().addHandler(handler)

def init_metric():
    otlp_exporter = OTLPMetricExporter(endpoint="http://localhost:4317")
    metric_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=1000)
    metric_provider = MeterProvider(metric_readers=[metric_reader], resource=Resource.create({"service.name": service_name}, ))
    metrics.set_meter_provider(metric_provider)