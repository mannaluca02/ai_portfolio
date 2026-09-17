import pytest
from pydantic import ValidationError
from app.schemas.chat import ChatRequest, ChatMode
from app.services.sentence_service import split_sentences
from app.services.generator_service import GeneratorService
from app.services.chatbot_service import ChatbotService


def test_language_validation():
    assert ChatRequest(message='Hello').language == 'de'
    assert ChatRequest(message='Hello', language='en').language == 'en'
    with pytest.raises(ValidationError):
        ChatRequest(message='Hello', language='fr')


def test_english_abbreviations_and_numbers():
    assert split_sentences('He uses tools, e.g. Python [1]. He worked at Example Inc. in Basel [2].', language='en') == [
        'He uses tools, e.g. Python [1].', 'He worked at Example Inc. in Basel [2].']
    assert len(split_sentences('The team had 9. He joined later [1].', language='en')) == 2


def test_english_system_prompt_retains_citation_rules():
    generator = object.__new__(GeneratorService)
    prompt = generator._build_system_prompt(language='en')
    assert 'English' in prompt
    assert '[N]' in prompt
    assert 'I cannot find that information in my portfolio data.' in prompt


def test_english_no_information():
    response = ChatbotService._no_information(ChatMode.NATURAL, language='en')
    assert response.answer == 'I cannot find that information in my portfolio data.'
    assert response.sources == []
