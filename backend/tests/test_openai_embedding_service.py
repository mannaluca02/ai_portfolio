"""Offline provider contract; no credentials, database, or model downloads."""

from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from app.services.openai_embedding_service import OpenAIEmbeddingService


def response(vectors, indices=None, model="text-embedding-3-small"):
    return SimpleNamespace(
        model=model,
        data=[SimpleNamespace(index=i, embedding=v) for i, v in zip(
            range(len(vectors)) if indices is None else indices, vectors, strict=True
        )],
    )


def provider(cache_size=2):
    client = Mock()
    client.with_options.return_value = client
    client.embeddings.create.return_value = response([[1.0] * 1024])
    return OpenAIEmbeddingService(client, cache_size=cache_size), client


def test_explicit_model_dimensions_and_bounded_requests():
    service, client = provider()
    vector = service.generate_embedding("Docker")
    client.with_options.assert_called_once_with(timeout=5.0, max_retries=0)
    client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small", dimensions=1024,
        encoding_format="float", input=["Docker"],
    )
    assert vector.shape == (1024,)
    assert service.get_embedding_dimension() == 1024
    assert service.space_id == "openai:text-embedding-3-small:1024"


def test_cache_returns_independent_arrays_and_evicts_lru():
    service, client = provider()
    service.generate_embedding("Docker")[0] = 999
    assert service.generate_embedding("Docker")[0] == 1
    service.generate_embedding("Python")
    service.generate_embedding("Docker")
    service.generate_embedding("PyTorch")
    assert client.embeddings.create.call_count == 3
    service.generate_embedding("Python")
    assert client.embeddings.create.call_count == 4


def test_batch_preserves_order_duplicates_and_response_indices():
    service, client = provider()
    client.embeddings.create.return_value = response(
        [[2.0] * 1024, [1.0] * 1024], indices=[1, 0]
    )
    result = service.generate_embeddings(["Docker", "Python", "Docker"])
    assert [vector[0] for vector in result] == [1, 2, 1]
    assert client.embeddings.create.call_args.kwargs["input"] == ["Docker", "Python"]
    result[0][0] = 8
    assert result[2][0] == 1


@pytest.mark.parametrize("texts", [[], [""], [" "], ["valid", ""], [None]])
def test_rejects_invalid_input_without_silently_dropping_rows(texts):
    service, client = provider()
    with pytest.raises(ValueError):
        service.generate_embeddings(texts)
    client.embeddings.create.assert_not_called()


@pytest.mark.parametrize("bad", [
    response([[1.0]]), response([[0.0] * 1024]),
    response([[float("nan")] * 1024]), response([[float("inf")] * 1024]),
    response([[1.0] * 1024], indices=[2]), response([]),
    response([[1.0] * 1024], model="different-model"),
    response([[1.0] * 1024, [2.0] * 1024], indices=[0, 0]),
])
def test_bad_response_is_rejected_and_not_cached(bad):
    service, client = provider()
    client.embeddings.create.return_value = bad
    with pytest.raises(ValueError):
        service.generate_embedding("Docker")
    client.embeddings.create.return_value = response([[1.0] * 1024])
    assert service.generate_embedding("Docker")[0] == 1
    assert client.embeddings.create.call_count == 2


def test_transport_errors_propagate_without_fake_vectors():
    service, client = provider()
    client.embeddings.create.side_effect = TimeoutError("offline")
    with pytest.raises(TimeoutError):
        service.generate_embedding("Docker")


def test_cache_can_be_disabled():
    service, client = provider(cache_size=0)
    service.generate_embedding("Docker")
    service.generate_embedding("Docker")
    assert client.embeddings.create.call_count == 2


def test_similarity_is_cosine_and_rejects_invalid_vectors():
    service, _ = provider()
    vector = np.ones(1024)
    assert service.calculate_similarity(vector, vector) == pytest.approx(1)
    assert service.calculate_similarity(vector, -vector) == pytest.approx(-1)
    with pytest.raises(ValueError):
        service.calculate_similarity(vector, np.zeros(1024))


@pytest.mark.parametrize("kwargs", [{"cache_size": -1}, {"timeout": 0}])
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        OpenAIEmbeddingService(Mock(), **kwargs)
