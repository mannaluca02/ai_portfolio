from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config import settings
from app.services import generator_service
from app.services.retriever_service import SearchResult

# Models measured end to end on the production-log questions that also accept
# max_tokens. The gpt-5 family rejects that parameter and needs a client change.
MEASURED_MODELS = {"gpt-4o-mini", "gpt-4.1-mini"}


def test_configured_model_was_measured_and_accepts_max_tokens():
    """gpt-3.5-turbo cited every sentence in only 58 percent of answers."""
    assert settings.OPENAI_MODEL in MEASURED_MODELS


def test_natural_mode_limits_allow_a_real_visitor_session():
    assert settings.RATE_LIMIT_NATURAL_DAILY >= 50
    assert settings.RATE_LIMIT_NATURAL_MONTHLY >= 400


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


def test_english_personal_answers_identify_the_owner_without_inventing_age():
    generator = generator_service.GeneratorService.__new__(generator_service.GeneratorService)
    prompt = generator._build_system_prompt('en')
    assert 'name supplied in the context' in prompt
    assert 'Use the supplied computed age' in prompt
    assert "do not attribute the portfolio owner's age to the visitor" in prompt
