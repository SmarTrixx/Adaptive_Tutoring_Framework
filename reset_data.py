#!/usr/bin/env python3
"""
Safe Data Reset Script for Adaptive Tutoring Framework

Clears all test/session data without affecting:
- Code and UI
- Question database
- Application logic

Usage:
    python3 reset_data.py              # Interactive confirmation
    python3 reset_data.py --confirm    # Skip confirmation
    python3 reset_data.py --help       # Show this message
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def reset_data(confirm=False):
    """Reset all session and response data"""
    
    print("\n" + "="*60)
    print("ADAPTIVE TUTORING FRAMEWORK - DATA RESET")
    print("="*60)
    print("\nThis will delete:")
    print("  • All student sessions")
    print("  • All student responses")
    print("  • All engagement metrics")
    print("\nThis will PRESERVE:")
    print("  • Question database")
    print("  • Code and UI")
    print("  • Application logic")
    print("\n" + "="*60)
    
    if not confirm:
        response = input("\n⚠️  Confirm data reset? (type 'yes' to confirm): ").strip().lower()
        if response != 'yes':
            print("\n❌ Reset cancelled")
            return False
    
    try:
        from app import create_app, db
        from app.models import Student, Session, StudentResponse, EngagementMetric
        
        app = create_app(os.getenv('FLASK_ENV', 'development'))
        
        with app.app_context():
            print("\n🔄 Starting data reset...")
            
            # Delete engagement metrics first (FK constraints)
            print("  • Deleting engagement metrics...", end='', flush=True)
            deleted_metrics = db.session.query(EngagementMetric).delete()
            print(f" ({deleted_metrics} records)")
            
            # Delete responses
            print("  • Deleting student responses...", end='', flush=True)
            deleted_responses = db.session.query(StudentResponse).delete()
            print(f" ({deleted_responses} records)")
            
            # Delete sessions
            print("  • Deleting sessions...", end='', flush=True)
            deleted_sessions = db.session.query(Session).delete()
            print(f" ({deleted_sessions} records)")
            
            # Delete students (optional - can keep student records)
            print("  • Deleting student records...", end='', flush=True)
            deleted_students = db.session.query(Student).delete()
            print(f" ({deleted_students} records)")
            
            # Commit all deletions
            db.session.commit()
            
            print("\n✅ Data reset complete!")
            print("\nReset Statistics:")
            print(f"  • Students deleted: {deleted_students}")
            print(f"  • Sessions deleted: {deleted_sessions}")
            print(f"  • Responses deleted: {deleted_responses}")
            print(f"  • Engagement metrics deleted: {deleted_metrics}")
            print("\n💡 The system is now ready for fresh testing.")
            print("="*60 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error during reset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    confirm = '--confirm' in sys.argv
    
    success = reset_data(confirm=confirm)
    sys.exit(0 if success else 1)
