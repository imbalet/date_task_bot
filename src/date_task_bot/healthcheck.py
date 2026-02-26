from logging import getLogger

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

logger = getLogger(__name__)


async def healthcheck(request: Request) -> Response:
    logger.debug("Healthcheck request")
    return web.json_response({"status": "ok"})


async def start_healthcheck_server(port: int) -> None:
    app = web.Application()
    app.add_routes([web.get("/health", healthcheck)])
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()
    logger.info(f"Healthcheck server running on http://127.0.0.1:{port}/health")
