"""
Proxy utility for forwarding requests to microservices
"""
import httpx
from fastapi import Request, Response, HTTPException
from loguru import logger
from typing import Optional


async def proxy_request(
    request: Request,
    target_url: str,
    path: str = "",
    timeout: float = 30.0
) -> Response:
    """
    Generic proxy function to forward requests to microservices

    Args:
        request: FastAPI request object
        target_url: Base URL of the target microservice
        path: Additional path to append to target_url
        timeout: Request timeout in seconds

    Returns:
        Response from the target microservice
    """
    # Build the full target URL
    full_url = f"{target_url.rstrip('/')}/{path.lstrip('/')}" if path else target_url

    # Get request body
    try:
        body = await request.body()
    except Exception as e:
        logger.error(f"Error reading request body: {e}")
        body = b""

    # Get headers (exclude host and content-length as they'll be set by httpx)
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    # Get query parameters
    query_params = dict(request.query_params)

    logger.info(f"Proxying {request.method} {request.url.path} -> {full_url}")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=headers,
                params=query_params,
                content=body,
                follow_redirects=True
            )

            # Build response headers (exclude some headers that shouldn't be forwarded)
            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)
            response_headers.pop("content-length", None)
            response_headers.pop("transfer-encoding", None)
            response_headers.pop("connection", None)

            # Add CORS headers to response
            origin = request.headers.get("origin", "*")
            response_headers["Access-Control-Allow-Origin"] = origin
            response_headers["Access-Control-Allow-Credentials"] = "true"

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )

    except httpx.TimeoutException:
        logger.error(f"Timeout calling {full_url}")
        raise HTTPException(
            status_code=504,
            detail=f"Gateway timeout: Service did not respond in {timeout}s"
        )
    except httpx.ConnectError:
        logger.error(f"Connection error to {full_url}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Error proxying request to {full_url}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Bad gateway: {str(e)}"
        )
