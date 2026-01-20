"""
Test script for query improvements: adaptive threshold + fallback retrieval
Tests the chatbot with previously problematic short/generic queries
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import SessionLocal
from app.services.chatbot_service import ChatbotService
from app.schemas.chat import ChatMode
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_query(chatbot: ChatbotService, query: str, expected_behavior: str):
    """Test a single query and display results"""
    print("\n" + "="*80)
    print(f"🔍 TESTING: {query}")
    print(f"📋 Expected: {expected_behavior}")
    print("="*80)

    try:
        response = chatbot.process_message(query, mode=ChatMode.NATURAL)

        print(f"\n✅ Answer:\n{response.answer}\n")
        print(f"📊 Metadata:")
        print(f"   - Confidence: {response.confidence:.2%}")
        print(f"   - Sources found: {len(response.sources)}")
        print(f"   - Processing time: {response.metadata.get('processing_time_ms', 'N/A')}ms")
        print(f"   - Verified: {response.verification.is_verified if response.verification else 'N/A'}")

        if response.sources:
            print(f"\n📚 Sources:")
            for source in response.sources[:3]:  # Show top 3
                print(f"   [{source.index}] {source.title} (similarity: {source.similarity:.2%})")

        # Check if we got a valid answer
        no_info_found = "keine relevanten informationen" in response.answer.lower()
        if no_info_found:
            print("\n⚠️  WARNING: No relevant information found")
        else:
            print("\n✅ SUCCESS: Answer provided")

        return not no_info_found

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run test suite for query improvements"""
    print("\n" + "="*80)
    print("🧪 TESTING QUERY IMPROVEMENTS")
    print("   Option 2: Adaptive Threshold")
    print("   Option 3: Fallback Retrieval")
    print("="*80)

    # Create database session
    db = SessionLocal()

    try:
        # Initialize chatbot service
        chatbot = ChatbotService(db)

        # Test cases: (query, expected_behavior)
        test_cases = [
            # Very short queries (1-3 words)
            ("Welche Projekte", "Should find projects with adaptive threshold 0.15"),
            ("Wer ist Luca", "Should find contact/bio info with adaptive threshold 0.15"),
            ("Skills", "Should find skills with adaptive threshold 0.15"),

            # Short queries (4-6 words)
            ("Welche Projekte wurden gemacht", "Should find projects with adaptive threshold 0.20-0.25"),
            ("Was für Erfahrung hat Luca", "Should find work experience with adaptive threshold 0.20-0.25"),
            ("Welche Firmen hat er gearbeitet", "Should find work experiences"),

            # Medium queries (should work already)
            ("Mit welchen Technologien hat Luca Erfahrung", "Should find skills/projects"),
            ("Welche Ausbildung hat Luca absolviert", "Should find education"),

            # Generic overview questions
            ("Erzähl mir über Luca", "Should find contact info or general bio"),
            ("Was kann Luca", "Should find skills/experience"),
        ]

        results = []
        for query, expected in test_cases:
            success = test_query(chatbot, query, expected)
            results.append((query, success))

        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)

        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        print(f"\nTotal tests: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Success rate: {success_rate:.1f}%")

        print("\nDetailed Results:")
        for query, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {query}")

        if success_rate >= 80:
            print("\n🎉 EXCELLENT: Query improvements are working well!")
        elif success_rate >= 60:
            print("\n✅ GOOD: Most queries are working, some edge cases remain")
        else:
            print("\n⚠️  NEEDS IMPROVEMENT: Many queries still failing")

    finally:
        db.close()


if __name__ == "__main__":
    main()
