#!/usr/bin/env python3
"""
Quick Demo - Test extraction on a few sample rows
This will test both the LLM and regex extraction methods
"""

import pandas as pd
from extractors import extract_with_llm_safe
from datetime import datetime

def run_quick_demo():
    """Run a quick test on 3 sample narratives"""

    print("\n" + "=" * 70)
    print("🧪 CRIME REPORT EXTRACTOR - QUICK DEMO")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test cases
    test_cases = [
        {
            'code': '220',
            'narrative': 'Residential burglary at 1456 Elm Street. Unknown suspects broke rear window to gain entry between 0800-1700 hours. Missing: laptop ($1,200), jewelry ($800), cash ($300). No witnesses.'
        },
        {
            'code': '510',
            'narrative': '2019 Honda Civic (silver) stolen from 789 Oak Ave parking lot. Last seen 2200 hours 10/15. Plate: ABC1234. Vehicle locked, keys not inside.'
        },
        {
            'code': '220',
            'narrative': 'S1 (male, 6ft, black hoodie) pried front door, stole electronics. S2 (female, 5\'5", blonde) was lookout. Fled in red Toyota Camry northbound on Main St.'
        }
    ]

    print("Testing extraction on 3 sample narratives...\n")

    for i, test in enumerate(test_cases, 1):
        print("─" * 70)
        print(f"Test Case {i}:")
        print("─" * 70)
        print(f"Crime Code: {test['code']}")
        print(f"Narrative: {test['narrative']}\n")

        # Extract using LLM
        print("🔄 Extracting information...")
        try:
            result = extract_with_llm_safe(test['narrative'], test['code'])

            print("✅ Extraction successful!\n")

            # Display results
            print("📍 Method of Entry:")
            print(f"   {result.get('method_of_entry', 'Not found')}\n")

            if result.get('suspects'):
                print("👤 Suspects:")
                for j, suspect in enumerate(result['suspects'], 1):
                    desc = suspect.get('description', 'No description')
                    print(f"   S{j}: {desc}")
                print()
            else:
                print("👤 Suspects: None found\n")

            if result.get('vehicles') and any(result['vehicles'][0].values()):
                vehicle = result['vehicles'][0]
                print("🚗 Vehicle:")
                for key, value in vehicle.items():
                    if value:
                        print(f"   {key.capitalize()}: {value}")
                print()
            else:
                print("🚗 Vehicle: None found\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")

        if i < len(test_cases):
            print()  # Space between test cases

    print("=" * 70)
    print("✨ Demo complete!")
    print("\nNext steps:")
    print("  1. Run full extraction: python main.py")
    print("  2. Check output in: output/crime_data_extracted.xlsx")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    run_quick_demo()
