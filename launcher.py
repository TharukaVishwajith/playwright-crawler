#!/usr/bin/env python3
"""
Best Buy Automation Launcher

This script provides easy access to both phases of the automation:
- Phase 1: Product listing scraping 
- Phase 2: Review scraping

Usage:
    source .venv/bin/activate
    python launcher.py
"""

import sys
import subprocess
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent


def show_menu():
    """Display the main menu options."""
    print("=" * 60)
    print("🚀 BEST BUY AUTOMATION LAUNCHER")
    print("=" * 60)
    print()
    print("Choose what you want to run:")
    print()
    print("1️⃣  Phase 1: Product Listing Scraping")
    print("    📋 Scrapes laptop products from Best Buy search results")
    print("    📁 Output: data/laptop_products_all_pages.json")
    print()
    print("2️⃣  Phase 2: Review Scraping (requires Phase 1 complete)")
    print("    💬 Scrapes customer reviews for each product")
    print("    📁 Input:  data/laptop_products_all_pages.json")
    print("    📁 Output: data/laptop_products_with_reviews.json")
    print()
    print("3️⃣  Test Review Scraping (first 3 products only)")
    print("    🧪 Tests review scraping on a small subset")
    print("    📁 Output: data/test_products_with_reviews.json")
    print()
    print("4️⃣  Run Both Phases (complete automation)")
    print("    🔄 Runs Phase 1, then Phase 2 automatically")
    print()
    print("5️⃣  Exit")
    print()


def check_phase1_complete():
    """Check if Phase 1 has been completed."""
    input_file = script_dir / "data" / "laptop_products_all_pages.json"
    return input_file.exists()


def run_command(command, description):
    """Run a command and handle the result."""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, cwd=script_dir)
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully!")
        else:
            print(f"\n❌ {description} failed with exit code {result.returncode}")
        return result.returncode
    except KeyboardInterrupt:
        print(f"\n⚠️  {description} interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running {description}: {e}")
        return 1


def main():
    """Main launcher function."""
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return 0
        
        if choice == "1":
            # Phase 1: Product Listing Scraping
            print("\n📋 Starting Phase 1: Product Listing Scraping...")
            run_command("python main.py", "Phase 1: Product Listing Scraping")
            
        elif choice == "2":
            # Phase 2: Review Scraping
            if not check_phase1_complete():
                print("\n❌ Phase 1 must be completed first!")
                print("📁 Missing file: data/laptop_products_all_pages.json")
                print("🔧 Please run Phase 1 first (option 1)")
                input("\nPress Enter to continue...")
                continue
            
            print("\n💬 Starting Phase 2: Review Scraping...")
            run_command("python run_review_scraping_only.py", "Phase 2: Review Scraping")
            
        elif choice == "3":
            # Test Review Scraping
            if not check_phase1_complete():
                print("\n❌ Phase 1 must be completed first!")
                print("📁 Missing file: data/laptop_products_all_pages.json")
                print("🔧 Please run Phase 1 first (option 1)")
                input("\nPress Enter to continue...")
                continue
                
            print("\n🧪 Starting Test Review Scraping...")
            run_command("python test_review_scraping.py", "Test Review Scraping")
            
        elif choice == "4":
            # Run Both Phases
            print("\n🔄 Starting Complete Automation (Both Phases)...")
            
            # Run Phase 1
            result1 = run_command("python main.py", "Phase 1: Product Listing Scraping")
            
            if result1 == 0:
                print("\n⏭️  Phase 1 completed, starting Phase 2...")
                run_command("python run_review_scraping_only.py", "Phase 2: Review Scraping")
            else:
                print("\n❌ Phase 1 failed, stopping automation")
            
        elif choice == "5":
            print("\n👋 Goodbye!")
            return 0
            
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
        
        print("\n" + "=" * 60)
        input("Press Enter to return to the main menu...")


if __name__ == "__main__":
    main() 