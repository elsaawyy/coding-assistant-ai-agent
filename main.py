#!/usr/bin/env python3
"""
Coding Assistant AI Agent - Main Entry Point
An autonomous agent that analyzes and improves GitHub repositories
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.core_agent import CodingAssistantAgent

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Coding Assistant AI Agent - Automatically analyze and improve GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://github.com/psf/requests
  python main.py https://github.com/psf/requests --max-fixes 10
  python main.py https://github.com/psf/requests --min-severity 2
  python main.py https://github.com/psf/requests --output report.json
        """
    )
    
    parser.add_argument(
        'repo_url',
        help='GitHub repository URL to analyze'
    )
    
    parser.add_argument(
        '--branch', '-b',
        default='main',
        help='Branch to analyze (default: main)'
    )
    
    parser.add_argument(
        '--max-fixes', '-m',
        type=int,
        default=20,
        help='Maximum number of fixes to apply (default: 20)'
    )
    
    parser.add_argument(
        '--min-severity', '-s',
        type=int,
        choices=[0, 1, 2, 3, 4],
        default=1,
        help='Minimum severity to fix (0=INFO, 1=LOW, 2=MEDIUM, 3=HIGH, 4=CRITICAL)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='analysis_report.json',
        help='Output file for the report (default: analysis_report.json)'
    )
    
    parser.add_argument(
        '--workspace', '-w',
        default='./workspace',
        help='Workspace directory for cloning repositories (default: ./workspace)'
    )
    
    parser.add_argument(
        '--extensions', '-e',
        nargs='+',
        default=['.py'],
        help='File extensions to analyze (default: .py)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress detailed output'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Analyze but do not apply fixes'
    )
    
    return parser.parse_args()

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🤖  CODING ASSISTANT AI AGENT  v1.0.0                   ║
║                                                              ║
║     Autonomous Code Analysis & Improvement System           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_config(config: dict):
    """Print configuration summary"""
    print("\n📋 Configuration:")
    print(f"  • Repository: {config['repo_url']}")
    print(f"  • Branch: {config['branch']}")
    print(f"  • Max fixes: {config['max_fixes']}")
    print(f"  • Min severity: {config['min_severity']}")
    print(f"  • Extensions: {', '.join(config['extensions'])}")
    print(f"  • Workspace: {config['workspace']}")
    print(f"  • Dry run: {config['dry_run']}")
    print()

async def main():
    """Main entry point"""
    args = parse_arguments()
    
    if not args.quiet:
        print_banner()
    
    # Prepare configuration
    config = {
        'repository_url': args.repo_url,
        'branch': args.branch,
        'max_fixes_per_run': args.max_fixes if not args.dry_run else 0,
        'min_severity': args.min_severity,
        'file_extensions': args.extensions,
        'workspace_dir': args.workspace,
        'dry_run': args.dry_run,
        'max_retries': 3,
        'max_actions_per_file': 10,
        'confidence_threshold': 0.7,
        'exclude_patterns': [
            'test_', '_test', 'tests/', 'venv/', 'env/',
            '__pycache__/', '.git/', 'node_modules/'
        ]
    }
    
    if not args.quiet:
        print_config(config)
    
    # Create workspace directory
    Path(args.workspace).mkdir(exist_ok=True)
    
    try:
        # Initialize and run agent
        agent = CodingAssistantAgent(config)
        report = await agent.run(args.repo_url)
        
        # Save report
        agent.save_report(report, args.output)
        
        # Print summary
        if not args.quiet:
            print("\n✨ Analysis completed successfully!")
            
            # Exit with appropriate code
            if report['summary']['fixes_applied'] > 0:
                print("\n✅ Improvements were applied to the codebase.")
                sys.exit(0)
            else:
                print("\nℹ️ No fixes were applied. Check the report for details.")
                sys.exit(0)
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_simple_test():
    """Simple test function for quick validation"""
    print("Running quick test...")
    
    # Test configuration
    config = {
        'repository_url': 'https://github.com/psf/requests',
        'branch': 'main',
        'max_fixes_per_run': 5,
        'min_severity': 1,
        'file_extensions': ['.py'],
        'workspace_dir': './test_workspace',
        'dry_run': True,
        'max_retries': 1,
        'max_actions_per_file': 5,
        'confidence_threshold': 0.5,
        'exclude_patterns': ['test_', 'tests/']
    }
    
    async def run_test():
        agent = CodingAssistantAgent(config)
        report = await agent.run('https://github.com/psf/requests')
        print(f"\nTest results: {report['summary']}")
        return report
    
    return asyncio.run(run_test())

if __name__ == "__main__":
    # Check if running in test mode
    if len(sys.argv) == 1:
        print("No arguments provided. Running quick test on 'requests' repository...")
        print("For normal usage: python main.py <repository_url>\n")
        run_simple_test()
    else:
        asyncio.run(main())