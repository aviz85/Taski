#!/usr/bin/env python
"""
סקריפט להרצת כל בדיקות הקצה-לקצה ובדיקות ה-API של מערכת Taski
"""

import unittest
import sys
import os
import time
import subprocess
import argparse
from datetime import datetime

def run_django_server():
    """הפעלת שרת ה-Django באופן זמני לבדיקות"""
    print("מפעיל את שרת Django...")
    
    # בדיקה אם השרת כבר פועל
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        if result == 0:
            print("שרת Django כבר פועל")
            sock.close()
            return None
        sock.close()
    except:
        pass
    
    # הפעלת השרת
    server_process = subprocess.Popen(
        ["python", "manage.py", "runserver"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    
    # המתנה להפעלת השרת
    time.sleep(5)
    return server_process

def run_tests(test_type):
    """הרצת בדיקות לפי סוג"""
    if test_type == "api" or test_type == "all":
        print("\n=== הרצת בדיקות API ===")
        from test_api import TaskiAPITests
        api_suite = unittest.TestLoader().loadTestsFromTestCase(TaskiAPITests)
        api_result = unittest.TextTestRunner(verbosity=2).run(api_suite)
        
        if api_result.failures or api_result.errors:
            return False
    
    if test_type == "ui" or test_type == "all":
        print("\n=== הרצת בדיקות ממשק משתמש ===")
        from test_end_to_end import TaskiEndToEndTests
        ui_suite = unittest.TestLoader().loadTestsFromTestCase(TaskiEndToEndTests)
        ui_result = unittest.TextTestRunner(verbosity=2).run(ui_suite)
        
        if ui_result.failures or ui_result.errors:
            return False
    
    return True

def generate_report(success):
    """יצירת דו"ח בדיקות בסיסי"""
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_dir, f"test_report_{timestamp}.txt")
    
    with open(report_file, "w") as f:
        f.write(f"== Taski Test Report ==\n")
        f.write(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status: {'SUCCESS' if success else 'FAILURE'}\n\n")
        
        # במערכת אמיתית היינו מוסיפים כאן עוד נתונים ופרטים על הבדיקות
    
    print(f"\nדו\"ח בדיקות נוצר ב: {report_file}")

def main():
    """פונקציה ראשית להרצת כל הבדיקות"""
    parser = argparse.ArgumentParser(description='Run Taski end-to-end tests')
    parser.add_argument('--type', choices=['all', 'api', 'ui'], default='all', 
                        help='סוגי הבדיקות להרצה (api, ui, או all לשניהם)')
    
    args = parser.parse_args()
    
    # וידוא שהסקריפט רץ מתיקיית הבדיקות
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # הפעלת שרת Django
    server_process = run_django_server()
    
    try:
        # הרצת הבדיקות
        success = run_tests(args.type)
        
        # יצירת דו"ח
        generate_report(success)
        
        # החזרת קוד היציאה המתאים
        return 0 if success else 1
    
    finally:
        # כיבוי שרת Django אם הפעלנו אותו
        if server_process:
            print("כיבוי שרת Django...")
            server_process.terminate()
            server_process.wait()

if __name__ == '__main__':
    sys.exit(main()) 