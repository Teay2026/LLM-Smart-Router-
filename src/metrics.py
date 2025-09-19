from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


routing_decisions_total = Counter(
    'llm_routing_decisions_total',
    'Total number of routing decisions',
    ['model', 'reason']
)

request_latency_histogram = Histogram(
    'llm_request_duration_seconds',
    'Request latency in seconds',
    ['model']
)

queue_depth_gauge = Gauge(
    'llm_queue_depth',
    'Current queue depth per model',
    ['model']
)

errors_total = Counter(
    'llm_errors_total',
    'Total number of errors',
    ['model', 'error_type']
)


class MetricsCollector:
    def record_routing_decision(self, model: str, reason: str):
        routing_decisions_total.labels(model=model, reason=reason).inc()

    def record_request_latency(self, model: str, latency_seconds: float):
        request_latency_histogram.labels(model=model).observe(latency_seconds)

    def update_queue_depth(self, model: str, depth: int):
        queue_depth_gauge.labels(model=model).set(depth)

    def record_error(self, model: str, error_type: str):
        errors_total.labels(model=model, error_type=error_type).inc()

    def get_metrics(self) -> str:
        return generate_latest().decode('utf-8')