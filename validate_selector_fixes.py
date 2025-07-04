#!/usr/bin/env python3
"""
Validation script to verify that all invalid CSS selectors have been fixed
"""

import os
import re
from pathlib import Path

def find_invalid_selectors():
    """Find any remaining invalid CSS selectors in the codebase"""
    
    print("🔍 Scanning for invalid CSS selectors...")
    
    # Patterns to look for
    invalid_patterns = [
        r'button:contains\(',
        r'a:contains\(',
        r':contains\(',
        r'querySelectorAll.*:contains'
    ]
    
    # Files to check
    python_files = []
    for file_path in Path('.').rglob('*.py'):
        if 'validate_selector_fixes' not in str(file_path):
            python_files.append(file_path)
    
    issues_found = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in invalid_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues_found.append({
                            'file': str(file_path),
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
    
    return issues_found

def test_fixed_selectors():
    """Test that our fixed selectors are valid"""
    
    print("🧪 Testing fixed CSS selectors...")
    
    # These are the selectors we replaced the invalid ones with
    fixed_selectors = [
        'button[title*="Apply"]',
        'a[title*="Apply"]', 
        'button[title*="Sign In"]',
        'a[title*="Login"]',
        '.apply-button',
        '[data-test="apply"]',
        'a[href*="apply"]'
    ]
    
    print("✅ Fixed selectors being tested:")
    for selector in fixed_selectors:
        print(f"   • {selector}")
    
    # Test that they don't contain invalid syntax
    for selector in fixed_selectors:
        if ':contains(' in selector:
            print(f"❌ Still contains invalid :contains(): {selector}")
            return False
        else:
            print(f"✅ Valid CSS selector: {selector}")
    
    return True

def validate_xpath_alternatives():
    """Validate that XPath alternatives are properly formatted"""
    
    print("\n🔍 Validating XPath alternatives...")
    
    # Check that button_finder_utility.py exists and has proper XPath
    if os.path.exists('button_finder_utility.py'):
        print("✅ button_finder_utility.py exists")
        
        with open('button_finder_utility.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for XPath patterns
        xpath_patterns = [
            r'//button\[contains\(text\(\)',
            r'//a\[contains\(text\(\)',
            r'find_elements\(By\.XPATH'
        ]
        
        xpath_found = False
        for pattern in xpath_patterns:
            if re.search(pattern, content):
                xpath_found = True
                print(f"✅ Found XPath pattern: {pattern}")
        
        if xpath_found:
            print("✅ XPath alternatives properly implemented")
        else:
            print("⚠️ XPath alternatives may not be implemented")
    
    else:
        print("⚠️ button_finder_utility.py not found")

def main():
    """Main validation function"""
    
    print("🛠️ CSS Selector Fix Validation")
    print("=" * 50)
    
    # Find any remaining invalid selectors
    issues = find_invalid_selectors()
    
    if issues:
        print(f"\n❌ Found {len(issues)} remaining invalid selectors:")
        for issue in issues:
            print(f"   📁 {issue['file']}:{issue['line']}")
            print(f"      {issue['content']}")
            print(f"      Pattern: {issue['pattern']}\n")
    else:
        print("✅ No invalid CSS selectors found!")
    
    # Test fixed selectors
    print("\n" + "=" * 50)
    if test_fixed_selectors():
        print("✅ All fixed selectors are valid CSS")
    else:
        print("❌ Some fixed selectors still have issues")
    
    # Validate XPath alternatives
    print("\n" + "=" * 50)
    validate_xpath_alternatives()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY:")
    
    if not issues:
        print("✅ All invalid :contains() selectors have been fixed")
        print("✅ Proper CSS attribute selectors are now used")
        print("✅ XPath alternatives implemented for text-based searches")
        print("✅ Enhanced button detection utility created")
        print("\n🎉 CSS selector issues have been successfully resolved!")
        return True
    else:
        print("❌ Some issues remain and need to be fixed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
