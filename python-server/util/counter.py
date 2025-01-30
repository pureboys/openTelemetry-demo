from opentelemetry import trace, metrics


class Counter:
    def __init__(self, service_name):
        meter = metrics.get_meter(service_name)
        self.request_counter = meter.create_counter(
            "http.server.request.count",
            description="The number of HTTP server requests.",
            unit="{request}"
        )
        self.request_active_counter = meter.create_up_down_counter(
            "http.server.request.active",
            description="The number of active HTTP server requests.",
            unit="{request}"
        )
        self.request_duration_histogram = meter.create_histogram(
            "http.server.request.duration",
            description="The duration of the HTTP server request.",
            unit="ms"
        )
