from celery import Celery

celery_app = Celery(
    "fingerprinting_cdf",
    broker="redis://localhost:6380/2",
    backend="redis://localhost:6380/2"
)

celery_app.conf.task_routes = {
    "tasks.process_fingerprinting_batch": {"queue": "fingerprinting"},
}