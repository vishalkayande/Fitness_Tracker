"""
Utility script to check and fix database triggers that reference non-existent tables.
Run this script to find and remove problematic triggers.
"""

import mysql.connector
from config import db_config

def check_and_fix_triggers():
    """Check for triggers that reference user_summary and remove them."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("Checking for triggers in fitness_tracker_db...")
        print("-" * 60)
        
        # Find all triggers on food_log table or that reference user_summary
        cursor.execute("""
            SELECT 
                TRIGGER_NAME, 
                EVENT_MANIPULATION, 
                EVENT_OBJECT_TABLE, 
                ACTION_STATEMENT,
                ACTION_TIMING
            FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = 'fitness_tracker_db'
            AND (
                EVENT_OBJECT_TABLE = 'food_log' 
                OR ACTION_STATEMENT LIKE '%user_summary%'
            )
        """)
        
        triggers = cursor.fetchall()
        
        if not triggers:
            print("No problematic triggers found!")
            print("The issue might be elsewhere. Let's check if user_summary table exists...")
            
            # Check if user_summary table exists
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = 'fitness_tracker_db' 
                AND TABLE_NAME = 'user_summary'
            """)
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("\n✓ Confirmed: user_summary table does NOT exist")
                print("\nThis is the source of the error.")
                print("\nSolution options:")
                print("1. Remove the trigger (if any exists)")
                print("2. Create the user_summary table")
                print("\nLet's check all triggers to see what's causing this...")
                
                # Check all triggers
                cursor.execute("SHOW TRIGGERS")
                all_triggers = cursor.fetchall()
                if all_triggers:
                    print("\nAll triggers in database:")
                    for trig in all_triggers:
                        print(f"  - {trig}")
                else:
                    print("\nNo triggers found in database.")
                    
        else:
            print(f"\nFound {len(triggers)} problematic trigger(s):\n")
            for trigger in triggers:
                print(f"Trigger Name: {trigger['TRIGGER_NAME']}")
                print(f"Event: {trigger['EVENT_MANIPULATION']} on {trigger['EVENT_OBJECT_TABLE']}")
                print(f"Timing: {trigger['ACTION_TIMING']}")
                print(f"Action: {trigger['ACTION_STATEMENT'][:200]}...")
                print("-" * 60)
                
                # Ask to drop (automatically drop for now)
                trigger_name = trigger['TRIGGER_NAME']
                print(f"\nDropping trigger: {trigger_name}")
                cursor.execute(f"DROP TRIGGER IF EXISTS `{trigger_name}`")
                conn.commit()
                print(f"✓ Successfully dropped trigger: {trigger_name}")
        
        # Also check all triggers to be thorough
        print("\n" + "=" * 60)
        print("Checking all triggers in database:")
        cursor.execute("SHOW TRIGGERS")
        all_triggers = cursor.fetchall()
        if all_triggers:
            print(f"\nFound {len(all_triggers)} total trigger(s):")
            for trig in all_triggers:
                print(f"  - {trig.get('Trigger', 'N/A')}")
        else:
            print("No triggers found.")
        
        cursor.close()
        conn.close()
        print("\n" + "=" * 60)
        print("Database check completed!")
        print("You can now try adding food logs again.")
        
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Database Trigger Fixer")
    print("=" * 60)
    check_and_fix_triggers()





