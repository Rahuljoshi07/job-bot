#!/usr/bin/env python3
"""
📊 ENHANCED JOB BOT ANALYTICS DASHBOARD
Advanced analytics and reporting for job application data
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
from datetime_utils import format_report_timestamp, get_current_datetime, get_current_user

class JobBotAnalytics:
    """Advanced analytics for job bot performance"""
    
    def __init__(self, db_path="job_bot.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to database"""
        if os.path.exists(self.db_path):
            self.conn = sqlite3.connect(self.db_path)
            return True
        return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_basic_stats(self):
        """Get basic application statistics"""
        if not self.connect():
            return None
        
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        stats['total_applications'] = cursor.fetchone()[0]
        
        # Applications by platform
        cursor.execute("""
            SELECT platform, COUNT(*) 
            FROM applications 
            GROUP BY platform 
            ORDER BY COUNT(*) DESC
        """)
        stats['by_platform'] = dict(cursor.fetchall())
        
        # Average relevance score
        cursor.execute("SELECT AVG(relevance_score) FROM applications WHERE relevance_score > 0")
        result = cursor.fetchone()[0]
        stats['avg_relevance_score'] = result if result else 0
        
        # Applications by date (last 30 days)
        cursor.execute("""
            SELECT DATE(applied_date) as date, COUNT(*) 
            FROM applications 
            WHERE applied_date >= datetime('now', '-30 days')
            GROUP BY DATE(applied_date)
            ORDER BY date DESC
        """)
        stats['daily_applications'] = dict(cursor.fetchall())
        
        # Response rate
        cursor.execute("SELECT COUNT(*) FROM applications WHERE response_received = 1")
        responses = cursor.fetchone()[0]
        stats['response_rate'] = (responses / max(1, stats['total_applications'])) * 100
        
        # Top companies applied to
        cursor.execute("""
            SELECT company, COUNT(*) 
            FROM applications 
            GROUP BY company 
            ORDER BY COUNT(*) DESC 
            LIMIT 10
        """)
        stats['top_companies'] = dict(cursor.fetchall())
        
        self.close()
        return stats
    
    def get_performance_trends(self, days=30):
        """Get performance trends over time"""
        if not self.connect():
            return None
        
        cursor = self.conn.cursor()
        
        # Daily application count and average score
        cursor.execute("""
            SELECT 
                DATE(applied_date) as date,
                COUNT(*) as applications,
                AVG(relevance_score) as avg_score
            FROM applications 
            WHERE applied_date >= datetime('now', '-{} days')
            GROUP BY DATE(applied_date)
            ORDER BY date
        """.format(days))
        
        trends = cursor.fetchall()
        self.close()
        
        return trends
    
    def get_platform_analysis(self):
        """Analyze performance by platform"""
        if not self.connect():
            return None
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                platform,
                COUNT(*) as total_apps,
                AVG(relevance_score) as avg_score,
                COUNT(CASE WHEN response_received = 1 THEN 1 END) as responses,
                MAX(applied_date) as last_application
            FROM applications 
            GROUP BY platform
            ORDER BY total_apps DESC
        """)
        
        analysis = cursor.fetchall()
        self.close()
        
        return analysis
    
    def get_success_insights(self):
        """Get insights into successful applications"""
        if not self.connect():
            return None
        
        cursor = self.conn.cursor()
        
        insights = {}
        
        # High-scoring applications that got responses
        cursor.execute("""
            SELECT title, company, platform, relevance_score, applied_date
            FROM applications 
            WHERE response_received = 1 AND relevance_score > 80
            ORDER BY relevance_score DESC
        """)
        insights['successful_high_score'] = cursor.fetchall()
        
        # Companies that responded
        cursor.execute("""
            SELECT company, COUNT(*) as responses, AVG(relevance_score) as avg_score
            FROM applications 
            WHERE response_received = 1
            GROUP BY company
            ORDER BY responses DESC
        """)
        insights['responsive_companies'] = cursor.fetchall()
        
        # Best performing job titles
        cursor.execute("""
            SELECT 
                title,
                COUNT(*) as total_apps,
                COUNT(CASE WHEN response_received = 1 THEN 1 END) as responses,
                AVG(relevance_score) as avg_score
            FROM applications 
            GROUP BY title
            HAVING total_apps >= 2
            ORDER BY responses DESC, avg_score DESC
        """)
        insights['best_job_titles'] = cursor.fetchall()
        
        self.close()
        return insights
    
    def generate_report(self):
        """Generate comprehensive analytics report"""
        print("📊 JOB BOT ANALYTICS REPORT")
        print("=" * 50)
        print(format_report_timestamp())
        print()
        
        # Basic stats
        stats = self.get_basic_stats()
        if not stats:
            print("❌ No data available. Run the bot first!")
            return
        
        print("📈 BASIC STATISTICS")
        print("-" * 30)
        print(f"Total Applications: {stats['total_applications']}")
        print(f"Average Relevance Score: {stats['avg_relevance_score']:.1f}%")
        print(f"Response Rate: {stats['response_rate']:.1f}%")
        print()
        
        print("🌐 APPLICATIONS BY PLATFORM")
        print("-" * 30)
        for platform, count in stats['by_platform'].items():
            percentage = (count / stats['total_applications']) * 100
            print(f"{platform:15} {count:3d} ({percentage:5.1f}%)")
        print()
        
        print("🏢 TOP COMPANIES")
        print("-" * 30)
        for company, count in list(stats['top_companies'].items())[:10]:
            print(f"{company:25} {count:3d} applications")
        print()
        
        # Platform analysis
        platform_data = self.get_platform_analysis()
        if platform_data:
            print("📊 PLATFORM PERFORMANCE")
            print("-" * 30)
            print(f"{'Platform':<15} {'Apps':<5} {'Avg Score':<10} {'Responses':<10} {'Response %':<10}")
            print("-" * 60)
            for row in platform_data:
                platform, apps, avg_score, responses, last_app = row
                response_rate = (responses / apps) * 100 if apps > 0 else 0
                print(f"{platform:<15} {apps:<5} {avg_score:<10.1f} {responses:<10} {response_rate:<10.1f}")
            print()
        
        # Success insights
        insights = self.get_success_insights()
        if insights:
            print("🎯 SUCCESS INSIGHTS")
            print("-" * 30)
            
            if insights['successful_high_score']:
                print("High-scoring applications that got responses:")
                for title, company, platform, score, date in insights['successful_high_score']:
                    print(f"  • {title} at {company} ({platform}) - {score:.1f}% - {date}")
                print()
            
            if insights['responsive_companies']:
                print("Most responsive companies:")
                for company, responses, avg_score in insights['responsive_companies'][:5]:
                    print(f"  • {company}: {responses} responses (avg score: {avg_score:.1f}%)")
                print()
        
        # Recent activity
        if stats['daily_applications']:
            print("📅 RECENT ACTIVITY (Last 10 days)")
            print("-" * 30)
            recent_days = list(stats['daily_applications'].items())[:10]
            for date, count in recent_days:
                print(f"{date}: {count} applications")
            print()
        
        print("✅ Report generation completed!")
    
    def export_data(self, format='csv'):
        """Export application data"""
        if not self.connect():
            print("❌ No database found!")
            return
        
        try:
            if format.lower() == 'csv':
                if not PANDAS_AVAILABLE:
                    print("❌ pandas not available. Install with: pip install pandas")
                    return
                
                # Export to CSV
                df = pd.read_sql_query("""
                    SELECT 
                        title, company, platform, url, applied_date, 
                        status, relevance_score, response_received
                    FROM applications 
                    ORDER BY applied_date DESC
                """, self.conn)
                
                filename = f"job_applications_{get_current_datetime().replace(' ', '_').replace(':', '')}.csv"
                df.to_csv(filename, index=False)
                print(f"✅ Data exported to {filename}")
                
            elif format.lower() == 'json':
                # Export to JSON
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM applications ORDER BY applied_date DESC
                """)
                
                columns = [desc[0] for desc in cursor.description]
                data = []
                for row in cursor.fetchall():
                    data.append(dict(zip(columns, row)))
                
                filename = f"job_applications_{get_current_datetime().replace(' ', '_').replace(':', '')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"✅ Data exported to {filename}")
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
        finally:
            self.close()
    
    def create_visualizations(self):
        """Create visualization charts"""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️ Matplotlib not available. Install with: pip install matplotlib")
            return
            
        try:
            stats = self.get_basic_stats()
            if not stats:
                print("❌ No data for visualization!")
                return
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Job Bot Analytics Dashboard', fontsize=16)
            
            # 1. Applications by platform (pie chart)
            if stats['by_platform']:
                platforms = list(stats['by_platform'].keys())
                counts = list(stats['by_platform'].values())
                ax1.pie(counts, labels=platforms, autopct='%1.1f%%')
                ax1.set_title('Applications by Platform')
            
            # 2. Daily applications (line chart)
            if stats['daily_applications']:
                dates = list(stats['daily_applications'].keys())
                counts = list(stats['daily_applications'].values())
                ax2.plot(dates[-14:], counts[-14:], marker='o')  # Last 14 days
                ax2.set_title('Daily Applications (Last 14 Days)')
                ax2.tick_params(axis='x', rotation=45)
            
            # 3. Top companies (bar chart)
            if stats['top_companies']:
                companies = list(stats['top_companies'].keys())[:8]
                counts = list(stats['top_companies'].values())[:8]
                ax3.bar(companies, counts)
                ax3.set_title('Top Companies Applied To')
                ax3.tick_params(axis='x', rotation=45)
            
            # 4. Performance metrics (bar chart)
            metrics = ['Total Apps', 'Avg Score', 'Response Rate']
            values = [stats['total_applications'], stats['avg_relevance_score'], stats['response_rate']]
            ax4.bar(metrics, values)
            ax4.set_title('Key Performance Metrics')
            
            plt.tight_layout()
            
            # Save chart
            filename = f"job_bot_analytics_{get_current_datetime().replace(' ', '_').replace(':', '')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Visualization saved to {filename}")
            
            # Show chart if not in headless mode
            if os.getenv('DISPLAY'):
                plt.show()
            
        except Exception as e:
            print(f"❌ Visualization failed: {e}")

def main():
    """Main function"""
    print("📊 JOB BOT ANALYTICS DASHBOARD")
    print("=" * 40)
    
    analytics = JobBotAnalytics()
    
    while True:
        print("\n🎛️ Choose option:")
        print("1. View Analytics Report")
        print("2. Export Data (CSV)")
        print("3. Export Data (JSON)")
        print("4. Create Visualizations")
        print("5. Exit")
        
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                analytics.generate_report()
            elif choice == '2':
                analytics.export_data('csv')
            elif choice == '3':
                analytics.export_data('json')
            elif choice == '4':
                analytics.create_visualizations()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
