"""
app/observability/tracing.py — OpenTelemetry tracer setup.

Usage:
    from app.observability.tracing import get_tracer
    tracer = get_tracer("execute_workflow")
    with tracer.start_as_current_span("workflow.execute") as span:
        span.set_attribute("run_id", run_id)
"""
from __future__ import annotations

import logging

logger = logging.getLogger("apotheon.tracing")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

_provider = None


def setup_tracing(service_name: str = "apotheon", otlp_endpoint: str = "") -> None:
    """Configure the global OpenTelemetry TracerProvider."""
    global _provider
    if not _HAS_OTEL:
        logger.debug("opentelemetry-sdk not installed — tracing disabled")
        return

    resource = Resource.create({SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("OTel OTLP exporter configured: %s", otlp_endpoint)
        except ImportError:
            logger.warning("opentelemetry-exporter-otlp not installed — falling back to console")
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        # Console exporter for dev (no-op when log level is higher than DEBUG)
        if logger.isEnabledFor(logging.DEBUG):
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _provider = provider
    logger.info("OpenTelemetry tracing initialized (service=%s)", service_name)


def get_tracer(name: str):
    """Return a tracer for the given module name. No-ops if OTel unavailable."""
    if not _HAS_OTEL:
        return _NoopTracer()
    return trace.get_tracer(name)


class _NoopSpan:
    def set_attribute(self, key, value): pass
    def record_exception(self, exc): pass
    def set_status(self, *a, **kw): pass
    def __enter__(self): return self
    def __exit__(self, *a): pass


class _NoopTracer:
    def start_as_current_span(self, name, **kwargs):
        return _NoopSpan()

    def start_span(self, name, **kwargs):
        return _NoopSpan()