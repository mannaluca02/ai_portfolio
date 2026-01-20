"""
Test script for chatbot improvements
Tests intent detection, MMR diversification, and improved prompts
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import get_db
from app.services.chatbot_service import get_chatbot_service
from app.schemas.chat import ChatMode
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_query(service, query: str, expected_intent: str):
    """Test a single query and display results"""
    print("\n" + "=" * 80)
    print(f"🔍 QUERY: {query}")
    print(f"📋 Expected Intent: {expected_intent}")
    print("=" * 80)

    try:
        # Process query
        response = service.process_message(query, mode=ChatMode.NATURAL)

        # Display results
        print(f"\n✅ Answer:\n{response.answer}\n")
        print(f"📊 Confidence: {response.confidence:.2%}")
        print(f"✓ Verified: {response.verification.is_verified if response.verification else 'N/A'}")
        print(f"\n📚 Sources ({len(response.sources)}):")

        # Track table distribution
        table_counts = {}
        for source in response.sources:
            table = source.table
            table_counts[table] = table_counts.get(table, 0) + 1
            print(f"  [{source.index}] {source.title}")
            print(f"      Table: {table} | Similarity: {source.similarity:.2%}")

        # Show table distribution
        print(f"\n📈 Table Distribution:")
        for table, count in sorted(table_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {table}: {count}")

        print(f"\n⏱️  Processing Time: {response.metadata.get('processing_time_ms', 0)}ms")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run test queries"""
    print("\n🚀 Testing Chatbot Improvements")
    print("=" * 80)

    # Get database session
    db = next(get_db())
    service = get_chatbot_service(db)

    # Test queries targeting different problems
    test_cases = [
        # Problem #3: Technical experience should show projects first, not just skills
        ("Hat Luca Erfahrung mit Python?", "TECHNICAL_EXPERIENCE (projects > skills)"),

        # Problem #4: Contact should only appear for explicit contact queries
        ("Wie kann ich Luca erreichen?", "CONTACT (only contact_info + social_links)"),

        # Problem #4: Social links for specific platforms
        ("Was ist Lucas GitHub?", "CONTACT (social_links)"),

        # Work experience query
        ("Wo arbeitet Luca?", "WORK (work_experiences)"),

        # Project query
        ("Welche Projekte hat Luca gemacht?", "PROJECT (projects)"),

        # General query - should not include contact
        ("Was kann Luca?", "GENERAL (no contact)"),
    ]

    results = []
    for query, expected in test_cases:
        success = test_query(service, query, expected)
        results.append((query, success))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for query, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {query[:50]}...")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Close database
    db.close()


if __name__ == "__main__":
    main()
