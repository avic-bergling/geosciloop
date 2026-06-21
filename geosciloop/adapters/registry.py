from __future__ import annotations

from pathlib import Path

from geosciloop.adapters.fixture_adapter import DEFAULT_FIXTURE_DIR, FixturePopulationAdapter
from geosciloop.adapters.gee_adapter import FixtureGEEAdapter
from geosciloop.adapters.osm_adapter import FixtureOSMAdapter
from geosciloop.adapters.stac_adapter import FixtureSTACAdapter


def build_adapter(name: str, fixture_dir: Path | str = DEFAULT_FIXTURE_DIR):
    adapters = {
        "fixture_stac": FixtureSTACAdapter,
        "fixture_gee": FixtureGEEAdapter,
        "fixture_osm": FixtureOSMAdapter,
        "fixture_population": FixturePopulationAdapter,
    }
    try:
        adapter_cls = adapters[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported adapter for v0.2 dry-run: {name}") from exc
    return adapter_cls(fixture_dir=fixture_dir)
