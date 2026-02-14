from logging import getLogger

from aiohttp import web

logger = getLogger(__name__)


async def healthcheck(request):
    logger.debug("Healthcheck request")
    return web.json_response({"status": "ok"})


async def start_healthcheck_server(port: int):
    app = web.Application()
    app.add_routes([web.get("/health", healthcheck)])
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Healthcheck server running on http://0.0.0.0:{port}/health")
