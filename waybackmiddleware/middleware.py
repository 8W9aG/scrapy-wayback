"""The middleware for scrapy-wayback."""
import http

import scrapy
import wayback

from .response import WaybackMachineResponse


class WaybackMachineDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=scrapy.signals.spider_opened)
        return s

    def process_request(self, request, spider):
        wayback_proxy_enabled = request.meta.get("wayback_machine_proxy_enabled", spider.settings.get("WAYBACK_MACHINE_PROXY_ENABLED", False))
        wayback_proxy_fallthrough_enabled = request.meta.get("wayback_machine_proxy_fallthrough_enabled", spider.settings.get("WAYBACK_MACHINE_PROXY_FALLTHROUGH_ENABLED", True))
        if wayback_proxy_enabled:
            if request.method == "GET":
                wayback_response = WaybackMachineResponse(request, self.client.search(request.url), None, self.client)
                if wayback_response.is_valid():
                    return wayback_response
            if not wayback_proxy_fallthrough_enabled:
                raise scrapy.exceptions.IgnoreRequest("Could not find URL on wayback machine")
        return None

    def process_response(self, request, response, spider):
        fallback_enabled = request.meta.get("wayback_machine_fallback_enabled", spider.settings.get("WAYBACK_MACHINE_FALLBACK_ENABLED", True))
        if not fallback_enabled:
            return response
        if response.status >= http.HTTPStatus.BAD_REQUEST and request.method == "GET":
            wayback_response = WaybackMachineResponse(request, self.client.search(request.url), response, self.client)
            if wayback_response.is_valid():
                return wayback_response
        return response

    def spider_opened(self, spider):
        self.client = wayback.WaybackClient()
