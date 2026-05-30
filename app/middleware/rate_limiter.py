from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60
        
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > minute_ago]
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Trop de requêtes")
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()
