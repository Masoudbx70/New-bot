import redis
import config.config as config

# اتصال به Redis برای مدیریت وضعیت کاربران و پیام‌ها
redis_client = redis.from_url(config.REDIS_URL)

def get_user_state(user_id):
    state = redis_client.get(f"user_state:{user_id}")
    return int(state) if state else None

def set_user_state(user_id, state):
    redis_client.setex(f"user_state:{user_id}", 3600, state)  # انقضا پس از 1 ساعت

def delete_user_state(user_id):
    redis_client.delete(f"user_state:{user_id}")

def increment_message_count(user_id):
    return redis_client.incr(f"message_count:{user_id}")

def get_message_count(user_id):
    count = redis_client.get(f"message_count:{user_id}")
    return int(count) if count else 0

def reset_message_count(user_id):
    redis_client.delete(f"message_count:{user_id}")

def add_warning(user_id):
    warnings = redis_client.incr(f"warnings:{user_id}")
    return warnings

def get_warnings(user_id):
    warnings = redis_client.get(f"warnings:{user_id}")
    return int(warnings) if warnings else 0

def reset_warnings(user_id):
    redis_client.delete(f"warnings:{user_id}")