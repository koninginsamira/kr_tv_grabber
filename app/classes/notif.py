import apprise


class Notif:
    _app: apprise.Apprise

    def __init__(self) -> None:
        self._app = apprise.Apprise()

    def add(
        self,
        servers: str,
        asset: apprise.AppriseAsset | None = None,
        tag: str | None=None
    ):
        self._app.add( # type: ignore
            servers=servers,
            asset=asset,
            tag=tag
        )

    def notify(
        self,
        body: str, title: str="",
        notify_type: apprise.NotifyType=apprise.NotifyType.INFO,
        body_format: apprise.NotifyFormat | None=None
    ):
        self._app.notify( # type: ignore
            body=body,
            title=title,
            notify_type=notify_type,
            body_format=body_format # type: ignore
        )