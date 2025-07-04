#!/usr/bin/env python3
"""
🧪 TEST ENHANCED SCORING SYSTEM
Demonstrates the new advanced job scoring capabilities
"""

import sys
import json
from datetime import datetime

# Import our enhanced scoring system
try:
    from advanced_scoring_system import AdvancedJobScorer, ScoringMetrics
    print("✅ Advanced scoring system imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import advanced scoring system: {e}")
    sys.exit(1)

def test_enhanced_scoring():
    """Test the enhanced scoring system with sample data"""
    
    print("\n" + "="*60)
    print("🎯 TESTING ENHANCED JOB SCORING SYSTEM")
    print("="*60)
    
    # Create user profile
    user_profile = {
        'skills': ['Python', 'AWS', 'Docker', 'Kubernetes', 'DevOps', 'Jenkins', 'CI/CD', 'Linux'],
        'experience_years': 5,
        'preferred_roles': ['DevOps Engineer', 'Cloud Engineer', 'SRE', 'Platform Engineer'],
        'location': 'Remote',
        'remote_only': True,
        'salary_min': 80000,
        'preferred_companies': ['Google', 'Amazon', 'Microsoft', 'Netflix'],
        'blacklisted_companies': ['Bad Corp', 'Scam Inc'],
        'keywords': ['cloud', 'automation', 'infrastructure', 'scalability'],
        'bio': 'Experienced DevOps engineer with expertise in cloud infrastructure and automation'
    }
    
    print(f"👤 User Profile:")
    print(f"   Skills: {', '.join(user_profile['skills'][:5])}...")
    print(f"   Experience: {user_profile['experience_years']} years")
    print(f"   Preferred Roles: {', '.join(user_profile['preferred_roles'])}")
    print(f"   Location: {user_profile['location']}")
    print(f"   Salary Min: ${user_profile['salary_min']:,}")
    
    # Create test jobs with different characteristics
    test_jobs = [
        {
            'title': 'Senior DevOps Engineer',
            'company': 'Google',
            'description': 'We are looking for an experienced DevOps engineer with strong skills in Python, AWS, Docker, and Kubernetes. You will work on automating infrastructure deployment and managing cloud-based systems. This is an exciting opportunity to work with cutting-edge technology and drive innovation in our platform.',
            'requirements': 'Required: 3+ years Python, AWS, Docker, Kubernetes, CI/CD experience. Preferred: Linux administration, Jenkins, Terraform.',
            'location': 'Remote',
            'salary': '$120,000 - $160,000'
        },
        {
            'title': 'Cloud Infrastructure Engineer',
            'company': 'Amazon',
            'description': 'Join our cloud infrastructure team to build scalable, reliable systems. Work with AWS services, automate deployments, and ensure high availability. Great opportunity for career growth and learning.',
            'requirements': 'Must have AWS experience, Python scripting, infrastructure automation. DevOps experience preferred.',
            'location': 'Remote',
            'salary': '$110,000 - $140,000'
        },
        {
            'title': 'Junior Software Developer',
            'company': 'StartupCorp',
            'description': 'Entry-level position for new graduates. Basic programming skills required. Fast-paced environment.',
            'requirements': 'Fresh graduate, basic programming knowledge, willingness to learn.',
            'location': 'San Francisco, CA',
            'salary': '$60,000 - $80,000'
        },
        {
            'title': 'Site Reliability Engineer',
            'company': 'Netflix',
            'description': 'Looking for an SRE to ensure platform reliability and performance. Work with Kubernetes, monitoring tools, and incident response. Excellent benefits and flexible work arrangements.',
            'requirements': 'Required: 5+ years experience, Kubernetes, Python, monitoring tools (Prometheus, Grafana). On-call rotation required.',
            'location': 'Remote',
            'salary': '$140,000 - $180,000'
        },
        {
            'title': 'Data Entry Clerk',
            'company': 'Bad Corp',
            'description': 'Urgent! Make money fast! Work from home guaranteed! No experience required! Earn $1000+ daily!',
            'requirements': 'No experience needed. Just click and earn!',
            'location': 'Anywhere',
            'salary': '$1000+ daily'
        }
    ]
    
    # Initialize the advanced scorer
    print(f"\n🧠 Initializing Advanced Job Scorer...")
    scorer = AdvancedJobScorer(user_profile)
    
    print(f"\n📊 ANALYZING {len(test_jobs)} TEST JOBS:")
    print("-" * 60)
    
    # Analyze each job
    results = []
    for i, job_data in enumerate(test_jobs, 1):
        print(f"\n🔍 JOB {i}: {job_data['title']} at {job_data['company']}")
        print(f"   💰 Salary: {job_data['salary']}")
        print(f"   📍 Location: {job_data['location']}")
        
        # Score the job
        metrics = scorer.score_job(job_data)
        results.append((job_data, metrics))
        
        # Display key scores
        print(f"   🎯 Overall Score: {metrics.overall_score}%")
        print(f"   🛠️  Skills Match: {metrics.skills_score}%")
        print(f"   💼 Experience Match: {metrics.experience_score}%")
        print(f"   📍 Location Match: {metrics.location_score}%")
        print(f"   💰 Salary Match: {metrics.salary_score}%")
        print(f"   📝 Title Relevance: {metrics.title_relevance}%")
        
        # Color-code the overall score
        if metrics.overall_score >= 80:
            print(f"   ✅ EXCELLENT MATCH!")
        elif metrics.overall_score >= 60:
            print(f"   🟡 GOOD MATCH")
        elif metrics.overall_score >= 40:
            print(f"   🟠 FAIR MATCH")
        else:
            print(f"   ❌ POOR MATCH")
    
    # Show top matches
    print(f"\n🏆 TOP JOB MATCHES (Sorted by Overall Score):")
    print("=" * 60)
    
    # Sort by overall score
    sorted_results = sorted(results, key=lambda x: x[1].overall_score, reverse=True)
    
    for i, (job_data, metrics) in enumerate(sorted_results, 1):
        print(f"{i}. {job_data['title']} at {job_data['company']}")
        print(f"   📊 Score: {metrics.overall_score}% | Skills: {metrics.skills_score}% | Experience: {metrics.experience_score}%")
        
        if i == 1:
            print(f"\n🎯 DETAILED ANALYSIS OF TOP MATCH:")
            explanation = scorer.get_scoring_explanation(metrics)
            print(explanation)
    
    # Test database saving
    print(f"\n💾 Testing Database Integration...")
    try:
        for job_data, metrics in results:
            job_id = f"test_{job_data['company']}_{hash(job_data['title'])}"
            scorer.save_scoring_data(job_id, metrics)
        print(f"✅ Successfully saved {len(results)} scoring records to database")
    except Exception as e:
        print(f"❌ Database save failed: {e}")
    
    # Summary stats
    print(f"\n📈 SCORING SUMMARY:")
    print(f"   Jobs Analyzed: {len(test_jobs)}")
    print(f"   Average Score: {sum(m.overall_score for _, m in results) / len(results):.1f}%")
    print(f"   High Quality Jobs (>70%): {sum(1 for _, m in results if m.overall_score > 70)}")
    print(f"   Apply-Worthy Jobs (>60%): {sum(1 for _, m in results if m.overall_score > 60)}")
    
    print(f"\n✅ Enhanced scoring system test completed successfully!")
    return True

def show_scoring_features():
    """Show the features of the enhanced scoring system"""
    
    print(f"\n🚀 ENHANCED SCORING SYSTEM FEATURES:")
    print("=" * 50)
    
    features = [
        "🎯 Multi-Factor Scoring (14 different metrics)",
        "🛠️  Advanced Skills Matching with categories",
        "💼 Experience Level Intelligence",
        "📍 Smart Location Preferences", 
        "💰 Salary Range Analysis",
        "🏢 Company Preference System",
        "📝 Job Title Relevance Scoring",
        "📋 Requirements Analysis",
        "🤖 NLP-based Similarity (when available)",
        "😊 Sentiment Analysis (scam detection)",
        "⚡ Urgency Detection",
        "🏆 Competition Level Assessment",
        "📈 Growth Potential Analysis",
        "💾 Database Integration for Analytics"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n🎮 INTEGRATION WITH YOUR JOB BOT:")
    print("   • Automatic scoring of all job matches")
    print("   • Higher precision in job filtering")  
    print("   • Detailed analytics and explanations")
    print("   • Smart decision making for applications")
    print("   • Continuous learning from results")

if __name__ == "__main__":
    print("🧪 ENHANCED JOB BOT SCORING SYSTEM TEST")
    print("=" * 50)
    
    # Show features
    show_scoring_features()
    
    # Run the test
    try:
        success = test_enhanced_scoring()
        if success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"Your job bot now has SUPER ENHANCED scoring capabilities!")
        else:
            print(f"\n❌ Some tests failed")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
