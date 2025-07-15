#!/usr/bin/env python3
import os
import re

def update_datetime_info():
    # Using your updated timestamp
    datetime_string = "2025-07-15 20:10:58"
    username = "Rahuljoshi07"
    
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        
        for file in files:
            if file.endswith((".py", ".md", ".txt")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update date patterns
                    date_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
                    updated_content = re.sub(date_pattern, datetime_string, content)
                    
                    # Update username patterns
                    username_patterns = [
                        r'Current User\'s Login: [A-Za-z0-9]+',
                        r'User: [A-Za-z0-9]+',
                        r'username = "[A-Za-z0-9]+"',
                        r"username = '[A-Za-z0-9]+'"
                    ]
                    
                    for pattern in username_patterns:
                        updated_content = re.sub(pattern, f'Current User\'s Login: {username}', updated_content)
                    
                    if content != updated_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        print(f"Updated: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    update_datetime_info()
