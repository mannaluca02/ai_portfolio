"""
Test script for source numbering and quality issues
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


def test_query(service, query: str, issue: str):
    """Test a single query and display results"""
    print("\n" + "=" * 80)
    print(f"🔍 QUERY: {query}")
    print(f"🐛 Testing Issue: {issue}")
    print("=" * 80)

    try:
        # Process query
        response = service.process_message(query, mode=ChatMode.NATURAL)

        # Display results
        print(f"\n✅ Answer:\n{response.answer}\n")
        print(f"📊 Confidence: {response.confidence:.2%}")
        print(f"✓ Verified: {response.verification.is_verified if response.verification else 'N/A'}")
        print(f"\n📚 Sources ({len(response.sources)}):")

        # Check for issues
        issues = []

        for source in response.sources:
            print(f"  [{source.index}] {source.title}")
            print(f"      Table: {source.table} | Similarity: {source.similarity:.2%}")

            # Flag low-quality sources
            if source.similarity < 0.40:
                issues.append(f"⚠️  Source [{source.index}] has low similarity: {source.similarity:.2%}")

        # Check citation numbers in answer
        import re
        citations = re.findall(r'\[(\d+)\]', response.answer)
        max_citation = max([int(c) for c in citations]) if citations else 0

        if max_citation > len(response.sources):
            issues.append(f"❌ Citation mismatch: Answer references [{max_citation}] but only {len(response.sources)} sources available")

        # Report issues
        if issues:
            print("\n⚠️  ISSUES DETECTED:")
            for issue_msg in issues:
                print(f"  {issue_msg}")
        else:
            print("\n✅ No issues detected")

        print(f"\n⏱️  Processing Time: {response.metadata.get('processing_time_ms', 0)}ms")

        return len(issues) == 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run test queries for reported issues"""
    print("\n🚀 Testing Source Quality & Citation Issues")
    print("=" * 80)

    # Get database session
    db = next(get_db())
    service = get_chatbot_service(db)

    # Test cases for reported issues
    test_cases = [
        ("Welche skills hat Luca?", "Issue #1: Wrong citation numbers [3][6] instead of correct sources"),
        ("Hat Luca bereits einmal mit AI oder etwas ähnlichem gearbeitet?", "Issue #2: Novartis IT-Support (35%) appears but irrelevant"),
        ("Hat Luca Erfahrung mit Python?", "General: Should prioritize projects over skills"),
        ("Wie kann ich Luca erreichen?", "Control: Should only show contact info"),
    ]

    results = []
    for query, issue in test_cases:
        success = test_query(service, query, issue)
        results.append((query, success))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for query, success in results:
        status = "✅ PASS" if success else "⚠️  ISSUES"
        print(f"{status}: {query[:50]}...")

    print(f"\nTotal: {passed}/{total} tests passed without issues")

    # Close database
    db.close()


if __name__ == "__main__":
    main()
