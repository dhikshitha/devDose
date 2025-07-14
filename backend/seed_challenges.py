#!/usr/bin/env python
from app import create_app, db
from models import Challenge, TestCase, Category
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_challenges():
    """Seed coding challenges"""
    
    challenges_data = [
        # Easy Challenges
        {
            'title': 'Hello World',
            'description': 'Your first programming challenge - print a greeting message',
            'difficulty': 'easy',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that returns the string "Hello, World!".

This is a classic first program that helps you understand basic syntax and output.''',
            'initial_code': '''def hello_world():
    # Write your code here
    pass''',
            'solution_code': '''def hello_world():
    return "Hello, World!"''',
            'hints': [
                'Use the return statement to send back a value',
                'The string should be exactly "Hello, World!" with proper capitalization'
            ],
            'points': 10,
            'test_cases': [
                {
                    'input_data': '',
                    'expected_output': 'Hello, World!',
                    'is_hidden': False,
                    'description': 'Basic test'
                }
            ]
        },
        {
            'title': 'Sum of Two Numbers',
            'description': 'Calculate the sum of two integers',
            'difficulty': 'easy',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that takes two integers as input and returns their sum.

Input: Two integers separated by a space
Output: The sum of the two integers''',
            'initial_code': '''def sum_two_numbers():
    # Read input and calculate sum
    pass''',
            'solution_code': '''def sum_two_numbers():
    a, b = map(int, input().split())
    print(a + b)''',
            'hints': [
                'Use input() to read the input',
                'Use split() to separate the two numbers',
                'Convert strings to integers using int()'
            ],
            'points': 10,
            'test_cases': [
                {
                    'input_data': '5 3',
                    'expected_output': '8',
                    'is_hidden': False,
                    'description': 'Positive numbers'
                },
                {
                    'input_data': '-10 20',
                    'expected_output': '10',
                    'is_hidden': False,
                    'description': 'Mixed positive and negative'
                },
                {
                    'input_data': '0 0',
                    'expected_output': '0',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Even or Odd',
            'description': 'Determine if a number is even or odd',
            'difficulty': 'easy',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that determines whether a given integer is even or odd.

Input: A single integer
Output: "Even" if the number is even, "Odd" if the number is odd''',
            'initial_code': '''def even_or_odd():
    # Read number and determine if even or odd
    pass''',
            'solution_code': '''def even_or_odd():
    n = int(input())
    if n % 2 == 0:
        print("Even")
    else:
        print("Odd")''',
            'hints': [
                'Use the modulo operator (%) to check divisibility',
                'A number is even if it\'s divisible by 2'
            ],
            'points': 10,
            'test_cases': [
                {
                    'input_data': '4',
                    'expected_output': 'Even',
                    'is_hidden': False,
                    'description': 'Even number'
                },
                {
                    'input_data': '7',
                    'expected_output': 'Odd',
                    'is_hidden': False,
                    'description': 'Odd number'
                },
                {
                    'input_data': '0',
                    'expected_output': 'Even',
                    'is_hidden': True
                },
                {
                    'input_data': '-5',
                    'expected_output': 'Odd',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Reverse a String',
            'description': 'Reverse the characters in a string',
            'difficulty': 'easy',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that reverses a given string.

Input: A string
Output: The reversed string''',
            'initial_code': '''def reverse_string():
    # Read and reverse the string
    pass''',
            'solution_code': '''def reverse_string():
    s = input()
    print(s[::-1])''',
            'hints': [
                'Python has a simple slicing syntax for reversing',
                'You can also use a loop to build the reversed string'
            ],
            'points': 15,
            'test_cases': [
                {
                    'input_data': 'hello',
                    'expected_output': 'olleh',
                    'is_hidden': False,
                    'description': 'Simple word'
                },
                {
                    'input_data': 'Python',
                    'expected_output': 'nohtyP',
                    'is_hidden': False,
                    'description': 'With capital letter'
                },
                {
                    'input_data': 'a',
                    'expected_output': 'a',
                    'is_hidden': True
                },
                {
                    'input_data': '12345',
                    'expected_output': '54321',
                    'is_hidden': True
                }
            ]
        },
        
        # Medium Challenges
        {
            'title': 'Fibonacci Sequence',
            'description': 'Generate the nth Fibonacci number',
            'difficulty': 'medium',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that returns the nth number in the Fibonacci sequence.

The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the previous two.

Input: A positive integer n (1 <= n <= 40)
Output: The nth Fibonacci number

Example: The first few Fibonacci numbers are: 0, 1, 1, 2, 3, 5, 8, 13, 21...''',
            'initial_code': '''def fibonacci():
    # Read n and calculate nth Fibonacci number
    pass''',
            'solution_code': '''def fibonacci():
    n = int(input())
    if n <= 0:
        print(0)
    elif n == 1:
        print(0)
    elif n == 2:
        print(1)
    else:
        a, b = 0, 1
        for i in range(2, n):
            a, b = b, a + b
        print(b)''',
            'hints': [
                'Start with the base cases: F(1) = 0, F(2) = 1',
                'Use two variables to keep track of the last two numbers',
                'You can solve this iteratively or recursively'
            ],
            'points': 20,
            'test_cases': [
                {
                    'input_data': '1',
                    'expected_output': '0',
                    'is_hidden': False,
                    'description': 'First Fibonacci number'
                },
                {
                    'input_data': '6',
                    'expected_output': '5',
                    'is_hidden': False,
                    'description': '6th Fibonacci number'
                },
                {
                    'input_data': '10',
                    'expected_output': '34',
                    'is_hidden': True
                },
                {
                    'input_data': '15',
                    'expected_output': '377',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Palindrome Check',
            'description': 'Check if a string is a palindrome',
            'difficulty': 'medium',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that checks whether a given string is a palindrome.

A palindrome reads the same forwards and backwards. For this problem, ignore case and consider only alphanumeric characters.

Input: A string
Output: "Yes" if palindrome, "No" otherwise''',
            'initial_code': '''def is_palindrome():
    # Check if the string is a palindrome
    pass''',
            'solution_code': '''def is_palindrome():
    s = input()
    # Keep only alphanumeric and convert to lowercase
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    if cleaned == cleaned[::-1]:
        print("Yes")
    else:
        print("No")''',
            'hints': [
                'Clean the string by removing non-alphanumeric characters',
                'Convert to the same case for comparison',
                'Compare the string with its reverse'
            ],
            'points': 25,
            'test_cases': [
                {
                    'input_data': 'racecar',
                    'expected_output': 'Yes',
                    'is_hidden': False,
                    'description': 'Simple palindrome'
                },
                {
                    'input_data': 'A man a plan a canal Panama',
                    'expected_output': 'Yes',
                    'is_hidden': False,
                    'description': 'Palindrome with spaces'
                },
                {
                    'input_data': 'hello',
                    'expected_output': 'No',
                    'is_hidden': False,
                    'description': 'Not a palindrome'
                },
                {
                    'input_data': 'Was it a car or a cat I saw?',
                    'expected_output': 'Yes',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Prime Number Check',
            'description': 'Determine if a number is prime',
            'difficulty': 'medium',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that determines whether a given positive integer is a prime number.

A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.

Input: A positive integer n (1 <= n <= 10000)
Output: "Prime" if the number is prime, "Not Prime" otherwise''',
            'initial_code': '''def is_prime():
    # Check if the number is prime
    pass''',
            'solution_code': '''def is_prime():
    n = int(input())
    if n <= 1:
        print("Not Prime")
        return
    if n == 2:
        print("Prime")
        return
    if n % 2 == 0:
        print("Not Prime")
        return
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            print("Not Prime")
            return
    
    print("Prime")''',
            'hints': [
                'Numbers less than 2 are not prime',
                'Check divisibility only up to the square root of n',
                'After checking 2, you only need to check odd divisors'
            ],
            'points': 25,
            'test_cases': [
                {
                    'input_data': '7',
                    'expected_output': 'Prime',
                    'is_hidden': False,
                    'description': 'Small prime'
                },
                {
                    'input_data': '12',
                    'expected_output': 'Not Prime',
                    'is_hidden': False,
                    'description': 'Composite number'
                },
                {
                    'input_data': '1',
                    'expected_output': 'Not Prime',
                    'is_hidden': True
                },
                {
                    'input_data': '97',
                    'expected_output': 'Prime',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Array Sum',
            'description': 'Calculate the sum of all elements in an array',
            'difficulty': 'easy',
            'category': 'Data Structures',
            'problem_statement': '''Write a function that calculates the sum of all elements in an array.

Input: 
- First line: An integer n (array size)
- Second line: n space-separated integers

Output: The sum of all array elements''',
            'initial_code': '''def array_sum():
    # Calculate sum of array elements
    pass''',
            'solution_code': '''def array_sum():
    n = int(input())
    arr = list(map(int, input().split()))
    print(sum(arr))''',
            'hints': [
                'Read the array size first',
                'Use map() to convert strings to integers',
                'Python has a built-in sum() function'
            ],
            'points': 15,
            'test_cases': [
                {
                    'input_data': '5\n1 2 3 4 5',
                    'expected_output': '15',
                    'is_hidden': False,
                    'description': 'Simple array'
                },
                {
                    'input_data': '3\n-1 0 1',
                    'expected_output': '0',
                    'is_hidden': False,
                    'description': 'With negative numbers'
                },
                {
                    'input_data': '1\n42',
                    'expected_output': '42',
                    'is_hidden': True
                }
            ]
        },
        
        # Hard Challenges
        {
            'title': 'Two Sum',
            'description': 'Find two numbers that add up to a target sum',
            'difficulty': 'hard',
            'category': 'Data Structures',
            'problem_statement': '''Given an array of integers and a target sum, find two numbers in the array that add up to the target.

Input:
- First line: Two integers n (array size) and target
- Second line: n space-separated integers

Output: Two space-separated indices (0-based) of the numbers that add up to target, or "Not Found" if no such pair exists.
If multiple pairs exist, return the one with the smallest first index.''',
            'initial_code': '''def two_sum():
    # Find two numbers that sum to target
    pass''',
            'solution_code': '''def two_sum():
    n, target = map(int, input().split())
    nums = list(map(int, input().split()))
    
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            print(f"{seen[complement]} {i}")
            return
        seen[num] = i
    
    print("Not Found")''',
            'hints': [
                'Use a hash map to store seen numbers',
                'For each number, check if target - number exists',
                'This can be solved in O(n) time'
            ],
            'points': 35,
            'test_cases': [
                {
                    'input_data': '4 9\n2 7 11 15',
                    'expected_output': '0 1',
                    'is_hidden': False,
                    'description': 'Basic case'
                },
                {
                    'input_data': '3 6\n3 2 4',
                    'expected_output': '1 2',
                    'is_hidden': False,
                    'description': 'Different order'
                },
                {
                    'input_data': '2 5\n1 2',
                    'expected_output': 'Not Found',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Valid Parentheses',
            'description': 'Check if parentheses are balanced',
            'difficulty': 'hard',
            'category': 'Data Structures',
            'problem_statement': '''Given a string containing only parentheses '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.

Input: A string containing only bracket characters
Output: "Valid" if the parentheses are balanced, "Invalid" otherwise''',
            'initial_code': '''def valid_parentheses():
    # Check if parentheses are valid
    pass''',
            'solution_code': '''def valid_parentheses():
    s = input()
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                print("Invalid")
                return
        else:
            stack.append(char)
    
    if stack:
        print("Invalid")
    else:
        print("Valid")''',
            'hints': [
                'Use a stack data structure',
                'Push opening brackets onto the stack',
                'When you see a closing bracket, check if it matches the top of the stack'
            ],
            'points': 40,
            'test_cases': [
                {
                    'input_data': '()',
                    'expected_output': 'Valid',
                    'is_hidden': False,
                    'description': 'Simple valid case'
                },
                {
                    'input_data': '()[]{}',
                    'expected_output': 'Valid',
                    'is_hidden': False,
                    'description': 'Multiple types'
                },
                {
                    'input_data': '(]',
                    'expected_output': 'Invalid',
                    'is_hidden': False,
                    'description': 'Mismatched brackets'
                },
                {
                    'input_data': '([)]',
                    'expected_output': 'Invalid',
                    'is_hidden': True
                },
                {
                    'input_data': '{[]}',
                    'expected_output': 'Valid',
                    'is_hidden': True
                }
            ]
        },
        
        # More Easy Challenges
        {
            'title': 'Find Maximum',
            'description': 'Find the maximum element in an array',
            'difficulty': 'easy',
            'category': 'Data Structures',
            'problem_statement': '''Write a function that finds the maximum element in an array.

Input:
- First line: An integer n (array size)
- Second line: n space-separated integers

Output: The maximum element in the array''',
            'initial_code': '''def find_maximum():
    # Find the maximum element
    pass''',
            'solution_code': '''def find_maximum():
    n = int(input())
    arr = list(map(int, input().split()))
    print(max(arr))''',
            'hints': [
                'Python has a built-in max() function',
                'You can also iterate through the array keeping track of the maximum'
            ],
            'points': 10,
            'test_cases': [
                {
                    'input_data': '5\n3 7 2 9 1',
                    'expected_output': '9',
                    'is_hidden': False
                },
                {
                    'input_data': '3\n-5 -2 -8',
                    'expected_output': '-2',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Count Vowels',
            'description': 'Count the number of vowels in a string',
            'difficulty': 'easy',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function that counts the number of vowels (a, e, i, o, u) in a string.
Count both uppercase and lowercase vowels.

Input: A string
Output: The number of vowels''',
            'initial_code': '''def count_vowels():
    # Count vowels in the string
    pass''',
            'solution_code': '''def count_vowels():
    s = input()
    vowels = 'aeiouAEIOU'
    count = sum(1 for char in s if char in vowels)
    print(count)''',
            'hints': [
                'Create a string containing all vowels',
                'Check each character to see if it\'s a vowel'
            ],
            'points': 10,
            'test_cases': [
                {
                    'input_data': 'hello world',
                    'expected_output': '3',
                    'is_hidden': False
                },
                {
                    'input_data': 'PYTHON',
                    'expected_output': '1',
                    'is_hidden': True
                }
            ]
        },
        
        # More Medium Challenges
        {
            'title': 'Remove Duplicates',
            'description': 'Remove duplicate elements from an array',
            'difficulty': 'medium',
            'category': 'Data Structures',
            'problem_statement': '''Write a function that removes duplicate elements from an array while preserving the order of first occurrence.

Input:
- First line: An integer n (array size)
- Second line: n space-separated integers

Output: Space-separated unique elements in order of first appearance''',
            'initial_code': '''def remove_duplicates():
    # Remove duplicates while preserving order
    pass''',
            'solution_code': '''def remove_duplicates():
    n = int(input())
    arr = list(map(int, input().split()))
    seen = set()
    result = []
    for num in arr:
        if num not in seen:
            seen.add(num)
            result.append(num)
    print(' '.join(map(str, result)))''',
            'hints': [
                'Use a set to track seen elements',
                'Maintain a separate list for the result'
            ],
            'points': 20,
            'test_cases': [
                {
                    'input_data': '7\n1 2 3 2 4 3 5',
                    'expected_output': '1 2 3 4 5',
                    'is_hidden': False
                },
                {
                    'input_data': '5\n5 5 5 5 5',
                    'expected_output': '5',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Binary Search',
            'description': 'Implement binary search on a sorted array',
            'difficulty': 'medium',
            'category': 'Data Structures',
            'problem_statement': '''Implement binary search to find an element in a sorted array.

Input:
- First line: Two integers n (array size) and target
- Second line: n space-separated sorted integers

Output: The index (0-based) of the target element, or -1 if not found''',
            'initial_code': '''def binary_search():
    # Implement binary search
    pass''',
            'solution_code': '''def binary_search():
    n, target = map(int, input().split())
    arr = list(map(int, input().split()))
    
    left, right = 0, n - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            print(mid)
            return
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    print(-1)''',
            'hints': [
                'Start with left and right pointers',
                'Calculate the middle index',
                'Adjust the search range based on comparison'
            ],
            'points': 25,
            'test_cases': [
                {
                    'input_data': '5 7\n1 3 5 7 9',
                    'expected_output': '3',
                    'is_hidden': False
                },
                {
                    'input_data': '6 4\n1 2 3 5 6 7',
                    'expected_output': '-1',
                    'is_hidden': True
                }
            ]
        },
        
        # More Hard Challenges
        {
            'title': 'Longest Common Prefix',
            'description': 'Find the longest common prefix among strings',
            'difficulty': 'hard',
            'category': 'Programming Languages',
            'problem_statement': '''Write a function to find the longest common prefix string amongst an array of strings.
If there is no common prefix, output an empty string.

Input:
- First line: An integer n (number of strings)
- Next n lines: One string per line

Output: The longest common prefix, or "None" if there is no common prefix''',
            'initial_code': '''def longest_common_prefix():
    # Find longest common prefix
    pass''',
            'solution_code': '''def longest_common_prefix():
    n = int(input())
    if n == 0:
        print("None")
        return
    
    strings = []
    for _ in range(n):
        strings.append(input())
    
    if not strings[0]:
        print("None")
        return
    
    for i in range(len(strings[0])):
        char = strings[0][i]
        for s in strings[1:]:
            if i >= len(s) or s[i] != char:
                result = strings[0][:i]
                print(result if result else "None")
                return
    
    print(strings[0])''',
            'hints': [
                'Compare characters at each position across all strings',
                'Stop when you find a mismatch',
                'The prefix can\'t be longer than the shortest string'
            ],
            'points': 35,
            'test_cases': [
                {
                    'input_data': '3\nflower\nflow\nflight',
                    'expected_output': 'fl',
                    'is_hidden': False
                },
                {
                    'input_data': '3\ndog\nracecar\ncar',
                    'expected_output': 'None',
                    'is_hidden': True
                }
            ]
        },
        {
            'title': 'Merge Sorted Arrays',
            'description': 'Merge two sorted arrays into one sorted array',
            'difficulty': 'hard',
            'category': 'Data Structures',
            'problem_statement': '''Given two sorted arrays, merge them into a single sorted array.

Input:
- First line: Two integers m and n (sizes of the two arrays)
- Second line: m space-separated integers (first sorted array)
- Third line: n space-separated integers (second sorted array)

Output: Space-separated integers representing the merged sorted array''',
            'initial_code': '''def merge_sorted_arrays():
    # Merge two sorted arrays
    pass''',
            'solution_code': '''def merge_sorted_arrays():
    m, n = map(int, input().split())
    arr1 = list(map(int, input().split())) if m > 0 else []
    arr2 = list(map(int, input().split())) if n > 0 else []
    
    result = []
    i, j = 0, 0
    
    while i < m and j < n:
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1
    
    while i < m:
        result.append(arr1[i])
        i += 1
    
    while j < n:
        result.append(arr2[j])
        j += 1
    
    print(' '.join(map(str, result)))''',
            'hints': [
                'Use two pointers, one for each array',
                'Compare elements and add the smaller one to result',
                'Don\'t forget to add remaining elements'
            ],
            'points': 30,
            'test_cases': [
                {
                    'input_data': '3 3\n1 3 5\n2 4 6',
                    'expected_output': '1 2 3 4 5 6',
                    'is_hidden': False
                },
                {
                    'input_data': '2 3\n1 2\n3 4 5',
                    'expected_output': '1 2 3 4 5',
                    'is_hidden': True
                }
            ]
        }
    ]
    
    app = create_app()
    with app.app_context():
        # Get categories
        categories = {cat.name: cat for cat in Category.query.all()}
        
        if not categories:
            logger.error("No categories found. Please run seed_data.py first.")
            return
        
        challenges_created = 0
        
        for challenge_data in challenges_data:
            # Check if challenge already exists
            existing = Challenge.query.filter_by(title=challenge_data['title']).first()
            if existing:
                logger.info(f"Challenge '{challenge_data['title']}' already exists, skipping...")
                continue
            
            # Extract test cases
            test_cases_data = challenge_data.pop('test_cases', [])
            category_name = challenge_data.pop('category')
            
            # Create challenge
            challenge = Challenge(**challenge_data)
            challenge.category = categories.get(category_name, categories.get('Programming Languages'))
            db.session.add(challenge)
            db.session.flush()  # Get the challenge ID
            
            # Create test cases
            for i, test_case_data in enumerate(test_cases_data):
                test_case_data['order_index'] = i
                test_case = TestCase(challenge_id=challenge.id, **test_case_data)
                db.session.add(test_case)
            
            challenges_created += 1
            logger.info(f"Created challenge: {challenge.title}")
        
        db.session.commit()
        logger.info(f"Successfully created {challenges_created} challenges")


if __name__ == "__main__":
    seed_challenges()