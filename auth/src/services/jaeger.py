from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import JAEGER_PORT, JAEGER_HOST

trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"})))

jaeger_exporter = JaegerExporter(agent_host_name=JAEGER_HOST, agent_port=JAEGER_PORT)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))


def init_jaeger(app):
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
