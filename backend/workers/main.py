import sys
import logging
from rq import Worker
from infrastructure.redis_adapter import redis_adapter
from core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def start_worker():
    """Starts the RQ worker process"""
    if not redis_adapter.redis_conn:
        logger.error("Redis connection failed. Cannot start worker.")
        sys.exit(1)

    queues = ["default"]
    logger.info("Initializing RQ worker. Listening on 'default' queue...")

    worker = Worker(
        queues=queues,
        connection= redis_adapter.redis_conn
    )

    worker.work(with_scheduler=True)


if __name__ == "__main__":
    start_worker()