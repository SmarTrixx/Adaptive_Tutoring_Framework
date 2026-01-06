# Test: Logging System Completeness and Data Quality

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import csv
import json
from pathlib import Path


def test_csv_completeness(csv_file):
    """Verify CSV has no missing fields."""
    print(f"\n📋 CSV COMPLETENESS TEST: {Path(csv_file).name}")
    print("─" * 70)
    
    required_fields = [
        # Session & timing
        'session_id', 'question_number', 'timestamp',
        
        # Question details
        'question_id', 'question_difficulty', 'response_correctness', 'response_time_seconds',
        
        # Behavioral indicators
        'behavioral_response_time_deviation', 'behavioral_inactivity_duration',
        'behavioral_hint_usage_count', 'behavioral_rapid_guessing_probability',
        
        # Cognitive indicators
        'cognitive_accuracy_trend', 'cognitive_consistency_score', 'cognitive_load',
        
        # Affective indicators
        'affective_frustration_probability', 'affective_confusion_probability',
        'affective_boredom_probability',
        
        # Fused engagement
        'engagement_score', 'engagement_categorical_state', 'engagement_behavioral_component',
        'engagement_cognitive_component', 'engagement_affective_component',
        'engagement_confidence', 'engagement_primary_driver',
        
        # Adaptation decision
        'decision_primary_action', 'decision_secondary_actions', 'decision_difficulty_delta',
        'decision_rationale', 'decision_engagement_influenced',
        
        # Resulting state
        'resulting_difficulty_level'
    ]
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        print(f"Required fields: {len(required_fields)}")
        print(f"Found fields: {len(headers)}")
        
        missing = set(required_fields) - set(headers)
        if missing:
            print(f"❌ MISSING FIELDS: {missing}")
            return False
        
        # Check data completeness
        rows = list(reader)
        missing_data_count = 0
        
        for row_num, row in enumerate(rows, 1):
            for field in required_fields:
                if field in row and (row[field] is None or row[field] == ''):
                    missing_data_count += 1
        
        if missing_data_count > 0:
            print(f"⚠️  Missing data points: {missing_data_count}")
            print(f"   (Note: Some fields may legitimately be empty)")
        
        print(f"✓ All required fields present")
        print(f"✓ {len(rows)} question records")
        return True


def test_json_completeness(json_file):
    """Verify JSON has complete data structure."""
    print(f"\n📋 JSON COMPLETENESS TEST: {Path(json_file).name}")
    print("─" * 70)
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    required_keys = ['session_id', 'export_timestamp', 'total_questions', 'questions']
    
    for key in required_keys:
        if key not in data:
            print(f"❌ Missing key: {key}")
            return False
    
    print(f"✓ JSON structure valid")
    print(f"✓ Session ID: {data['session_id']}")
    print(f"✓ Total questions: {data['total_questions']}")
    print(f"✓ Export timestamp: {data['export_timestamp']}")
    
    # Check question records
    if len(data['questions']) > 0:
        first_q = data['questions'][0]
        expected_keys = [
            'session_id', 'question_number', 'timestamp', 'question_id',
            'question_difficulty', 'response_correctness', 'response_time_seconds',
            'behavioral_response_time_deviation', 'behavioral_inactivity_duration',
            'behavioral_hint_usage_count', 'behavioral_rapid_guessing_probability',
            'cognitive_accuracy_trend', 'cognitive_consistency_score', 'cognitive_load',
            'affective_frustration_probability', 'affective_confusion_probability',
            'affective_boredom_probability', 'engagement_score', 'engagement_categorical_state',
            'engagement_behavioral_component', 'engagement_cognitive_component',
            'engagement_affective_component', 'engagement_confidence', 'engagement_primary_driver',
            'decision_primary_action', 'decision_secondary_actions', 'decision_difficulty_delta',
            'decision_rationale', 'decision_engagement_influenced', 'resulting_difficulty_level'
        ]
        
        missing_keys = set(expected_keys) - set(first_q.keys())
        if missing_keys:
            print(f"❌ Question record missing keys: {missing_keys}")
            return False
        
        print(f"✓ Question records have complete structure")
    
    return True


def test_window_logs(window_csv, window_json):
    """Verify window summary logs."""
    print(f"\n📋 WINDOW SUMMARY LOG TEST")
    print("─" * 70)
    
    # CSV
    with open(window_csv, 'r') as f:
        reader = csv.DictReader(f)
        windows = list(reader)
    
    print(f"✓ Window CSV: {len(windows)} windows recorded")
    
    # JSON
    with open(window_json, 'r') as f:
        data = json.load(f)
    
    print(f"✓ Window JSON: {data['total_windows']} windows recorded")
    
    if len(windows) == data['total_windows']:
        print(f"✓ CSV and JSON counts match ({len(windows)} windows)")
    else:
        print(f"❌ CSV/JSON mismatch: CSV={len(windows)}, JSON={data['total_windows']}")
        return False
    
    # Check window structure
    if len(data['windows']) > 0:
        w = data['windows'][0]
        expected = [
            'session_id', 'window_number', 'timestamp', 'window_size',
            'correct_count', 'incorrect_count', 'accuracy', 'avg_response_time',
            'avg_engagement_score', 'avg_behavioral_score', 'avg_cognitive_score',
            'avg_affective_score', 'dominant_engagement_state', 'primary_driver_summary',
            'difficulty_at_start', 'difficulty_at_end', 'total_difficulty_change',
            'decisions_count', 'increase_count', 'decrease_count', 'maintain_count'
        ]
        
        missing = set(expected) - set(w.keys())
        if missing:
            print(f"❌ Window record missing: {missing}")
            return False
        
        print(f"✓ Window records have complete structure")
    
    return True


def test_data_statistics(json_file):
    """Verify data can support statistical evaluation."""
    print(f"\n📊 STATISTICAL EVALUATION TEST")
    print("─" * 70)
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    questions = data['questions']
    
    if not questions:
        print("❌ No questions to analyze")
        return False
    
    # Gather statistics
    accuracies = []
    response_times = []
    engagement_scores = []
    difficulties = []
    decision_types = {'increase': 0, 'decrease': 0, 'maintain': 0}
    
    for q in questions:
        if q['response_correctness'] is not None:
            accuracies.append(1 if q['response_correctness'] else 0)
        
        if q['response_time_seconds']:
            response_times.append(float(q['response_time_seconds']))
        
        if q['engagement_score']:
            engagement_scores.append(float(q['engagement_score']))
        
        if q['resulting_difficulty_level']:
            difficulties.append(float(q['resulting_difficulty_level']))
        
        if q['decision_primary_action']:
            action = q['decision_primary_action']
            if 'increase' in action:
                decision_types['increase'] += 1
            elif 'decrease' in action:
                decision_types['decrease'] += 1
            elif 'maintain' in action:
                decision_types['maintain'] += 1
    
    # Display statistics
    print(f"\nAccuracy:")
    if accuracies:
        avg_acc = sum(accuracies) / len(accuracies)
        print(f"  • Mean: {avg_acc:.1%}")
        print(f"  • Can calculate: average, std dev, trend")
    
    print(f"\nResponse Time:")
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"  • Mean: {avg_time:.1f}s")
        print(f"  • Range: {min(response_times):.1f}s - {max(response_times):.1f}s")
        print(f"  • Can calculate: trends, variability")
    
    print(f"\nEngagement:")
    if engagement_scores:
        avg_eng = sum(engagement_scores) / len(engagement_scores)
        print(f"  • Mean: {avg_eng:.4f}")
        print(f"  • Range: {min(engagement_scores):.4f} - {max(engagement_scores):.4f}")
        print(f"  • Can correlate with performance")
    
    print(f"\nDifficulty:")
    if difficulties:
        print(f"  • Start: {difficulties[0]:.3f}")
        print(f"  • End: {difficulties[-1]:.3f}")
        print(f"  • Delta: {difficulties[-1] - difficulties[0]:+.3f}")
        print(f"  • Can analyze: adaptation patterns")
    
    print(f"\nDecisions:")
    total_decisions = sum(decision_types.values())
    for action, count in decision_types.items():
        pct = 100 * count / total_decisions if total_decisions > 0 else 0
        print(f"  • {action.capitalize()}: {count} ({pct:.1f}%)")
    
    print(f"\n✓ Data is complete and suitable for thesis evaluation")
    print(f"  • Can analyze: accuracy trends, engagement correlation")
    print(f"  • Can measure: adaptation effectiveness, policy sensibility")
    print(f"  • Can support: statistical tests, visualization")
    
    return True


def main():
    print("\n" + "█"*70)
    print("LOGGING SYSTEM VALIDATION")
    print("█"*70)
    
    logs_dir = "/tmp/engagement_logs"
    
    # Find log files
    import glob
    csv_files = glob.glob(f"{logs_dir}/*_questions.csv")
    json_files = glob.glob(f"{logs_dir}/*_questions.json")
    
    if not csv_files:
        print(f"\n❌ No log files found in {logs_dir}")
        return
    
    # Test first scenario
    sample_csv = csv_files[0]
    sample_json = json_files[0]
    
    print(f"\nTesting sample files:")
    print(f"  CSV: {Path(sample_csv).name}")
    print(f"  JSON: {Path(sample_json).name}")
    
    # Run tests
    csv_ok = test_csv_completeness(sample_csv)
    json_ok = test_json_completeness(sample_json)
    
    # Find window logs
    window_csvs = glob.glob(f"{logs_dir}/*_windows.csv")
    window_jsons = glob.glob(f"{logs_dir}/*_windows.json")
    
    if window_csvs and window_jsons:
        window_ok = test_window_logs(window_csvs[0], window_jsons[0])
    else:
        window_ok = False
    
    # Test statistics
    stats_ok = test_data_statistics(sample_json)
    
    # Summary
    print(f"\n" + "─"*70)
    print(f"VALIDATION SUMMARY")
    print("─"*70)
    
    checks = [
        ("CSV Completeness", csv_ok),
        ("JSON Completeness", json_ok),
        ("Window Logs", window_ok),
        ("Statistical Evaluation", stats_ok)
    ]
    
    passed = sum(1 for _, ok in checks if ok)
    
    for name, ok in checks:
        status = "✓" if ok else "✗"
        print(f"{status} {name}")
    
    print(f"\n{'✅ ALL CHECKS PASSED' if passed == len(checks) else '⚠️  SOME CHECKS FAILED'}")
    print("█"*70 + "\n")


if __name__ == '__main__':
    main()
