"""
Crime Report Extractor - Main Processing Script

This script extracts structured information from crime report narratives:
- Crime type (from code lookup)
- Method of entry
- Suspect descriptions
- Vehicle information

Uses a hybrid approach: Regex for simple patterns + DeepSeek LLM for complex extraction
"""

import pandas as pd
import os
import sys
from datetime import datetime
from typing import Dict, Optional
import config
from extractors import extract_with_llm_safe, clean_suspect_description, format_license_plate


class CrimeReportExtractor:
    """Main class for processing crime reports"""

    def __init__(self, input_file: str = None, output_file: str = None, crime_codes_file: str = None):
        """
        Initialize the extractor

        Args:
            input_file: Path to input Excel file (default: input/crime_data.xlsx)
            output_file: Path to output Excel file (default: output/crime_data_extracted.xlsx)
            crime_codes_file: Path to crime codes CSV (default: input/crime_codes.csv)
        """
        self.input_file = input_file or os.path.join(config.INPUT_DIR, config.DEFAULT_INPUT_FILE)
        self.output_file = output_file or os.path.join(config.OUTPUT_DIR, config.DEFAULT_OUTPUT_FILE)
        self.crime_codes_file = crime_codes_file or os.path.join(config.INPUT_DIR, config.CRIME_CODES_FILE)

        self.df = None
        self.crime_lookup = {}
        self.stats = {
            'total_rows': 0,
            'successful': 0,
            'failed': 0,
            'method_extracted': 0,
            'suspects_found': 0,
            'vehicles_found': 0
        }

    def load_data(self):
        """Load input data and crime code lookup"""
        print(f"\n📂 Loading data from: {self.input_file}")

        try:
            # Load main data
            self.df = pd.read_excel(self.input_file)
            print(f"✅ Loaded {len(self.df)} crime reports")

            # Validate required columns
            required_cols = [config.INPUT_COLUMNS['crime_code'], config.INPUT_COLUMNS['narrative']]
            missing_cols = [col for col in required_cols if col not in self.df.columns]

            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}\nFound columns: {list(self.df.columns)}")

            # Load crime codes
            if os.path.exists(self.crime_codes_file):
                crime_codes_df = pd.read_csv(self.crime_codes_file)
                # Assume first column is code, second is description
                code_col = crime_codes_df.columns[0]
                desc_col = crime_codes_df.columns[1]
                self.crime_lookup = dict(zip(crime_codes_df[code_col], crime_codes_df[desc_col]))
                print(f"✅ Loaded {len(self.crime_lookup)} crime code mappings")
            else:
                print(f"⚠️  Crime codes file not found: {self.crime_codes_file}")
                print("   Will proceed without crime type mapping")

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            sys.exit(1)

    def initialize_output_columns(self):
        """Initialize all output columns in the dataframe"""
        # Map crime type
        crime_code_col = config.INPUT_COLUMNS['crime_code']
        self.df['crime_type'] = self.df[crime_code_col].map(self.crime_lookup)

        # Initialize extraction columns
        self.df['method_of_entry'] = None
        self.df['suspect_1'] = None
        self.df['suspect_2'] = None
        self.df['vehicle_make'] = None
        self.df['vehicle_model'] = None
        self.df['vehicle_color'] = None
        self.df['vehicle_plate'] = None

    def process_row(self, idx: int, row: pd.Series) -> bool:
        """
        Process a single row and extract information

        Args:
            idx: Row index
            row: Row data

        Returns:
            True if successful, False if failed
        """
        try:
            crime_code = str(row[config.INPUT_COLUMNS['crime_code']])
            narrative = str(row[config.INPUT_COLUMNS['narrative']])

            # Skip if narrative is empty
            if not narrative or narrative.lower() in ['nan', 'none', '']:
                return False

            # Extract using LLM (with fallback to regex)
            extracted = extract_with_llm_safe(narrative, crime_code)

            # Method of entry
            if extracted.get('method_of_entry'):
                self.df.at[idx, 'method_of_entry'] = extracted['method_of_entry']
                self.stats['method_extracted'] += 1

            # Suspects
            if extracted.get('suspects') and isinstance(extracted['suspects'], list):
                for i, suspect in enumerate(extracted['suspects'][:2]):  # Max 2 suspects
                    if isinstance(suspect, dict) and 'description' in suspect:
                        desc = clean_suspect_description(suspect['description'])
                        if desc:
                            col_name = f'suspect_{i+1}'
                            self.df.at[idx, col_name] = desc
                            if i == 0:  # Count only if at least one suspect found
                                self.stats['suspects_found'] += 1

            # Vehicles
            if extracted.get('vehicles') and isinstance(extracted['vehicles'], list):
                # Take first vehicle if multiple
                for vehicle in extracted['vehicles']:
                    if isinstance(vehicle, dict) and any(vehicle.values()):
                        self.df.at[idx, 'vehicle_make'] = vehicle.get('make')
                        self.df.at[idx, 'vehicle_model'] = vehicle.get('model')
                        self.df.at[idx, 'vehicle_color'] = vehicle.get('color')

                        plate = vehicle.get('plate')
                        if plate:
                            self.df.at[idx, 'vehicle_plate'] = format_license_plate(plate)

                        self.stats['vehicles_found'] += 1
                        break  # Only take first vehicle

            return True

        except Exception as e:
            print(f"\n❌ Error processing row {idx}: {e}")
            return False

    def process_all(self):
        """Process all crime reports"""
        print(f"\n🔄 Processing {len(self.df)} crime reports...")
        print("=" * 70)

        self.stats['total_rows'] = len(self.df)

        # Process each row with progress indicator
        for idx, row in self.df.iterrows():
            # Progress indicator every 10 rows
            if (idx + 1) % 10 == 0 or idx == 0:
                print(f"Progress: {idx + 1}/{len(self.df)} rows processed...", end='\r')

            success = self.process_row(idx, row)
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1

        print(f"\nProgress: {len(self.df)}/{len(self.df)} rows processed... ✅")
        print("=" * 70)

    def save_output(self):
        """Save processed data to Excel"""
        print(f"\n💾 Saving results to: {self.output_file}")

        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

            # Save to Excel
            self.df.to_excel(self.output_file, index=False, engine='openpyxl')
            print(f"✅ Successfully saved {len(self.df)} rows to {self.output_file}")

            # Also save as CSV for easier inspection
            csv_file = self.output_file.replace('.xlsx', '.csv')
            self.df.to_csv(csv_file, index=False)
            print(f"✅ Also saved as CSV: {csv_file}")

        except Exception as e:
            print(f"❌ Error saving output: {e}")
            sys.exit(1)

    def print_statistics(self):
        """Print extraction statistics and quality report"""
        print("\n" + "=" * 70)
        print("📊 EXTRACTION STATISTICS")
        print("=" * 70)

        print(f"\n📝 Processing Summary:")
        print(f"   Total rows processed:    {self.stats['total_rows']}")
        print(f"   Successful extractions:  {self.stats['successful']}")
        print(f"   Failed extractions:      {self.stats['failed']}")

        print(f"\n🔍 Extraction Details:")

        # Calculate percentages
        total = self.stats['total_rows']
        if total > 0:
            method_pct = (self.stats['method_extracted'] / total) * 100
            suspect_pct = (self.stats['suspects_found'] / total) * 100
            vehicle_pct = (self.stats['vehicles_found'] / total) * 100

            print(f"   Method of entry found:   {self.stats['method_extracted']} ({method_pct:.1f}%)")
            print(f"   Suspects identified:     {self.stats['suspects_found']} ({suspect_pct:.1f}%)")
            print(f"   Vehicles found:          {self.stats['vehicles_found']} ({vehicle_pct:.1f}%)")

        # Sample of extracted data
        print(f"\n📋 Sample Extractions (first 3 rows):")
        print("-" * 70)

        sample_cols = ['crime_code', 'crime_type', 'method_of_entry', 'suspect_1', 'vehicle_make', 'vehicle_color']
        available_cols = [col for col in sample_cols if col in self.df.columns]

        for idx, row in self.df.head(3).iterrows():
            print(f"\nRow {idx + 1}:")
            for col in available_cols:
                value = row[col]
                if pd.notna(value) and value:
                    print(f"   {col}: {value}")

        print("\n" + "=" * 70)

    def run(self):
        """Main execution method"""
        print("\n" + "=" * 70)
        print("🚔 CRIME REPORT EXTRACTOR")
        print("=" * 70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check API key
        if config.DEEPSEEK_API_KEY == 'your-api-key-here':
            print("\n⚠️  WARNING: DeepSeek API key not configured!")
            print("   Will use regex-only extraction (lower accuracy)")
            print("   To use LLM extraction, set DEEPSEEK_API_KEY environment variable")
            print("   or update config.py with your API key")

        # Execute pipeline
        self.load_data()
        self.initialize_output_columns()
        self.process_all()
        self.save_output()
        self.print_statistics()

        print(f"\n⏱️  End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("✨ Processing complete!")


def main():
    """Entry point for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract structured data from crime report narratives')
    parser.add_argument('-i', '--input', help='Input Excel file path', default=None)
    parser.add_argument('-o', '--output', help='Output Excel file path', default=None)
    parser.add_argument('-c', '--codes', help='Crime codes CSV file path', default=None)

    args = parser.parse_args()

    # Create and run extractor
    extractor = CrimeReportExtractor(
        input_file=args.input,
        output_file=args.output,
        crime_codes_file=args.codes
    )

    extractor.run()


if __name__ == '__main__':
    main()
