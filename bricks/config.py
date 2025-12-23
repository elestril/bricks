from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Sequence, Tuple

from ruamel.yaml import YAML

GRID_UNIT_MM = 12.7
TYPE_HEIGHTS = {
    "Tile": 0.25,
    "Plate": 0.25,
    "Wall": 4.0,
    "Riser": 1.0,
}

yaml = YAML(typ="safe")


@dataclass(frozen=True)
class BrickSpec:
    name: str
    rel_path: Path
    size_units: Tuple[float, float, float]
    params: Dict[str, Any]
    set_name: str
    brick_type: str
    family: str
    variant: str | None = None

    @property
    def size_mm(self) -> Tuple[float, float, float]:
        return tuple(d * GRID_UNIT_MM for d in self.size_units)

    def metadata(self) -> Dict[str, Any]:
        return {
            "set": self.set_name,
            "type": self.brick_type,
            "family": self.family,
            "variant": self.variant,
            "path": str(self.rel_path),
            "size": list(self.size_units),
            "size_mm": list(self.size_mm),
            "parameters": _sanitize(self.params),
        }


def build_from_yaml(config_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Generate STL files based on the supplied YAML configuration."""

    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    data = _load_yaml(config_path)
    specs = list(_compile_specs(data))

    parameter_sets: Dict[str, Any] = {}
    for spec in specs:
        brick_dir = output_dir / spec.rel_path
        brick_dir.mkdir(parents=True, exist_ok=True)
        stl_path = brick_dir / f"{spec.name}.stl"
        _write_box_stl(stl_path, spec.size_mm, spec.name)
        parameter_sets[spec.name] = spec.metadata()

    _write_config_json(output_dir, parameter_sets)
    return parameter_sets


def _load_yaml(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle) or {}


def _compile_specs(data: Mapping[str, Any]) -> Iterator[BrickSpec]:
    generate_blocks = data.get("generate", {}) or {}
    for block in generate_blocks.values():
        yield from _compile_block(block)


def _compile_block(block: Mapping[str, Any]) -> Iterator[BrickSpec]:
    base_config = block.get("config", {}) or {}
    generate_config = block.get("generate", {}) or {}
    combos = list(_expand_generate(generate_config)) or [{}]
    condition = block.get("condition")

    for combo in combos:
        merged = _merge_config(base_config, combo)
        if condition:
            rendered = condition.format_map(_SafeDict(merged))
            if not _evaluate_condition(rendered):
                continue
        yield _spec_from_params(merged)


def _expand_generate(entries: Mapping[str, Any]) -> Iterable[Dict[str, Any]]:
    if not entries:
        return [{}]
    keys = list(entries.keys())
    values = [list(_as_iterable(entries[key])) for key in keys]
    return (dict(zip(keys, combo)) for combo in product(*values))


def _as_iterable(value: Any) -> Iterable[Any]:
    if isinstance(value, (list, tuple)):
        return value
    return (value,)


def _merge_config(base: Mapping[str, Any], overrides: Mapping[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(base)
    merged.update(overrides)
    return merged


def _evaluate_condition(expression: str) -> bool:
    try:
        return bool(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return False


def _spec_from_params(params: MutableMapping[str, Any]) -> BrickSpec:
    set_name = str(params.get("set", "Bricks"))
    brick_type = str(params.get("type", "Tile"))
    family = str(params.get("family", "Square"))
    variant = params.get("variant")

    size_units = _extract_size_units(brick_type, family, params)
    rel_path = Path(str(params.get("path", f"{set_name}/{brick_type}s")))
    name = str(params.get("name") or _derive_name(set_name, brick_type, family, size_units, variant))

    sanitized_params = dict(params)
    sanitized_params["path"] = str(rel_path)

    return BrickSpec(
        name=name,
        rel_path=rel_path,
        size_units=size_units,
        params=sanitized_params,
        set_name=set_name,
        brick_type=brick_type,
        family=family,
        variant=variant if variant is None else str(variant),
    )


def _extract_size_units(brick_type: str, family: str, params: Mapping[str, Any]) -> Tuple[float, float, float]:
    def _to_float(value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    size_config = params.get("size")
    size_list: Sequence[Any] = size_config if isinstance(size_config, (list, tuple)) else ()

    x_units = _to_float(params.get("x"), _to_float(size_list[0], 1.0) if len(size_list) > 0 else 1.0)
    y_units = _to_float(params.get("y"), _to_float(size_list[1], 1.0) if len(size_list) > 1 else 1.0)

    if family in {"HexR", "HexS"} and params.get("y") is None and len(size_list) <= 1:
        y_units = x_units

    if len(size_list) > 2:
        z_units = _to_float(size_list[2], TYPE_HEIGHTS.get(brick_type, 1.0))
    else:
        z_units = _to_float(params.get("z"), TYPE_HEIGHTS.get(brick_type, 1.0))

    return (x_units, y_units, z_units)


def _derive_name(set_name: str, brick_type: str, family: str, size_units: Tuple[float, float, float], variant: Any) -> str:
    size_token = _format_size_token(family, size_units)
    parts = [set_name, brick_type, size_token]
    if variant:
        parts.append(str(variant))
    return "-".join(parts)


def _format_size_token(family: str, size_units: Tuple[float, float, float]) -> str:
    x_str = _format_dimension(size_units[0])
    y_str = _format_dimension(size_units[1])

    if family == "HexR" or family == "HexS":
        return f"{family}{x_str}"
    if family == "Hex":
        return f"{family}{x_str}x{y_str}"
    if family == "Long":
        return f"{x_str}x{y_str}L"
    return f"{x_str}x{y_str}"


def _format_dimension(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:g}"


def _write_box_stl(path: Path, size_mm: Tuple[float, float, float], name: str) -> None:
    dx, dy, dz = size_mm
    vertices = {
        "000": (0.0, 0.0, 0.0),
        "100": (dx, 0.0, 0.0),
        "010": (0.0, dy, 0.0),
        "110": (dx, dy, 0.0),
        "001": (0.0, 0.0, dz),
        "101": (dx, 0.0, dz),
        "011": (0.0, dy, dz),
        "111": (dx, dy, dz),
    }

    facets = [
        ((0.0, 0.0, -1.0), ("000", "100", "110")),
        ((0.0, 0.0, -1.0), ("000", "110", "010")),
        ((0.0, 0.0, 1.0), ("001", "011", "111")),
        ((0.0, 0.0, 1.0), ("001", "111", "101")),
        ((0.0, -1.0, 0.0), ("000", "001", "101")),
        ((0.0, -1.0, 0.0), ("000", "101", "100")),
        ((0.0, 1.0, 0.0), ("010", "110", "111")),
        ((0.0, 1.0, 0.0), ("010", "111", "011")),
        ((-1.0, 0.0, 0.0), ("000", "010", "011")),
        ((-1.0, 0.0, 0.0), ("000", "011", "001")),
        ((1.0, 0.0, 0.0), ("100", "101", "111")),
        ((1.0, 0.0, 0.0), ("100", "111", "110")),
    ]

    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"solid {name}\n")
        for normal, keys in facets:
            handle.write(
                "  facet normal {0:.6f} {1:.6f} {2:.6f}\n".format(*normal)
            )
            handle.write("    outer loop\n")
            for key in keys:
                vertex = vertices[key]
                handle.write(
                    "      vertex {0:.6f} {1:.6f} {2:.6f}\n".format(*vertex)
                )
            handle.write("    endloop\n")
            handle.write("  endfacet\n")
        handle.write(f"endsolid {name}\n")


def _write_config_json(output_dir: Path, parameter_sets: Mapping[str, Any]) -> None:
    payload = {
        "fileFormatVersion": "1",
        "parameterSets": parameter_sets,
    }
    with (output_dir / "config.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _sanitize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(v) for v in value]
    return value
