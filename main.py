#!/usr/bin/env python3
"""
Graph-First Project Intelligence System
Track 9 Hackathon Entry

Main entry point for the system.
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(__file__))

from src.workflow import run_pipeline, save_results
from src.utils.data_loader import (
    load_email_data,
    load_calendar_data,
    create_sample_dataset
)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Graph-First Project Intelligence System - Extract verifiable project knowledge from emails"
    )
    
    parser.add_argument(
        '--emails',
        type=str,
        help='Path to email data JSON file'
    )
    
    parser.add_argument(
        '--calendar',
        type=str,
        help='Path to calendar data JSON file (optional)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Output directory for results (default: ./output)'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create sample dataset for testing'
    )
    
    parser.add_argument(
        '--run-sample',
        action='store_true',
        help='Run pipeline on sample dataset'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    # Create sample dataset
    if args.create_sample:
        create_sample_dataset('./data')
        return
    
    # Run on sample data
    if args.run_sample:
        print("Running pipeline on sample dataset...")
        if not os.path.exists('./data/sample_emails.json'):
            print("Sample data not found. Creating...")
            create_sample_dataset('./data')
        
        raw_emails = load_email_data('./data/sample_emails.json')
        raw_calendar = load_calendar_data('./data/sample_calendar.json')
        
        result = run_pipeline(
            raw_emails=raw_emails,
            raw_calendar=raw_calendar,
            verbose=not args.quiet
        )
        
        save_results(result, args.output)
        return
    
    # Run on provided data
    if not args.emails:
        print("Error: Must provide --emails or use --run-sample or --create-sample")
        parser.print_help()
        return
    
    if not os.path.exists(args.emails):
        print(f"Error: Email file not found: {args.emails}")
        return
    
    # Load data
    print(f"Loading emails from {args.emails}...")
    raw_emails = load_email_data(args.emails)
    
    raw_calendar = []
    if args.calendar:
        if os.path.exists(args.calendar):
            print(f"Loading calendar from {args.calendar}...")
            raw_calendar = load_calendar_data(args.calendar)
        else:
            print(f"Warning: Calendar file not found: {args.calendar}")
    
    # Check for API keys
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("\n⚠️  WARNING: No API key found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("Create a .env file with:")
        print("  OPENAI_API_KEY=your_key_here")
        print("  or")
        print("  ANTHROPIC_API_KEY=your_key_here")
        return
    
    # Run pipeline
    result = run_pipeline(
        raw_emails=raw_emails,
        raw_calendar=raw_calendar,
        verbose=not args.quiet
    )
    
    # Save results
    save_results(result, args.output)


if __name__ == "__main__":
    main()
