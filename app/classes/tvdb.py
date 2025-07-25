from datetime import timedelta, datetime
from typing import Literal, TypedDict
import tvdb_v4_official # type: ignore

from modules.cache import Cache, cache, cache_file


class RemoteId(TypedDict):
    id: str
    key: int
    sourceName: str

class Serie(TypedDict):
    objectID: str
    country: str
    id: str
    image_url: str
    name: str
    first_air_time: datetime
    overview: str
    primary_language: str
    primary_type: Literal["series"]
    status: str
    type: Literal["series"]
    tvdb_id: int
    year: int
    slug: str
    overviews: dict[str, str]
    translations: dict[str, str]
    network: str
    remote_ids: list[RemoteId]
    thumbnail: str
    last_updated: datetime

class Episode(TypedDict):
    id: int
    seriesId: int
    name: str | None
    aired: datetime
    runtime: int
    nameTranslations: list[str]
    overview: None
    overviewTranslations: list[str]
    image: str | None
    imageType: str | None
    isMovie: bool
    seasons: None
    number: int
    absoluteNumber: int
    seasonNumber: int
    lastUpdated: datetime
    finaleType: None
    year: int

class TVDB:
    _api: tvdb_v4_official.TVDB
    _cache: Cache | None
    _cache_lifespan: timedelta = timedelta(weeks=1)

    def __init__(self, key: str):
        self._api = tvdb_v4_official.TVDB(key)

    def with_cache(
        self,
        path: str | None = None,
        lifespan: timedelta | None = None
    ) -> "TVDB":
        use_path = path is not None
        if not use_path:
            self._cache = []
            
        if lifespan:
            self._cache_lifespan = lifespan

        for name in dir(self):
            if name.startswith("__") or name == "with_cache":
                continue

            attr = getattr(self, name)
            if callable(attr):
                fn = getattr(attr, "__func__", attr)

                if path is not None:
                    cached_fn = cache_file(
                        path=path,
                        lifespan=self._cache_lifespan
                    )(fn)
                elif self._cache is not None:
                    cached_fn = cache(
                        cache=self._cache,
                        lifespan=self._cache_lifespan
                    )(fn)
                else:
                    raise Exception("Neither a cache file or a cache list exist. What happened?")

                setattr(self, name, cached_fn.__get__(self, self.__class__))

        return self

    def search_series(
        self,
        query: str,
        year: int | None = None,
        company: str | None = None,
        country: str | None = None,
        director: str | None = None,
        language: str | None = None,
        network: str | None = None,
        remote_id: str | None = None,
        offset: int = 0,
        limit: int = 50
    ) -> list[Serie]:
        return self._api.search( # type: ignore
            query,
            year=year,
            company=company,
            country=country,
            director=director,
            language=language,
            network=network,
            remote_id=remote_id,
            type="series",
            offset=offset,
            limit=limit)

    # def search_movies(
    #     self,
    #     query: str,
    #     year: int | None = None,
    #     company: str | None = None,
    #     country: str | None = None,
    #     director: str | None = None,
    #     language: str | None = None,
    #     network: str | None = None,
    #     remote_id: str | None = None,
    #     offset: int = 0,
    #     limit: int = 50
    # ) -> list[Movie]:

    # def search_company(
    #     self,
    #     query: str,
    #     director: str | None = None,
    #     type: str | None = None,
    #     network: str | None = None,
    #     remote_id: str | None = None,
    #     offset: int = 0,
    #     limit: int = 50
    # ) -> list[Company]:

    def get_episodes(self, show_id: str) -> list[Episode]:
        return self._api.get_series_episodes(id=show_id)["episodes"] # type: ignore