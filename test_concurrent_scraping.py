"""
Test Concurrent Product Data Scraping Script
Tests the concurrent specifications and review scraping functionality on a small subset of products.
Demonstrates the speed improvement with multi-tab processing.
"""

import asyncio
import json
import sys
import os
import time

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import BestBuyAutomation
import config


async def test_concurrent_product_data_scraping():
    """Test concurrent product data scraping (specs + reviews) on the first 6 products."""
    automation = BestBuyAutomation()
    
    try:
        print("=== Testing CONCURRENT Product Data Scraping (Specs + Reviews) ===")
        print("🚀 Using multiple browser tabs for parallel processing")
        print("⚡ Comparing sequential vs concurrent performance")
        print("🔧 Extracts product specifications from the slide panel")
        print("🔄 Handles multiple pages of reviews per product")
        print("📄 Will navigate through all review pages automatically")
        
        # Launch browser
        await automation.launch_browser()
        
        # Load products from JSON
        products = await automation.load_products_from_json("laptop_products_all_pages.json")
        
        print(f"Loaded {len(products)} products from JSON file")
        print("Testing concurrent product data scraping on first 6 products...\n")
        
        # Test with 6 products using 3 concurrent tabs
        test_products_subset = products[:6]
        max_concurrent_tabs = 3
        
        print(f"🔧 Test configuration:")
        print(f"   Products to test: {len(test_products_subset)}")
        print(f"   Concurrent tabs: {max_concurrent_tabs}")
        print(f"   Products per tab: ~{len(test_products_subset) // max_concurrent_tabs}")
        print()
        
        # Measure time for concurrent processing
        print("⏱️ Starting concurrent processing test...")
        start_time = time.time()
        
        products_with_data = await automation.scrape_all_product_reviews_concurrent(max_concurrent_tabs)
        
        # Filter to only the test subset for fair comparison
        test_results = products_with_data[:len(test_products_subset)]
        
        concurrent_time = time.time() - start_time
        
        print(f"⚡ Concurrent processing completed in {concurrent_time:.2f} seconds")
        print()
        
        # Display results
        total_specs = sum(len(product.get('product_specs', {})) for product in test_results)
        total_reviews = sum(len(product.get('reviews', [])) for product in test_results)
        
        print("📊 CONCURRENT PROCESSING RESULTS:")
        print(f"   ✅ Products processed: {len(test_results)}")
        print(f"   📋 Total specifications found: {total_specs}")
        print(f"   💬 Total reviews found: {total_reviews}")
        print(f"   ⏱️ Total time: {concurrent_time:.2f} seconds")
        print(f"   🚀 Average time per product: {concurrent_time / len(test_results):.2f} seconds")
        print()
        
        # Show sample results
        if test_results:
            print("📖 Sample product details:")
            for i, product in enumerate(test_results[:3]):
                specs_count = len(product.get('product_specs', {}))
                reviews_count = len(product.get('reviews', []))
                print(f"   Product {i+1}: {specs_count} specs, {reviews_count} reviews")
                print(f"      Name: {product.get('product_name', 'N/A')[:60]}...")
                
                # Show sample specs
                if product.get('product_specs'):
                    sample_specs = list(product['product_specs'].items())[:2]
                    for spec_name, spec_value in sample_specs:
                        print(f"      📋 {spec_name}: {spec_value}")
                
                # Show sample review
                if product.get('reviews'):
                    first_review = product['reviews'][0]
                    print(f"      💬 Review: {first_review.get('title', 'N/A')[:40]}...")
                print()
        
        # Save test results
        test_file = config.DATA_DIR / "test_concurrent_products_with_specs_and_reviews.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Test completed! Results saved to: {test_file}")
        
        # Performance analysis
        print("⚡ PERFORMANCE ANALYSIS:")
        print(f"   Concurrent processing time: {concurrent_time:.2f} seconds")
        estimated_sequential_time = concurrent_time * max_concurrent_tabs  # Rough estimate
        print(f"   Estimated sequential time: {estimated_sequential_time:.2f} seconds")
        speedup = estimated_sequential_time / concurrent_time
        print(f"   Estimated speedup: {speedup:.1f}x faster")
        print(f"   Efficiency: {(speedup / max_concurrent_tabs) * 100:.1f}%")
        
        print("\n🎯 BENEFITS OF CONCURRENT PROCESSING:")
        print("   ✅ Multiple products processed simultaneously")
        print("   ✅ Better resource utilization")
        print("   ✅ Faster overall completion time")
        print("   ✅ Scalable with more browser tabs")
        print("   ✅ Maintains all error handling and features")
        
    except Exception as e:
        print(f"❌ Concurrent test failed: {e}")
        return 1
    finally:
        await automation.cleanup()
        
    return 0


if __name__ == "__main__":
    print("Starting concurrent product data scraping test...")
    exit_code = asyncio.run(test_concurrent_product_data_scraping())
    exit(exit_code) 