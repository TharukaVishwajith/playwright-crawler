#!/usr/bin/env python3
"""
Best Buy Review Scraping - Phase 2 Only

This script ONLY runs the review scraping phase. It requires that Phase 1 
(product listing scraping) has already been completed and the file 
'data/laptop_products_all_pages.json' exists.

Usage:
    source .venv/bin/activate
    python run_review_scraping_only.py

Output:
    - data/laptop_products_with_reviews.json (enhanced products with reviews)
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


def check_prerequisites():
    """Check if Phase 1 output file exists."""
    input_file = config.DATA_DIR / "laptop_products_all_pages.json"
    
    if not input_file.exists():
        print("❌ ERROR: Required input file not found!")
        print(f"   Missing: {input_file}")
        print("\n📋 Prerequisites:")
        print("   1. Phase 1 (product listing scraping) must be completed first")
        print("   2. File 'data/laptop_products_all_pages.json' must exist")
        print("\n🔧 To complete Phase 1, run:")
        print("   python main.py")
        print("\n❓ Or if you want to test with sample data:")
        print("   python test_review_scraping.py")
        return False
    
    return True


async def main():
    """Main entry point for Phase 2 only - Review Scraping."""
    
    print("=" * 60)
    print("🔍 BEST BUY REVIEW SCRAPING - PHASE 2 ONLY")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    automation = BestBuyAutomation()
    
    try:
        # Show what we're about to do
        input_file = config.DATA_DIR / "laptop_products_all_pages.json"
        output_file = config.DATA_DIR / "laptop_products_with_reviews.json"
        
        print(f"📁 Input:  {input_file}")
        print(f"📁 Output: {output_file}")
        print("\n🚀 Starting review scraping for all products...")
        print("⏱️  This may take 20-30 minutes depending on the number of products")
        print("🔄 Each product page will be visited to scrape customer reviews")
        print("\nPress Ctrl+C to cancel if needed.\n")
        
        # Run the review scraping task
        result = await automation.run_review_scraping_task()
        
        # Display results
        print("\n" + "=" * 60)
        print("✅ PHASE 2 COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Total products processed: {result.get('total_products_processed', 'N/A')}")
        print(f"📝 Products with reviews found: {result.get('products_with_reviews', 'N/A')}")
        print(f"💬 Total reviews scraped: {result.get('total_reviews_scraped', 'N/A')}")
        print(f"📈 Average reviews per product: {result.get('average_reviews_per_product', 'N/A')}")
        print(f"📁 Output saved to: {output_file}")
        print(f"🕐 Completed at: {result.get('timestamp', 'N/A')}")
        
        # Show next steps
        print("\n🎉 Review scraping completed!")
        print(f"📄 Check the output file: {output_file}")
        print("📸 Screenshots saved in the data/ directory for verification")
        print("📋 Logs available in logs/automation.log")
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        print("🔄 You can resume by running this script again")
        return 1
    except Exception as e:
        print(f"\n❌ Review scraping failed: {e}")
        print("📋 Check logs/automation.log for detailed error information")
        return 1
        
    return 0


if __name__ == "__main__":
    # Show usage information
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print(__doc__)
        sys.exit(0)
    
    # Run the review scraping
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 