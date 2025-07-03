import sys
sys.path.append('.')

from resume_analyzer import ResumeAnalyzer

print("Testing resume analysis...")
analyzer = ResumeAnalyzer()
result = analyzer.analyze_resume()

if result:
    print("✅ Resume analysis successful!")
    print(f"Skills found: {result['skills']}")
    print(f"Contact info: {result['contact_info']}")
else:
    print("❌ Resume analysis failed")
