import logging
from redis import Redis
from rq import Queue
from core.config import settings

logger = logging.getLogger(__name__)

class RedisAdapter:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        if not self.redis_url:
            logger.warning("REDIS_URL not set! Background jobs will fail.")
            self.redis_conn = None
            self.queue = None
            return

        try:
            self.redis_conn = Redis.from_url(self.redis_url)
            self.queue = Queue(connection=self.redis_conn, default_timeout=1800) # 30 mins timeout for complex processing
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_conn = None
            self.queue = None

    def enqueue_job(self, func, *args, **kwargs):
        if not self.queue:
            raise RuntimeError("Redis queue is not configured")
        
        job = self.queue.enqueue(
            func, 
            *args, 
            **kwargs,
            job_timeout='30m', 
            failure_ttl=86400,
            retry=None
        )
        return job

redis_adapter = RedisAdapter()
