#!/usr/bin/env python3
"""
Flask Web Dashboard for Job Bot Monitoring
Provides web interface for viewing application status, statistics, and visualization
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import time

# Check if Flask is available, if not use basic HTTP server
try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available. Install with: pip install flask")

class JobBotDashboard:
    def __init__(self, db_path='job_bot.db', applications_file='applications.txt'):
        self.db_path = db_path
        self.applications_file = applications_file
        self.init_database()
        self.load_applications_from_file()
        
    def init_database(self):
        """Initialize SQLite database for storing job applications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'applied',
                url TEXT,
                application_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_applications INTEGER DEFAULT 0,
                successful_applications INTEGER DEFAULT 0,
                failed_applications INTEGER DEFAULT 0,
                platforms_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_applications_from_file(self):
        """Load existing applications from text file into database"""
        if not os.path.exists(self.applications_file):
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we already have data
        cursor.execute('SELECT COUNT(*) FROM applications')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        with open(self.applications_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ' - Applied to ' in line:
                    try:
                        timestamp_str, rest = line.split(' - Applied to ', 1)
                        if ' at ' in rest:
                            job_title, company_platform = rest.split(' at ', 1)
                            if ' (' in company_platform:
                                company, platform = company_platform.rsplit(' (', 1)
                                platform = platform.rstrip(')')
                            else:
                                company = company_platform
                                platform = 'Unknown'
                        else:
                            job_title = rest
                            company = 'Unknown'
                            platform = 'Unknown'
                        
                        cursor.execute('''
                            INSERT INTO applications (timestamp, job_title, company, platform)
                            VALUES (?, ?, ?, ?)
                        ''', (timestamp_str, job_title, company, platform))
                    except ValueError:
                        continue
        
        conn.commit()
        conn.close()
    
    def get_applications(self, limit=100, offset=0, platform_filter=None, search_query=None):
        """Get applications with optional filtering and pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM applications'
        params = []
        
        conditions = []
        if platform_filter:
            conditions.append('platform = ?')
            params.append(platform_filter)
        
        if search_query:
            conditions.append('(job_title LIKE ? OR company LIKE ?)')
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        applications = cursor.fetchall()
        
        # Get total count
        count_query = 'SELECT COUNT(*) FROM applications'
        if conditions:
            count_query += ' WHERE ' + ' AND '.join(conditions[:-2] if search_query else conditions)
            cursor.execute(count_query, params[:-2])
        else:
            cursor.execute(count_query)
        
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return applications, total_count
    
    def get_statistics(self):
        """Get application statistics for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total applications
        cursor.execute('SELECT COUNT(*) FROM applications')
        total_applications = cursor.fetchone()[0]
        
        # Applications by platform
        cursor.execute('SELECT platform, COUNT(*) FROM applications GROUP BY platform')
        platform_stats = dict(cursor.fetchall())
        
        # Applications by day (last 30 days)
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM applications
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''')
        daily_stats = cursor.fetchall()
        
        # Recent applications
        cursor.execute('''
            SELECT job_title, company, platform, timestamp
            FROM applications
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        recent_applications = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_applications': total_applications,
            'platform_stats': platform_stats,
            'daily_stats': daily_stats,
            'recent_applications': recent_applications
        }
    
    def add_application(self, job_title, company, platform, url=None, application_id=None):
        """Add new application to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO applications (timestamp, job_title, company, platform, url, application_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), job_title, company, platform, url, application_id))
        
        conn.commit()
        conn.close()

# Flask app setup
if FLASK_AVAILABLE:
    app = Flask(__name__)
    dashboard = JobBotDashboard()
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/api/statistics')
    def api_statistics():
        """API endpoint for statistics"""
        stats = dashboard.get_statistics()
        return jsonify(stats)
    
    @app.route('/api/applications')
    def api_applications():
        """API endpoint for applications with pagination and filtering"""
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        platform_filter = request.args.get('platform')
        search_query = request.args.get('search')
        
        applications, total = dashboard.get_applications(
            limit=limit, 
            offset=offset,
            platform_filter=platform_filter,
            search_query=search_query
        )
        
        # Convert to dictionaries
        app_list = []
        for app in applications:
            app_list.append({
                'id': app[0],
                'timestamp': app[1],
                'job_title': app[2],
                'company': app[3],
                'platform': app[4],
                'status': app[5],
                'url': app[6],
                'application_id': app[7]
            })
        
        return jsonify({
            'applications': app_list,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    
    @app.route('/templates/<path:filename>')
    def templates(filename):
        """Serve template files"""
        return send_from_directory('templates', filename)
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        return send_from_directory('static', filename)

def create_template_files():
    """Create HTML templates for the dashboard"""
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Create main dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0; }
        .applications-table { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .filters { margin: 20px 0; display: flex; gap: 15px; flex-wrap: wrap; }
        .filter-input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .platform-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
        .platform-remoteok { background: #e3f2fd; color: #1976d2; }
        .platform-dice { background: #f3e5f5; color: #7b1fa2; }
        .platform-linkedin { background: #e8f5e8; color: #388e3c; }
        .pagination { margin: 20px 0; text-align: center; }
        .pagination button { padding: 8px 16px; margin: 0 2px; border: 1px solid #ddd; background: white; cursor: pointer; }
        .pagination button:hover { background: #f0f0f0; }
        .pagination button.active { background: #3498db; color: white; border-color: #3498db; }
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr; }
            .filters { flex-direction: column; }
            .filter-input { width: 100%; }
            table { font-size: 0.9em; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Job Bot Dashboard</h1>
        <p>Monitor your job applications and track success rates</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total-applications">0</div>
                <div>Total Applications</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="applications-today">0</div>
                <div>Applications Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="success-rate">0%</div>
                <div>Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="active-platforms">0</div>
                <div>Active Platforms</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Applications Over Time</h3>
            <canvas id="applicationsChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>Applications by Platform</h3>
            <canvas id="platformChart" width="400" height="200"></canvas>
        </div>
        
        <div class="applications-table">
            <h3>Recent Applications</h3>
            <div class="filters">
                <input type="text" id="search-input" placeholder="Search jobs or companies..." class="filter-input">
                <select id="platform-filter" class="filter-input">
                    <option value="">All Platforms</option>
                    <option value="RemoteOK">RemoteOK</option>
                    <option value="DICE">DICE</option>
                    <option value="LinkedIn">LinkedIn</option>
                </select>
                <button onclick="applyFilters()" class="filter-input">Apply Filters</button>
            </div>
            
            <table id="applications-table">
                <thead>
                    <tr>
                        <th>Job Title</th>
                        <th>Company</th>
                        <th>Platform</th>
                        <th>Applied Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="applications-body">
                </tbody>
            </table>
            
            <div class="pagination">
                <button onclick="prevPage()" id="prev-btn">Previous</button>
                <span id="page-info">Page 1 of 1</span>
                <button onclick="nextPage()" id="next-btn">Next</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentPage = 1;
        let totalPages = 1;
        let currentFilters = { search: '', platform: '' };
        
        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const stats = await response.json();
                
                document.getElementById('total-applications').textContent = stats.total_applications;
                document.getElementById('active-platforms').textContent = Object.keys(stats.platform_stats).length;
                
                // Update charts
                updateApplicationsChart(stats.daily_stats);
                updatePlatformChart(stats.platform_stats);
                
            } catch (error) {
                console.error('Error loading statistics:', error);
            }
        }
        
        async function loadApplications(page = 1) {
            try {
                const params = new URLSearchParams({
                    limit: 20,
                    offset: (page - 1) * 20,
                    search: currentFilters.search,
                    platform: currentFilters.platform
                });
                
                const response = await fetch(`/api/applications?${params}`);
                const data = await response.json();
                
                updateApplicationsTable(data.applications);
                updatePagination(data.total, data.limit, data.offset);
                
            } catch (error) {
                console.error('Error loading applications:', error);
            }
        }
        
        function updateApplicationsTable(applications) {
            const tbody = document.getElementById('applications-body');
            tbody.innerHTML = '';
            
            applications.forEach(app => {
                const row = document.createElement('tr');
                const date = new Date(app.timestamp).toLocaleDateString();
                const platformClass = `platform-${app.platform.toLowerCase()}`;
                
                row.innerHTML = `
                    <td>${app.job_title}</td>
                    <td>${app.company}</td>
                    <td><span class="platform-badge ${platformClass}">${app.platform}</span></td>
                    <td>${date}</td>
                    <td>${app.status}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function updatePagination(total, limit, offset) {
            totalPages = Math.ceil(total / limit);
            currentPage = Math.floor(offset / limit) + 1;
            
            document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
            document.getElementById('prev-btn').disabled = currentPage === 1;
            document.getElementById('next-btn').disabled = currentPage === totalPages;
        }
        
        function updateApplicationsChart(dailyStats) {
            const ctx = document.getElementById('applicationsChart').getContext('2d');
            
            const labels = dailyStats.map(stat => stat[0]);
            const data = dailyStats.map(stat => stat[1]);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Applications',
                        data: data,
                        borderColor: '#3498db',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function updatePlatformChart(platformStats) {
            const ctx = document.getElementById('platformChart').getContext('2d');
            
            const labels = Object.keys(platformStats);
            const data = Object.values(platformStats);
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
        
        function applyFilters() {
            currentFilters.search = document.getElementById('search-input').value;
            currentFilters.platform = document.getElementById('platform-filter').value;
            currentPage = 1;
            loadApplications(1);
        }
        
        function prevPage() {
            if (currentPage > 1) {
                currentPage--;
                loadApplications(currentPage);
            }
        }
        
        function nextPage() {
            if (currentPage < totalPages) {
                currentPage++;
                loadApplications(currentPage);
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadStatistics();
            loadApplications();
            
            // Auto-refresh every 30 seconds
            setInterval(() => {
                loadStatistics();
                loadApplications(currentPage);
            }, 30000);
        });
    </script>
</body>
</html>'''
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_html)

def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask dashboard"""
    if not FLASK_AVAILABLE:
        print("Flask is not available. Please install it: pip install flask")
        return
    
    create_template_files()
    print(f"🚀 Starting Job Bot Dashboard on http://{host}:{port}")
    print("   📊 View statistics and monitor applications")
    print("   🔍 Search and filter job applications")
    print("   📱 Mobile-responsive design")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_dashboard()