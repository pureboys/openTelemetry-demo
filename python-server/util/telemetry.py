from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

# 设置 Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

fastapi_service_name = "fastapi-app"
telemetry_endpoint = "127.0.0.1:4317"


def init_trace(service_name):
    if trace.get_tracer_provider() is None or not isinstance(trace.get_tracer_provider(), TracerProvider):
        otlp_exporter = OTLPSpanExporter(endpoint=telemetry_endpoint, insecure=True)
        provider = TracerProvider(resource=Resource.create({ResourceAttributes.SERVICE_NAME: service_name}))
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)


def init_log(service_name):
    if not hasattr(logging.getLogger(), 'handlers') or not logging.getLogger().handlers:
        logging_level = logging.DEBUG
        logger_provider = LoggerProvider(resource=Resource.create({ResourceAttributes.SERVICE_NAME: service_name, }), )
        set_logger_provider(logger_provider)
        exporter = OTLPLogExporter(endpoint=telemetry_endpoint, insecure=True)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        handler = LoggingHandler(level=logging_level, logger_provider=logger_provider)

        logging.basicConfig(level=logging_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", )
        # Attach OTLP handler to root logger
        logging.getLogger().addHandler(handler)


def init_metric(service_name):
    if metrics.get_meter_provider() is None or not isinstance(metrics.get_meter_provider(), MeterProvider):
        otlp_exporter = OTLPMetricExporter(endpoint=telemetry_endpoint)
        metric_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=1000)
        metric_provider = MeterProvider(metric_readers=[metric_reader],
                                        resource=Resource.create({ResourceAttributes.SERVICE_NAME: service_name}, ))
        metrics.set_meter_provider(metric_provider)
