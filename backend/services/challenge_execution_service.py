import subprocess
import tempfile
import os
import time
import json
import resource
import signal
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Secure code execution service for challenges"""
    
    def __init__(self):
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': ['python3'],
                'timeout': 5  # seconds
            },
            'javascript': {
                'extension': '.js',
                'command': ['node'],
                'timeout': 5
            }
        }
    
    def execute_code(self, 
                    code: str, 
                    language: str, 
                    test_input: str,
                    time_limit: int = 5000,
                    memory_limit: int = 256) -> Dict:
        """
        Execute code with given input and return results
        """
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'output': '',
                'execution_time': 0
            }
        
        lang_config = self.supported_languages[language]
        
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=lang_config['extension'],
                delete=False
            ) as code_file:
                # For Python, detect if we need to add function calls
                if language == 'python':
                    modified_code = self._prepare_python_code(code, test_input)
                    code_file.write(modified_code)
                else:
                    code_file.write(code)
                code_file_path = code_file.name
            
            # Create temporary file for input
            with tempfile.NamedTemporaryFile(
                mode='w',
                delete=False
            ) as input_file:
                input_file.write(test_input)
                input_file_path = input_file.name
            
            # Execute code
            start_time = time.time()
            
            try:
                # Run the code with input redirection
                with open(input_file_path, 'r') as stdin_file:
                    process = subprocess.Popen(
                        lang_config['command'] + [code_file_path],
                        stdin=stdin_file,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        preexec_fn=self._set_limits if os.name != 'nt' else None
                    )
                
                # Wait for completion with timeout
                stdout, stderr = process.communicate(timeout=time_limit / 1000)
                execution_time = int((time.time() - start_time) * 1000)
                
                if process.returncode != 0:
                    return {
                        'success': False,
                        'error': stderr,
                        'output': stdout,
                        'execution_time': execution_time
                    }
                
                return {
                    'success': True,
                    'error': '',
                    'output': stdout.strip(),
                    'execution_time': execution_time
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'success': False,
                    'error': f'Time limit exceeded ({time_limit}ms)',
                    'output': '',
                    'execution_time': time_limit
                }
            
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'output': '',
                'execution_time': 0
            }
        
        finally:
            # Clean up temporary files
            for path in [code_file_path, input_file_path]:
                try:
                    os.unlink(path)
                except:
                    pass
    
    def _set_limits(self):
        """Set resource limits for subprocess (Unix only)"""
        try:
            # Limit CPU time
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
            # Limit memory - Note: RLIMIT_AS may not work properly on macOS
            # Try RLIMIT_DATA instead for macOS compatibility
            if hasattr(resource, 'RLIMIT_AS'):
                try:
                    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
                except (ValueError, OSError):
                    # Fall back to RLIMIT_DATA on macOS
                    if hasattr(resource, 'RLIMIT_DATA'):
                        resource.setrlimit(resource.RLIMIT_DATA, (256 * 1024 * 1024, 256 * 1024 * 1024))
        except Exception as e:
            # Log the error but don't fail - resource limits are optional
            logger.warning(f"Could not set resource limits: {str(e)}")
    
    def _prepare_python_code(self, code: str, test_input: str) -> str:
        """Prepare Python code for execution"""
        # Detect common function patterns that need to be called
        lines = code.strip().split('\n')
        
        # Check if code defines functions that need to be called
        function_patterns = [
            ('hello_world', 'result = hello_world()\nif result is not None: print(result)'),
            ('sum_two_numbers', 'sum_two_numbers()'),
            ('even_or_odd', 'even_or_odd()'),
            ('factorial', 'n = int(input())\nprint(factorial(n))'),
            ('fibonacci', 'n = int(input())\nprint(fibonacci(n))'),
            ('reverse_string', 's = input()\nprint(reverse_string(s))'),
        ]
        
        # Check if any function pattern matches
        for func_name, call_code in function_patterns:
            if f'def {func_name}' in code:
                # Add the function call at the end
                return code + '\n\n# Execute the function\n' + call_code
        
        # If no specific pattern matched but there's a def statement,
        # assume the code handles its own execution
        return code


class ChallengeValidator:
    """Service for validating challenge submissions"""
    
    def __init__(self):
        self.executor = CodeExecutor()
    
    def validate_submission(self,
                          code: str,
                          language: str,
                          test_cases: List[Dict],
                          time_limit: int = 5000,
                          memory_limit: int = 256) -> Dict:
        """
        Validate code against all test cases
        """
        results = {
            'passed': 0,
            'failed': 0,
            'total': len(test_cases),
            'test_results': [],
            'overall_status': 'pending',
            'execution_time': 0,
            'memory_used': 0
        }
        
        total_execution_time = 0
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"Running test case {i + 1}/{len(test_cases)}")
            
            # Execute code with test input
            execution_result = self.executor.execute_code(
                code=code,
                language=language,
                test_input=test_case['input'],
                time_limit=time_limit,
                memory_limit=memory_limit
            )
            
            total_execution_time += execution_result['execution_time']
            
            # Check if execution was successful
            if not execution_result['success']:
                test_result = {
                    'test_case_id': test_case.get('id', i),
                    'passed': False,
                    'error': execution_result['error'],
                    'execution_time': execution_result['execution_time']
                }
                results['failed'] += 1
                results['test_results'].append(test_result)
                results['overall_status'] = 'error'
                break
            
            # Compare output
            actual_output = execution_result['output'].strip()
            expected_output = test_case['expected_output'].strip()
            passed = actual_output == expected_output
            
            test_result = {
                'test_case_id': test_case.get('id', i),
                'passed': passed,
                'actual_output': actual_output,
                'expected_output': expected_output,
                'execution_time': execution_result['execution_time']
            }
            
            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
                # Stop on first failure for efficiency
                results['test_results'].append(test_result)
                results['overall_status'] = 'failed'
                break
            
            results['test_results'].append(test_result)
        
        # Set final status
        if results['passed'] == results['total']:
            results['overall_status'] = 'passed'
        elif results['overall_status'] == 'pending':
            results['overall_status'] = 'failed'
        
        results['execution_time'] = total_execution_time
        
        return results
    
    def validate_syntax(self, code: str, language: str) -> Tuple[bool, Optional[str]]:
        """
        Validate syntax without executing
        """
        if language == 'python':
            try:
                compile(code, '<string>', 'exec')
                return True, None
            except SyntaxError as e:
                return False, f"Syntax error: {str(e)}"
        
        elif language == 'javascript':
            # Basic JavaScript syntax check using Node.js
            check_code = f"""
            try {{
                new Function({json.dumps(code)});
                console.log("Valid");
            }} catch (e) {{
                console.error("Syntax error:", e.message);
                process.exit(1);
            }}
            """
            
            try:
                result = subprocess.run(
                    ['node', '-e', check_code],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    return True, None
                else:
                    return False, result.stderr
                    
            except Exception as e:
                return False, f"Validation error: {str(e)}"
        
        return False, f"Unsupported language: {language}"