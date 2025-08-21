"""
Marketing Campaign Report Export Automation
Author: Sahil Hansa
Email: sahilhansa007@gmail.com
Description: Automated report generation and export for marketing campaign data
Location: Jammu, J&K, India
"""

import pandas as pd
import os
from datetime import datetime

class ReportExporter:
    """
    Automated report exporter for marketing campaign project
    """
    def __init__(self, data_folder='data/processed/', output_folder='reports/'):
        self.data_folder = data_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def load_data(self, filename):
        try:
            path = f"{self.data_folder}{filename}"
            data = pd.read_csv(path)
            print(f"Loaded {len(data)} records from {filename}")
            return data
        except Exception as e:
            print(f"Failed to load {filename}: {str(e)}")
            return None

    def export_summary(self):
        campaign_data = self.load_data('campaign_data_latest.csv')
        kpi_data = self.load_data('kpi_metrics_latest.csv')

        if campaign_data is None or kpi_data is None:
            print("Required data not found for report export.")
            return False

        # Generate summary report combining campaign and KPI data
        summary = pd.merge(campaign_data, kpi_data,
                           on='campaign_id', how='inner')

        # Select key columns for report
        report_columns = [
            'campaign_id', 'campaign_name', 'start_date', 'end_date',
            'channel', 'status', 'roi_percentage', 'cost_per_lead',
            'cost_per_acquisition', 'conversion_rate', 'click_through_rate'
        ]
        report = summary[report_columns]

        # Export report to CSV and Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(self.output_folder, f'report_{timestamp}.csv')
        excel_path = os.path.join(self.output_folder, f'report_{timestamp}.xlsx')

        report.to_csv(csv_path, index=False)
        report.to_excel(excel_path, index=False)

        print(f"Report exported to:\n - {csv_path}\n - {excel_path}")
        return True

def main():
    print("=== Marketing Campaign Report Exporter ===")
    exporter = ReportExporter()
    exporter.export_summary()
    print("=== Export Complete ===")

if __name__ == "__main__":
    main()
