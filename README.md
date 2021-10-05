# scrapy-wayback

<a href="https://pypi.org/project/scrapy-wayback/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/scrapy-wayback">
</a>

Scrapy middleware with wayback machine support for more robust scrapers.

## Dependencies :globe_with_meridians:

* [Python 3.7](https://www.python.org/downloads/release/python-370/)
* [Scrapy 2.4.0](https://scrapy.org/)
* [Wayback 0.3.0](https://pypi.org/project/wayback/)

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install scrapy-wayback`

## Settings

### WAYBACK_MACHINE_FALLBACK_ENABLED (Optional)

Whether falling back to wayback machine after a failed request is enabled (defaults to true).

Meta field to enable/disable this per request is: `wayback_machine_fallback_enabled`

### WAYBACK_MACHINE_PROXY_ENABLED (Optional)

Whether proxying to wayback machine before a request is made is enabled (defaults to false).

Meta field to enable/disable this per request is: `wayback_machine_proxy_enabled`

### WAYBACK_MACHINE_PROXY_FALLTHROUGH_ENABLED (Optional)

Whether when proxying to wayback machine and an error occurs, that the request should continue to the original URL as per normal (defaults to true). Note that this will not have an effect if the wayback machine proxy is not enabled first.

Meta field to enable/disable this per request is: `wayback_machine_proxy_fallthrough_enabled`

## Usage example :eyes:

In order to use this plugin simply add the following settings and substitute your variables:

```py
DOWNLOADER_MIDDLEWARES = {
    "waybackmiddleware.middleware.WaybackMachineDownloaderMiddleware": 630
}
```

This will immediately allow you begin using the wayback machine as a fallback when one of your requests fail. In order to use it as a proxy you can add the following to your settings:

```py
WAYBACK_MACHINE_PROXY_ENABLED = True
```

This will make every request hit the wayback machine for a response first, before hitting the original server. If you want to avoid hitting the original server entirely, put the following in your settings (as well as the above):

```py
WAYBACK_MACHINE_PROXY_FALLTHROUGH_ENABLED = False
```

This will ensure that your scraper never hits the original servers, just what has been recorded by the wayback machine.

Whenever you receive a response from the wayback machine middleware, it will use the class `WaybackMachineResponse`. It subclasses `scrapy.http.HtmlResponse` so you can use it like a normal response, however it has some other goodies:

```py
def parse(self, response):
    while True:
        if response is None:
            return
        print(f"Response {response.request.url} at {response.timestamp.isoformat()}")
        response = response.earlier_response()
```

This will allow you to go through the history one by one to get the earlier snapshots of the page. If you are interested in the response that the wayback middleware recovered, use the `original_response` attribute.

In order to perform a request that will yield the whole archived contents of a site, you can do the following:

```py
import scrapy
from waybackmiddleware.request import WaybackMachineRequest
from waybackmiddleware.response import WaybackMachineResponse


class ArchiveScraper(scrapy.Spider):
    def start_requests():
        yield WaybackMachineRequest("http://www.walmart.com")
    
    def parse(self, response):
        print(f"Archive of {response.url} at {response.timestamp}")
        if isinstance(response, WaybackMachineResponse):
            next_response = response.earlier_response()
            if next_response is not None:
                yield next_response.request_for_response(self.parse)
```

This will send all archived contents of `walmart.com` to the `parse` callback (called multiple times).

## License :memo:

The project is available under the [MIT License](LICENSE).
