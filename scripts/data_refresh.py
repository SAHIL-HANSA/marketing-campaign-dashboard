"""
Marketing Campaign Data Refresh Automation
Author: Sahil Hansa
Email: sahilhansa007@gmail.com
Description: Automated data refresh script for Power BI Marketing Campaign Dashboard
Location: Jammu, J&K, India
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import schedule
import time
import os
import json
from sqlalchemy import create_engine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_refresh.log'),
        logging.StreamHandler()
    ]
)

class MarketingDataRefresh:
    """
    Marketing Campaign Data Refresh and Automation Class
    
    Handles automated data refresh for Power BI dashboard
    
    Author: Sahil Hansa
    Contact: sahilhansa007@gmail.com
    """
    
    def __init__(self, config_file='config/database_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.engine = None
        self.refresh_status = {}
        
    def load_config(self):
        """Load database and email configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logging.info("Configuration loaded successfully")
                return config
        except FileNotFoundError:
            logging.error(f"Configuration file {self.config_file} not found")
            # Return default configuration
            return self.get_default_config()
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Provide default configuration template"""
        return {
            "database": {
                "host": "localhost",
                "port": 3306,
                "username": "marketing_user",
                "password": "password",
                "database": "marketing_db"
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "sahilhansa007@gmail.com",
                "password": "app_password",
                "recipients": ["marketing@company.com", "manager@company.com"]
            },
            "refresh_schedule": {
                "hourly_during_campaigns": True,
                "daily_summary": "08:00",
                "weekly_report": "Monday 09:00"
            }
        }
    
    def connect_database(self):
        """Establish database connection"""
        try:
            db_config = self.config['database']
            connection_string = f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            self.engine = create_engine(connection_string)
            logging.info("Database connection established successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to database: {str(e)}")
            return False
    
    def refresh_campaign_data(self):
        """Refresh campaign performance data"""
        try:
            if not self.connect_database():
                return False
            
            logging.info("Starting campaign data refresh...")
            
            # Extract latest campaign data
            query = """
            SELECT 
                campaign_id,
                campaign_name,
                campaign_type,
                channel,
                start_date,
                end_date,
                budget_allocated,
                total_spend,
                impressions,
                clicks,
                leads_generated,
                conversions,
                revenue_generated,
                status
            FROM marketing_campaigns 
            WHERE start_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            ORDER BY start_date DESC
            """
            
            campaign_data = pd.read_sql(query, self.engine)
            
            # Save to processed data folder
            output_path = 'data/processed/campaign_data_latest.csv'
            os.makedirs('data/processed', exist_ok=True)
            campaign_data.to_csv(output_path, index=False)
            
            logging.info(f"Campaign data refreshed successfully: {len(campaign_data)} records")
            self.refresh_status['campaign_data'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'records': len(campaign_data)
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Error refreshing campaign data: {str(e)}")
            self.refresh_status['campaign_data'] = {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def refresh_budget_data(self):
        """Refresh budget allocation and spending data"""
        try:
            if not self.engine:
                if not self.connect_database():
                    return False
            
            logging.info("Starting budget data refresh...")
            
            # Extract budget data
            query = """
            SELECT 
                budget_id,
                campaign_id,
                channel,
                budget_category,
                allocated_amount,
                spent_amount,
                remaining_amount,
                quarter,
                month,
                year,
                cost_center
            FROM budget_allocation 
            WHERE year >= YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
            ORDER BY year DESC, quarter DESC, month DESC
            """
            
            budget_data = pd.read_sql(query, self.engine)
            
            # Save refreshed data
            output_path = 'data/processed/budget_data_latest.csv'
            budget_data.to_csv(output_path, index=False)
            
            logging.info(f"Budget data refreshed successfully: {len(budget_data)} records")
            self.refresh_status['budget_data'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'records': len(budget_data)
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Error refreshing budget data: {str(e)}")
            self.refresh_status['budget_data'] = {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def calculate_kpis(self):
        """Calculate and refresh KPI metrics"""
        try:
            logging.info("Calculating KPI metrics...")
            
            # Load refreshed campaign data
            campaign_data = pd.read_csv('data/processed/campaign_data_latest.csv')
            
            # Calculate KPIs
            kpi_data = []
            
            for _, row in campaign_data.iterrows():
                # Calculate ROI
                roi = ((row['revenue_generated'] - row['total_spend']) / row['total_spend'] * 100) if row['total_spend'] > 0 else 0
                
                # Calculate Cost Per Lead
                cpl = row['total_spend'] / row['leads_generated'] if row['leads_generated'] > 0 else 0
                
                # Calculate Cost Per Acquisition
                cpa = row['total_spend'] / row['conversions'] if row['conversions'] > 0 else 0
                
                # Calculate Conversion Rate
                conversion_rate = (row['conversions'] / row['leads_generated'] * 100) if row['leads_generated'] > 0 else 0
                
                # Calculate CTR
                ctr = (row['clicks'] / row['impressions'] * 100) if row['impressions'] > 0 else 0
                
                kpi_data.append({
                    'campaign_id': row['campaign_id'],
                    'campaign_name': row['campaign_name'],
                    'channel': row['channel'],
                    'roi_percentage': round(roi, 2),
                    'cost_per_lead': round(cpl, 2),
                    'cost_per_acquisition': round(cpa, 2),
                    'conversion_rate': round(conversion_rate, 2),
                    'click_through_rate': round(ctr, 4),
                    'total_investment': row['total_spend'],
                    'total_revenue': row['revenue_generated'],
                    'net_profit': row['revenue_generated'] - row['total_spend'],
                    'profitability_score': min(10, max(0, roi / 30)),  # Scale 0-10
                    'last_updated': datetime.now().isoformat()
                })
            
            # Save KPI data
            kpi_df = pd.DataFrame(kpi_data)
            output_path = 'data/processed/kpi_metrics_latest.csv'
            kpi_df.to_csv(output_path, index=False)
            
            logging.info(f"KPI metrics calculated successfully: {len(kpi_data)} campaigns")
            self.refresh_status['kpi_calculation'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'campaigns_processed': len(kpi_data)
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Error calculating KPIs: {str(e)}")
            self.refresh_status['kpi_calculation'] = {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def generate_alerts(self):
        """Generate performance alerts for underperforming campaigns"""
        try:
            logging.info("Generating performance alerts...")
            
            # Load KPI data
            kpi_data = pd.read_csv('data/processed/kpi_metrics_latest.csv')
            
            alerts = []
            
            # Check for campaigns with negative ROI
            negative_roi = kpi_data[kpi_data['roi_percentage'] < 0]
            for _, campaign in negative_roi.iterrows():
                alerts.append({
                    'type': 'Critical',
                    'campaign_id': campaign['campaign_id'],
                    'campaign_name': campaign['campaign_name'],
                    'channel': campaign['channel'],
                    'issue': 'Negative ROI',
                    'current_roi': f"{campaign['roi_percentage']:.2f}%",
                    'recommended_action': 'Pause campaign and review targeting',
                    'priority': 'High'
                })
            
            # Check for campaigns with high cost per lead
            high_cpl = kpi_data[kpi_data['cost_per_lead'] > 100]
            for _, campaign in high_cpl.iterrows():
                alerts.append({
                    'type': 'Warning',
                    'campaign_id': campaign['campaign_id'],
                    'campaign_name': campaign['campaign_name'],
                    'channel': campaign['channel'],
                    'issue': 'High Cost Per Lead',
                    'current_cpl': f"${campaign['cost_per_lead']:.2f}",
                    'recommended_action': 'Optimize targeting or reduce bid',
                    'priority': 'Medium'
                })
            
            # Check for campaigns with low conversion rates
            low_conversion = kpi_data[kpi_data['conversion_rate'] < 5]
            for _, campaign in low_conversion.iterrows():
                alerts.append({
                    'type': 'Warning',
                    'campaign_id': campaign['campaign_id'],
                    'campaign_name': campaign['campaign_name'],
                    'channel': campaign['channel'],
                    'issue': 'Low Conversion Rate',
                    'current_conversion': f"{campaign['conversion_rate']:.2f}%",
                    'recommended_action': 'Review landing page and offer',
                    'priority': 'Medium'
                })
            
            # Save alerts
            if alerts:
                alerts_df = pd.DataFrame(alerts)
                output_path = 'data/processed/performance_alerts.csv'
                alerts_df.to_csv(output_path, index=False)
                
                logging.info(f"Generated {len(alerts)} performance alerts")
                self.send_alert_email(alerts)
            else:
                logging.info("No performance alerts generated - all campaigns performing well")
            
            self.refresh_status['alerts'] = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'alerts_count': len(alerts)
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Error generating alerts: {str(e)}")
            self.refresh_status['alerts'] = {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            return False
    
    def send_alert_email(self, alerts):
        """Send email alerts for critical issues"""
        try:
            if not alerts:
                return True
                
            email_config = self.config['email']
            
            # Create email content
            subject = f"Marketing Campaign Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            html_content = f"""
            <html>
                <body>
                    <h2>Marketing Campaign Performance Alerts</h2>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Total Alerts: {len(alerts)}</p>
                    
                    <table border="1" style="border-collapse: collapse;">
                        <tr style="background-color: #f2f2f2;">
                            <th>Priority</th>
                            <th>Campaign</th>
                            <th>Channel</th>
                            <th>Issue</th>
                            <th>Action Required</th>
                        </tr>
            """
            
            for alert in alerts:
                priority_color = "#ff4444" if alert['priority'] == 'High' else "#ffaa00"
                html_content += f"""
                        <tr>
                            <td style="background-color: {priority_color}; color: white; font-weight: bold;">{alert['priority']}</td>
                            <td>{alert['campaign_name']}</td>
                            <td>{alert['channel']}</td>
                            <td>{alert['issue']}</td>
                            <td>{alert['recommended_action']}</td>
                        </tr>
                """
            
            html_content += """
                    </table>
                    <br>
                    <p>Please review and take appropriate actions for the flagged campaigns.</p>
                    <p>Best regards,<br>Marketing Analytics Team</p>
                </body>
            </html>
            """
            
            # Send email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logging.info("Alert email sent successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error sending alert email: {str(e)}")
            return False
    
    def full_refresh(self):
        """Execute complete data refresh workflow"""
        logging.info("=== Starting Full Data Refresh ===")
        logging.info(f"Author: Sahil Hansa")
        logging.info(f"Email: sahilhansa007@gmail.com")
        logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        success_count = 0
        
        # Step 1: Refresh campaign data
        if self.refresh_campaign_data():
            success_count += 1
        
        # Step 2: Refresh budget data  
        if self.refresh_budget_data():
            success_count += 1
        
        # Step 3: Calculate KPIs
        if self.calculate_kpis():
            success_count += 1
            
        # Step 4: Generate alerts
        if self.generate_alerts():
            success_count += 1
        
        # Save refresh status
        self.save_refresh_status()
        
        logging.info(f"=== Data Refresh Complete: {success_count}/4 steps successful ===")
        
        return success_count == 4
    
    def save_refresh_status(self):
        """Save refresh status to file"""
        try:
            os.makedirs('logs', exist_ok=True)
            status_file = f"logs/refresh_status_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(status_file, 'w') as f:
                json.dump(self.refresh_status, f, indent=2)
                
            logging.info(f"Refresh status saved to {status_file}")
            
        except Exception as e:
            logging.error(f"Error saving refresh status: {str(e)}")
    
    def schedule_refresh_jobs(self):
        """Set up automated refresh schedule"""
        logging.info("Setting up automated refresh schedule...")
        
        config = self.config['refresh_schedule']
        
        # Hourly refresh during active campaigns (business hours)
        if config.get('hourly_during_campaigns', False):
            for hour in range(9, 18):  # 9 AM to 5 PM
                schedule.every().day.at(f"{hour:02d}:00").do(self.full_refresh)
        
        # Daily summary refresh
        daily_time = config.get('daily_summary', '08:00')
        schedule.every().day.at(daily_time).do(self.full_refresh)
        
        # Weekly comprehensive refresh
        schedule.every().monday.at("09:00").do(self.full_refresh)
        
        logging.info("Refresh schedule configured successfully")
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """
    Main execution function for data refresh automation
    
    Author: Sahil Hansa
    Contact: sahilhansa007@gmail.com
    """
    print("=== Marketing Campaign Data Refresh ===")
    print("Author: Sahil Hansa")
    print("Email: sahilhansa007@gmail.com")
    print("GitHub: https://github.com/SAHIL-HANSA")
    print("Location: Jammu, J&K, India")
    print("=" * 45)
    
    # Initialize refresh system
    refresh_system = MarketingDataRefresh()
    
    # Check command line arguments for immediate refresh
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--immediate':
        print("Running immediate data refresh...")
        success = refresh_system.full_refresh()
        if success:
            print("✅ Data refresh completed successfully")
        else:
            print("❌ Data refresh completed with errors - check logs")
    else:
        print("Starting scheduled refresh service...")
        print("Press Ctrl+C to stop the service")
        try:
            refresh_system.schedule_refresh_jobs()
        except KeyboardInterrupt:
            print("\n🛑 Refresh service stopped by user")
        except Exception as e:
            print(f"❌ Error in refresh service: {str(e)}")

if __name__ == "__main__":
    main()