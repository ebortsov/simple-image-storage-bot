from cachetools import TTLCache
from aiogram import Router, BaseMiddleware, types
import logging

TTL_VALUE = 0.5  # in seconds

cache = TTLCache(maxsize=10000, ttl=TTL_VALUE)


# This middleware allow user to perform only one action per THROTTLING_DELAY seconds
class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user: types.User = data['event_from_user']

        if user.id in cache:
            logging.debug(f'user {user.id} is in cache')
            return

        logging.debug(f'user {user.id} is not in cache')
        cache[user.id] = True
        return await handler(event, data)
