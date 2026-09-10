from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from app.config import settings
from app.services import generator_service
from app.services.retriever_service import SearchResult


def test_generator_uses_bounded_configuration_and_shared_evidence(monkeypatch):
    client = Mock()
    constructor = Mock(return_value=client)
    monkeypatch.setattr(generator_service, "OpenAI", constructor)
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Luca nutzt Python [1]."), finish_reason="stop")],
        usage=SimpleNamespace(total_tokens=32))
    generator = generator_service.GeneratorService()
    source = SearchResult(1, 'skills', 'Python', 'Luca nutzt Python.', 'python', 'skills', 'python', .8,
                          {'years_of_experience': 2})
    result = generator.generate_response('Python?', [source])
    constructor.assert_called_once_with(api_key=settings.OPENAI_API_KEY,
                                       timeout=settings.OPENAI_TIMEOUT_SECONDS, max_retries=0)
    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs['max_tokens'] == 300
    assert kwargs['model'] == settings.OPENAI_MODEL
    assert source.evidence_text() in kwargs['messages'][1]['content']
    assert result['finish_reason'] == 'stop'
    assert result['sources'][0]['index'] == 1
    assert result['tokens_used'] == 32
    assert not generator.generate_response('Unknown', [])['sources']
    client.chat.completions.create.side_effect = TimeoutError()
    with pytest.raises(TimeoutError):
        generator.generate_response('Python?', [source])
