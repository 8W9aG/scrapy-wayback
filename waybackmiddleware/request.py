"""The standard wayback request."""
import typing

import scrapy


class WaybackMachineRequest(scrapy.Request):
    """A request object containing wayback machine parameters."""
    def __init__(self, url: str, response: typing.Optional[typing.Any] = None, **kwargs):
        super().__init__(url, **kwargs)
        self._response = response
