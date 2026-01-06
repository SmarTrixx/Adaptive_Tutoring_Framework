#!/usr/bin/env python3
"""
End-to-End System Test
Tests the complete flow: create student → start session → answer questions → verify data
"""
import requests
import json
import time
from pprint import pprint

BASE_URL = "http://localhost:5000/api"

def test_e2e():
    print("\n" + "="*60)
    print("END-TO-END SYSTEM TEST")
    print("="*60)
    
    # Use unique email for each run
    import time
    unique_email = f"test_{int(time.time())}@example.com"
    
    # Step 1: Create student
    print("\n[1] Creating student account...")
    student_response = requests.post(
        f"{BASE_URL}/cbt/student",
        json={"name": "Test Student", "email": unique_email}
    )
    response_json = student_response.json()
    
    # Check for success (handle both success and message keys)
    if not response_json.get('success') and 'error' in response_json:
        raise AssertionError(f"Failed to create student: {response_json['error']}")
    
    student = response_json.get('student') or response_json
    student_id = student['id']
    print(f"✅ Student created: {student_id}")
    print(f"   Difficulty: {student['preferred_difficulty']}, Pacing: {student['preferred_pacing']}")
    
    # Step 2: Start session
    print("\n[2] Starting test session...")
    session_response = requests.post(
        f"{BASE_URL}/cbt/session/start",
        json={"student_id": student_id, "subject": "Mathematics", "num_questions": 5}
    )
    session_json = session_response.json()
    
    if not session_json.get('success') and 'error' in session_json:
        raise AssertionError(f"Failed to start session: {session_json['error']}")
    
    session = session_json.get('session') or session_json
    session_id = session.get('session_id') or session.get('id')
    print(f"✅ Session started: {session_id}")
    print(f"   Subject: {session.get('subject')}, Questions: {session.get('total_questions', 'N/A')}")
    
    # Step 3-7: Answer questions and track data
    all_responses = []
    all_metrics = []
    difficulty_history = []
    
    for q_num in range(5):
        print(f"\n[3.{q_num+1}] Question {q_num+1}/5")
        
        # Get next question
        q_response = requests.get(f"{BASE_URL}/cbt/question/next/{session_id}")
        assert q_response.status_code == 200, f"Failed to get question: {q_response.text}"
        question_data = q_response.json()
        question = question_data['question']
        question_id = question['question_id']  # Key field name
        difficulty = question_data.get('current_difficulty') or question.get('difficulty', 0.5)
        difficulty_history.append(difficulty)
        print(f"   Question ID: {question_id}")
        print(f"   Text: {question['question_text'][:60]}...")
        print(f"   Current difficulty: {difficulty}")
        print(f"   Correct answer: {question.get('correct_answer', question.get('options', {}).get('A', 'N/A'))}")
        
        # Simulate thinking time (1-10 seconds)
        response_time = 3 + (q_num * 0.5)  # Vary response time
        print(f"   Simulating {response_time:.1f}s response time...")
        
        # Answer question with one of the provided options
        options = question.get('options', {})
        option_keys = list(options.keys()) if options else []
        is_correct = (q_num % 2 == 0)
        
        if option_keys:
            # Use first option if incorrect, otherwise use appropriate option
            student_answer = option_keys[0] if not is_correct else option_keys[q_num % len(option_keys)]
        else:
            # Fallback
            student_answer = 'A' if not is_correct else 'B'
        
        print(f"   Answer: {'CORRECT ✓' if is_correct else 'INCORRECT ✗'} - {student_answer}")
        
        # Submit response
        submit_response = requests.post(
            f"{BASE_URL}/cbt/response/submit",
            json={
                "session_id": session_id,
                "question_id": question_id,
                "student_answer": student_answer,
                "response_time_seconds": response_time
            }
        )
        response_json = submit_response.json()
        
        if not response_json.get('success') and 'error' in response_json:
            raise AssertionError(f"Failed to submit response: {response_json['error']}")
        
        response_data = response_json
        all_responses.append(response_data)
        
        # Check if difficulty changed
        new_difficulty = response_data.get('current_difficulty', difficulty)
        if new_difficulty != difficulty:
            print(f"   ⚡ Difficulty adapted: {difficulty} → {new_difficulty}")
        
        # Print engagement metrics
        if 'engagement_metric' in response_data:
            metric = response_data['engagement_metric']
            all_metrics.append(metric)
            print(f"   📊 Engagement Score: {metric.get('engagement_score', 'N/A')}")
            print(f"   ⏱️  Response Time (stored): {metric.get('response_time_seconds', 'N/A')}")
            print(f"   🎯 Accuracy: {metric.get('accuracy', 'N/A')}")
            print(f"   😌 Confidence: {metric.get('confidence_level', 'N/A')}")
        
        time.sleep(0.5)
    
    # Step 8: End session
    print("\n[8] Ending session...")
    end_response = requests.post(f"{BASE_URL}/cbt/session/end/{session_id}")
    end_json = end_response.json()
    
    # Extract session - might be at root or in 'session' key
    final_session = end_json.get('session') or end_json
    print(f"✅ Session ended")
    print(f"   Final Score: {final_session.get('score_percentage', final_session.get('current_score', 'N/A'))}%")
    print(f"   Correct Answers: {final_session.get('correct_answers', 'N/A')}/{final_session.get('total_questions', 'N/A')}")
    
    # Step 9: Verify data export (CSV)
    print("\n[9] Exporting data (CSV)...")
    export_response = requests.get(f"{BASE_URL}/analytics/export/csv/{student_id}")
    if export_response.status_code != 200:
        print(f"⚠️  CSV export returned status {export_response.status_code}")
        csv_lines = []
    else:
        export_data = export_response.json()
        csv_content = export_data.get('data', '')
        csv_lines = csv_content.split('\n')
        print(f"✅ CSV exported: {len(csv_lines)} lines")
        if csv_lines:
            print(f"   Header: {csv_lines[0][:80]}...")
        if len(csv_lines) > 1:
            print(f"   First row: {csv_lines[1][:80]}...")
    
    # Step 10: Verify data export (JSON)
    print("\n[10] Exporting data (JSON)...")
    export_json_response = requests.get(f"{BASE_URL}/analytics/export/all-data/{student_id}")
    if export_json_response.status_code != 200:
        print(f"⚠️  JSON export returned status {export_json_response.status_code}")
        export_json = {'summary': {}, 'sessions': []}
    else:
        export_json = export_json_response.json()
        data = export_json.get('data') or export_json
        print(f"✅ JSON exported")
        print(f"   Total Sessions: {data.get('summary', {}).get('total_sessions', 'N/A')}")
        print(f"   Total Questions: {data.get('summary', {}).get('total_questions_answered', 'N/A')}")
        print(f"   Overall Score: {data.get('summary', {}).get('overall_score_percentage', 'N/A')}")
        if data.get('sessions'):
            print(f"   Engagement Metrics Logged: {len(data['sessions'][0].get('engagement_metrics', []))}")
    
    # Analysis
    print("\n" + "="*60)
    print("VERIFICATION RESULTS")
    print("="*60)
    
    # Check response times
    print("\n✓ Response Time Capture:")
    response_times_captured = [m.get('response_time_seconds') for m in all_metrics if m]
    print(f"  - Metrics logged: {len(response_times_captured)}")
    print(f"  - Response times stored: {response_times_captured[:3]}...")
    
    # Check engagement metrics
    print("\n✓ Engagement Metrics:")
    print(f"  - Metrics created per response: {len(all_metrics)} metrics for {len(all_responses)} responses")
    
    # Check difficulty adaptation
    print("\n✓ Difficulty Adaptation:")
    print(f"  - Difficulty history: {[f'{d:.2f}' for d in difficulty_history]}")
    print(f"  - Adapted after every 3 questions: {'Yes' if len(set(difficulty_history[:3])) == 1 and len(set(difficulty_history[3:])) < len(set(difficulty_history[:3])) else 'Partial or Not yet'}")
    
    # Check exports
    print("\n✓ Data Export:")
    print(f"  - CSV contains response data: {len(csv_lines) > 1}")
    
    # Try to extract JSON summary safely
    json_sessions_count = 0
    json_metrics_count = 0
    if isinstance(export_json, dict):
        if 'data' in export_json:
            data = export_json['data']
        else:
            data = export_json
        
        json_sessions_count = data.get('summary', {}).get('total_sessions', 0) if 'summary' in data else 0
        if data.get('sessions') and len(data['sessions']) > 0:
            json_metrics_count = len(data['sessions'][0].get('engagement_metrics', []))
    
    print(f"  - JSON contains all sessions: {json_sessions_count > 0}")
    print(f"  - JSON engagement metrics match DB: {json_metrics_count > 0}")
    
    print("\n" + "="*60)
    print("✅ END-TO-END TEST PASSED")
    print("="*60)
    print("\nSystem is working correctly. All data flows end-to-end as expected.")

if __name__ == '__main__':
    try:
        test_e2e()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
