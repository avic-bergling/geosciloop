from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
from urllib.request import urlretrieve

from geosciloop.adapters.provenance import DataSourceProvenance


class OptionalDependencyNotAvailable(RuntimeError):
    """Raised when an optional adapter dependency is needed but not installed."""


def _item_to_dict(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    if hasattr(item, "to_dict"):
        return item.to_dict()
    payload = {
        "id": getattr(item, "id", None),
        "collection": getattr(item, "collection_id", None) or getattr(item, "collection", None),
        "properties": getattr(item, "properties", {}),
        "assets": {},
    }
    assets = getattr(item, "assets", {})
    for key, asset in assets.items():
        payload["assets"][key] = {"href": getattr(asset, "href", None)}
    return payload


class STACAdapter:
    def __init__(self, catalog_url: str, client: Any | None = None):
        self.catalog_url = catalog_url
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        try:
            from pystac_client import Client
        except ImportError as exc:
            raise OptionalDependencyNotAvailable(
                "STAC access requires optional dependency 'pystac-client'. Install a STAC extra or inject a client."
            ) from exc
        self.client = Client.open(self.catalog_url)
        return self.client

    def search(
        self,
        collections: list[str],
        bbox: list[float],
        datetime_range: str,
        query: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[DataSourceProvenance]:
        search_kwargs = {
            "collections": collections,
            "bbox": bbox,
            "datetime": datetime_range,
            "query": query or {},
            "limit": limit,
        }
        search = self._client().search(**search_kwargs)
        records: list[DataSourceProvenance] = []
        for item in search.items():
            payload = _item_to_dict(item)
            assets = [
                {"asset_key": key, "href": asset.get("href"), **{k: v for k, v in asset.items() if k != "href"}}
                for key, asset in payload.get("assets", {}).items()
            ]
            records.append(
                DataSourceProvenance(
                    provider="STAC",
                    dataset=payload.get("collection") or ",".join(collections),
                    source_type="imagery",
                    query={**search_kwargs, "catalog_url": self.catalog_url, "item_id": payload.get("id")},
                    assets=assets,
                    temporal_extent={"datetime": payload.get("properties", {}).get("datetime"), "query": datetime_range},
                    spatial_extent={"bbox": bbox},
                    credentials_required=False,
                    access_method="stac_search",
                )
            )
        return records

    def download_assets(
        self,
        records: list[DataSourceProvenance],
        output_dir: Path,
        asset_keys: list[str] | None = None,
        downloader: Callable[[str, Path], Any] | None = None,
    ) -> list[DataSourceProvenance]:
        output_dir.mkdir(parents=True, exist_ok=True)
        transfer = downloader or (lambda href, path: urlretrieve(href, path))
        downloaded: list[DataSourceProvenance] = []
        for record in records:
            selected_assets = []
            for asset in record.assets:
                key = asset.get("asset_key")
                href = asset.get("href")
                if not href or (asset_keys is not None and key not in asset_keys):
                    continue
                target = output_dir / f"{record.dataset}_{record.query.get('item_id')}_{key}".replace("/", "_")
                transfer(href, target)
                selected_assets.append({**asset, "local_path": str(target)})
            downloaded.append(
                DataSourceProvenance(
                    provider=record.provider,
                    dataset=record.dataset,
                    source_type=record.source_type,
                    query=record.query,
                    assets=selected_assets,
                    temporal_extent=record.temporal_extent,
                    spatial_extent=record.spatial_extent,
                    credentials_required=record.credentials_required,
                    access_method="stac_download",
                    notes=["Downloaded assets are recorded for provenance; content validation is a separate step."],
                )
            )
        return downloaded
