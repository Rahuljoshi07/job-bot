from config import Config
from resume_analyzer import ResumeAnalyzer
import os

def main():
    print("🚀 Job Bot Setup")
    print("=" * 50)
    
    config = Config()
    
    # Setup credentials
    print("Setting up your job application profile...")
    user_config = config.setup_user_credentials()
    
    # Setup resume
    print("\n📄 Resume Setup:")
    resume_path = input("Enter the full path to your resume (PDF/DOCX): ")
    
    if config.update_resume_path(resume_path):
        # Test resume analysis
        analyzer = ResumeAnalyzer()
        analysis = analyzer.analyze_resume()
        
        if analysis:
            print("\n✅ Resume analysis successful!")
            print(f"Found skills: {', '.join(analysis['skills'][:10])}")
        else:
            print("⚠️ Resume analysis failed, but file was copied successfully")
    
    print("\n🎉 Setup completed! You can now run the bot with:")
    print("python job-bot/job_bot_with_login.py")

if __name__ == "__main__":
    main()
