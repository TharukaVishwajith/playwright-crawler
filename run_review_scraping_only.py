#!/usr/bin/env python3
"""
Enhanced Product Data Scraping Script
This script runs ONLY Phase 2: extracting product specifications and customer reviews.
Now includes specification extraction from the product details slide panel.

Requirements:
- Phase 1 must be completed (laptop_products_all_pages.json file must exist)
- Virtual environment must be activated
- All dependencies must be installed

Usage:
    source .venv/bin/activate
    python run_review_scraping_only.py

Output:
    - data/laptop_products_with_specs_and_reviews.json (enhanced products with specifications and reviews)
    - Screenshots and logs for verification
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import BestBuyAutomation
import config


def validate_prerequisites():
    """Validate that all prerequisites are met before running."""
    print("🔍 Checking prerequisites...")
    
    # Check if input file exists
    input_file = config.DATA_DIR / "laptop_products_all_pages.json"
    if not input_file.exists():
        print("❌ ERROR: Required input file not found!")
        print(f"   Expected: {input_file}")
        print("   💡 Solution: Run Phase 1 first with: python main.py")
        return False
    
    print(f"✅ Input file found: {input_file}")
    
    # Check if data directory is writable
    try:
        config.DATA_DIR.mkdir(exist_ok=True)
        test_file = config.DATA_DIR / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Data directory is writable")
    except Exception as e:
        print(f"❌ ERROR: Cannot write to data directory: {e}")
        return False
    
    print("✅ All prerequisites met!")
    return True


async def run_enhanced_product_scraping():
    """Run the enhanced product data scraping (specifications + reviews)."""
    
    if not validate_prerequisites():
        return 1
    
    print("\n" + "="*70)
    print("🚀 STARTING ENHANCED PRODUCT DATA SCRAPING")
    print("📋 Features: Specifications + Customer Reviews + Pagination")
    print("="*70)
    
    automation = BestBuyAutomation()
    
    try:
        # Execute the enhanced scraping task
        result = await automation.run_review_scraping_task()
        
        print("\n" + "="*70)
        print("✅ ENHANCED PRODUCT DATA SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print(f"📊 RESULTS:")
        print(f"   Total products processed: {result.get('total_products_processed', 'N/A')}")
        print(f"   Products with specifications: {result.get('products_with_specs', 'N/A')}")
        print(f"   Products with reviews: {result.get('products_with_reviews', 'N/A')}")
        print(f"   Total specifications scraped: {result.get('total_specifications_scraped', 'N/A')}")
        print(f"   Total reviews scraped: {result.get('total_reviews_scraped', 'N/A')}")
        print(f"   Average specs per product: {result.get('average_specs_per_product', 'N/A')}")
        print(f"   Average reviews per product: {result.get('average_reviews_per_product', 'N/A')}")
        
        output_file = config.DATA_DIR / "laptop_products_with_specs_and_reviews.json"
        print(f"\n📁 OUTPUT:")
        print(f"   File: {output_file}")
        print(f"   Screenshots: {config.DATA_DIR}/*.png")
        print(f"   Logs: {config.LOGS_DIR}/automation.log")
        
        print(f"\n⏰ Completed at: {result.get('timestamp', 'N/A')}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ PROCESS INTERRUPTED BY USER")
        print("💡 Partial results may be available in the data directory")
        return 1
        
    except Exception as e:
        print(f"\n❌ ENHANCED PRODUCT DATA SCRAPING FAILED!")
        print(f"Error: {e}")
        print(f"\n🔍 TROUBLESHOOTING:")
        print(f"   1. Check logs: {config.LOGS_DIR}/automation.log")
        print(f"   2. Check screenshots in: {config.DATA_DIR}/")
        print(f"   3. Verify input file: {config.DATA_DIR}/laptop_products_all_pages.json")
        print(f"   4. Ensure virtual environment is activated")
        print(f"   5. Try test mode first: python test_review_scraping.py")
        return 1


def print_usage_info():
    """Print usage information and tips."""
    print("📖 ENHANCED PRODUCT DATA SCRAPING")
    print("="*50)
    print("This script extracts:")
    print("  🔧 Product specifications (from slide panel)")
    print("  💬 Customer reviews (all pages)")
    print("  📄 Handles review pagination automatically")
    print("  🇺🇸 Handles country selection")
    print("  📱 Smart page loading")
    print()
    print("📋 What happens:")
    print("  1. Loads products from Phase 1 results")
    print("  2. Visits each product page")
    print("  3. Clicks specifications button")
    print("  4. Extracts all specifications")
    print("  5. Finds and clicks 'See All Customer Reviews'")
    print("  6. Scrapes all review pages")
    print("  7. Saves enhanced JSON with specs + reviews")
    print()
    print("⏱️  Expected time: 20-30 minutes for ~115 products")
    print("📁 Output: laptop_products_with_specs_and_reviews.json")
    print()
    print("🔧 Prerequisites:")
    print("  ✅ Phase 1 completed (laptop_products_all_pages.json exists)")
    print("  ✅ Virtual environment activated")
    print("  ✅ Dependencies installed")


if __name__ == "__main__":
    print_usage_info()
    
    # Ask for user confirmation
    try:
        response = input("\n🚀 Ready to start enhanced product data scraping? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Operation cancelled by user")
            exit(0)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        exit(0)
    
    print("\n🔄 Starting enhanced product data scraping...")
    exit_code = asyncio.run(run_enhanced_product_scraping())
    exit(exit_code) 