"""Offline: the evidence cache and the container CPU limit, no model downloads."""

import sys
from unittest.mock import Mock

import numpy as np
import pytest
from app.services import embedding_service as module
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def service():
    """A real instance with a stub model; the cache is class-level, so reset it."""
    EmbeddingService._document_cache.clear()
    instance = EmbeddingService.__new__(EmbeddingService)
    instance._model = Mock()
    instance._model.encode.side_effect = lambda texts, **kwargs: np.array(
        [[float(len(text)), 1.0] for text in texts])
    return instance


def test_repeated_evidence_is_encoded_once(service):
    first = service.embed_documents(["Python seit 2020", "React"])
    second = service.embed_documents(["Python seit 2020", "React"])
    assert service._model.encode.call_count == 1
    assert [vector.tolist() for vector in first] == [vector.tolist() for vector in second]


def test_only_the_uncached_texts_reach_the_model(service):
    service.embed_documents(["Python"])
    service.embed_documents(["Python", "Docker"])
    assert service._model.encode.call_args_list[-1].args[0] == ["Docker"]


def test_order_and_duplicates_are_preserved(service):
    vectors = service.embed_documents(["React", "Python", "React"])
    assert len(vectors) == 3
    assert vectors[0].tolist() == vectors[2].tolist()
    assert vectors[1].tolist() != vectors[0].tolist()
    assert service._model.encode.call_args.args[0] == ["React", "Python"]


def test_returned_vectors_do_not_alias_the_cache(service):
    service.embed_documents(["Python"])[0][0] = 99.0
    assert service.embed_documents(["Python"])[0][0] != 99.0


def test_cache_is_bounded(service, monkeypatch):
    monkeypatch.setattr(EmbeddingService, "_CACHE_SIZE", 2)
    for text in ["a", "bb", "ccc", "dddd"]:
        service.embed_documents([text])
    assert len(EmbeddingService._document_cache) == 2


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_input_is_rejected(service, text):
    with pytest.raises(ValueError):
        service.embed_documents([text])


def cgroup(tmp_path, monkeypatch, files):
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    monkeypatch.setattr(module, "Path", lambda p: tmp_path / p.lstrip("/"))


def test_cpu_limit_from_cgroup_v2(tmp_path, monkeypatch):
    cgroup(tmp_path, monkeypatch, {"sys/fs/cgroup/cpu.max": "200000 100000"})
    assert module._cgroup_cpu_limit() == 2


def test_cpu_limit_absent_when_quota_is_unlimited(tmp_path, monkeypatch):
    cgroup(tmp_path, monkeypatch, {"sys/fs/cgroup/cpu.max": "max 100000"})
    assert module._cgroup_cpu_limit() is None


def test_cpu_limit_from_cgroup_v1(tmp_path, monkeypatch):
    cgroup(tmp_path, monkeypatch, {"sys/fs/cgroup/cpu/cpu.cfs_quota_us": "150000",
                                   "sys/fs/cgroup/cpu/cpu.cfs_period_us": "100000"})
    assert module._cgroup_cpu_limit() == 2


def test_cpu_limit_is_none_without_cgroup_files(tmp_path, monkeypatch):
    cgroup(tmp_path, monkeypatch, {})
    assert module._cgroup_cpu_limit() is None


def test_torch_threads_are_only_ever_lowered(monkeypatch):
    torch = Mock()
    torch.get_num_threads.return_value = 2
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setattr(module.settings, "TORCH_NUM_THREADS", 8)
    module.configure_torch_threads()
    torch.set_num_threads.assert_not_called()


def test_explicit_setting_overrides_the_cgroup(monkeypatch):
    torch = Mock()
    torch.get_num_threads.return_value = 32
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setattr(module.settings, "TORCH_NUM_THREADS", 2)
    monkeypatch.setattr(module, "_cgroup_cpu_limit", lambda: 8)
    module.configure_torch_threads()
    torch.set_num_threads.assert_called_once_with(2)
