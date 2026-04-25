"""Simple test script for the agent"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.core_agent import CodingAssistantAgent

async def test_basic():
    """Test basic agent functionality"""
    print("=" * 60)
    print("🧪 TESTING CODING ASSISTANT AGENT")
    print("=" * 60)
    
    config = {
        'repository_url': 'https://github.com/psf/requests',
        'branch': 'main',
        'max_fixes_per_run': 3,
        'min_severity': 1,
        'file_extensions': ['.py'],
        'workspace_dir': './test_workspace',
        'dry_run': False,  # Don't actually write fixes
        'max_retries': 1,
        'max_actions_per_file': 5,
        'confidence_threshold': 0.5,
        'exclude_patterns': ['test_', 'tests/']
    }
    
    try:
        agent = CodingAssistantAgent(config)
        report = await agent.run('https://github.com/psf/requests')
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nResults:")
        print(f"  Files analyzed: {report['summary']['files_analyzed']}")
        print(f"  Total issues: {report['summary']['total_issues']}")
        print(f"  Fixes applied: {report['summary']['fixes_applied']}")
        
        return True
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic())
    sys.exit(0 if success else 1)