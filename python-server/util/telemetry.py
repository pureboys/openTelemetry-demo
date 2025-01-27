from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


def init_trace():
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider = TracerProvider(resource=Resource.create({"service.name": "fastapi-app"}))
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


def init_log():
    logging_level = logging.DEBUG
    logger_provider = LoggerProvider(resource=Resource.create({"service.name": "fastapi-app", }), )
    set_logger_provider(logger_provider)
    exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler(level=logging_level, logger_provider=logger_provider)

    logging.basicConfig(level=logging_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", )
    # Attach OTLP handler to root logger
    logging.getLogger().addHandler(handler)
