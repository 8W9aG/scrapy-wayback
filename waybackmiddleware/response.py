"""The standard wayback response."""
import typing
import http

import scrapy
import wayback

from .request import WaybackMachineRequest


def find_memento(
    records: typing.List[str],
    client: wayback.WaybackClient
) -> typing.Tuple[typing.Optional[wayback.Memento], typing.Optional[str]]:
    """Finds the latest valid memento in the records."""
    try:
        for record in records:
            try:
                memento = client.get_memento(record, mode=wayback.Mode.original)
                if memento.status_code == http.HTTPStatus.OK:
                    return memento, record
            except wayback.exceptions.MementoPlaybackError:
                pass
    except wayback.exceptions.BlockedSiteError:
        pass
    return None, None


class WaybackMachineResponse(scrapy.http.HtmlResponse):
    """A response object containing information about the wayback response."""
    def __init__(
        self,
        request: scrapy.Request,
        records: typing.List[str],
        response: typing.Optional[scrapy.http.Response],
        client: wayback.WaybackClient
    ) -> None:
        memento, record = find_memento(records, client)
        self._memento = memento
        self._record = record
        self._records = records
        self._client = client
        super().__init__(
            memento.url,
            body="" if self._memento is None else self._memento.text,
            encoding="utf8" if self._memento is None else self._memento.encoding,
            status=http.HTTPStatus.NOT_FOUND if self._memento is None else self._memento.status_code,
            request=request,
        )
        self.original_response = response
        self.timestamp = None if self._memento is None else self._memento.timestamp

    def earlier_response(self) -> typing.Optional[typing.Any]:
        """Fetch the response earlier than this."""
        earlier_records = self._records[self._records.index(self._record) + 1:]
        response = WaybackMachineResponse(
            self.request,
            earlier_records,
            self.original_response,
            self._client
        )
        if response.is_valid():
            return response
        return None

    def is_valid(self) -> bool:
        """Whether the response is valid."""
        return self._memento is not None

    def request_for_response(self, callback: typing.Callable) -> WaybackMachineRequest:
        """Generate a wayback machine request for the response."""
        return WaybackMachineRequest(
            self.request.url,
            self,
            callback=callback
        )

    def wayback_url(self) -> str:
        """Fetch the wayback URL for the response."""
        return self._memento.memento_url
