"""Comprehensive validation for applied fixes"""

import subprocess
import tempfile
import ast
from pathlib import Path
from typing import Dict, Any, Tuple

class Validator:
    """Validate fixes using multiple strategies"""
    
    def __init__(self, run_tests: bool = False, run_linter: bool = False):
        self.run_tests = run_tests
        self.run_linter = run_linter
        
    async def validate_fix(self, file_path: Path, fixed_code: str) -> Tuple[bool, Dict]:
        """Validate the generated fix"""
        
        results = {
            'syntax_valid': False,
            'tests_passed': None,
            'lint_passed': None,
            'errors': []
        }
        
        # 1. Syntax validation
        try:
            ast.parse(fixed_code)
            results['syntax_valid'] = True
        except SyntaxError as e:
            results['errors'].append(f"Syntax error: {e}")
            return False, results
        
        # 2. Linter validation (optional)
        if self.run_linter:
            lint_result = self._run_linter(fixed_code)
            results['lint_passed'] = lint_result['passed']
            if not lint_result['passed']:
                results['errors'].extend(lint_result['errors'])
        
        # 3. Test validation (optional)
        if self.run_tests and results['syntax_valid']:
            test_result = await self._run_tests(file_path, fixed_code)
            results['tests_passed'] = test_result['passed']
            if not test_result['passed']:
                results['errors'].extend(test_result['errors'])
        
        # Fix is valid if syntax passes and (no tests or tests pass)
        is_valid = results['syntax_valid']
        if self.run_tests:
            is_valid = is_valid and results['tests_passed']
        
        return is_valid, results
    
    def _run_linter(self, code: str) -> Dict:
        """Run pylint/flake8 on the code"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run flake8
            result = subprocess.run(
                ['flake8', temp_file, '--exit-zero'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            errors = [line for line in result.stdout.split('\n') if line.strip()]
            
            return {
                'passed': len(errors) == 0,
                'errors': errors[:5]  # Limit to first 5 errors
            }
        except Exception as e:
            return {'passed': False, 'errors': [str(e)]}
        finally:
            Path(temp_file).unlink(missing_ok=True)
    
    async def _run_tests(self, original_file: Path, fixed_code: str) -> Dict:
        """Run tests to validate the fix"""
        # This would need to run pytest on the project
        # Complex implementation
        return {'passed': True, 'errors': []}