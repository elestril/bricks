"""Helpers for comparing STL geometry to PythonSCAD meshes via numpy-stl."""

from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable, Sequence, Tuple

from stl import mesh

Triangle = Sequence[Sequence[float]]
Signature = Tuple[float, ...]


def _triangle_signature(triangle: Triangle, decimals: int = 5) -> Signature:
    rounded = [tuple(round(coord, decimals) for coord in vertex) for vertex in triangle]
    rounded.sort()
    return tuple(coord for vertex in rounded for coord in vertex)


def _triangle_signatures(triangles: Iterable[Triangle], decimals: int = 5) -> Counter[Signature]:
    counts: Counter[Signature] = Counter()
    for triangle in triangles:
        counts[_triangle_signature(triangle, decimals=decimals)] += 1
    return counts


def _stl_signatures(path: Path, decimals: int = 5) -> Counter[Signature]:
    stl_mesh = mesh.Mesh.from_file(str(path))
    return _triangle_signatures(stl_mesh.vectors, decimals=decimals)


def _stl_signatures_from_bytes(data: bytes, decimals: int = 5) -> Counter[Signature]:
    stl_mesh = _mesh_from_bytes(data)
    return _triangle_signatures(stl_mesh.vectors, decimals=decimals)


def assert_triangles_match_stl(triangles: Iterable[Triangle], reference: Path, decimals: int = 5) -> None:
    ref_sig = _stl_signatures(reference, decimals=decimals)
    cand_sig = _triangle_signatures(triangles, decimals=decimals)
    _assert_signatures(ref_sig, cand_sig, str(reference))


def assert_stl_bytes_match_file(candidate: bytes, reference: Path, decimals: int = 5) -> None:
    ref_sig = _stl_signatures(reference, decimals=decimals)
    cand_sig = _stl_signatures_from_bytes(candidate, decimals=decimals)
    _assert_signatures(ref_sig, cand_sig, str(reference))


def triangles_from_stl_bytes(data: bytes) -> list[Triangle]:
    return _mesh_from_bytes(data).vectors.tolist()


def _mesh_from_bytes(data: bytes) -> mesh.Mesh:
    with NamedTemporaryFile(suffix=".stl", delete=False) as temp:
        temp.write(data)
        temp_path = temp.name
    try:
        return mesh.Mesh.from_file(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def _assert_signatures(reference_sig: Counter[Signature], candidate_sig: Counter[Signature], label: str) -> None:
    if reference_sig == candidate_sig:
        return

    missing = reference_sig - candidate_sig
    extra = candidate_sig - reference_sig
    msg = [
        f"Triangle mismatch compared to {label}",
        f"Missing triangles: {sum(missing.values())}",
        f"Extra triangles: {sum(extra.values())}",
    ]
    raise AssertionError("\n".join(msg))
