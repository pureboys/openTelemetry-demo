from opentelemetry import trace, metrics
from opentelemetry.semconv.metrics import MetricInstruments, http_metrics


class Counter:
    def __init__(self, service_name):
        meter = metrics.get_meter(service_name)
        self.request_counter = meter.create_counter(
            "http.server.requests",
            description="Total Number of HTTP server requests.",
            unit="{request}"
        )
        self.request_active_counter = meter.create_up_down_counter(
            MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS,
            description="The number of active HTTP server requests.",
            unit="{request}"
        )
        self.request_duration_histogram = meter.create_histogram(
            http_metrics.HTTP_SERVER_REQUEST_DURATION,
            description="The duration of the HTTP server request.",
            unit="ms"
        )
