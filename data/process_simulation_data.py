"""
Data Processing Pipeline
=========================

Converts raw system outputs from learner simulation into Chapter 4 tables.

Pipeline:
1. Load raw simulation data (system outputs)
2. Extract and normalize data from system responses
3. Compute summary statistics
4. Generate Chapter 4 tables
5. Export results for thesis
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# ============================================================================
# DATA EXTRACTION
# ============================================================================

def extract_from_simulation(json_file: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Extract structured data from simulation JSON.
    Returns: (responses_df, engagement_df, adaptations_df)
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    responses = []
    engagement_metrics = []
    adaptations = []
    
    # Process both conditions
    for condition_key in ['adaptive', 'non_adaptive']:
        learners = data.get(condition_key, [])
        
        for learner_data in learners:
            learner_id = learner_data['learner_id']
            profile = learner_data['profile']
            interactions = learner_data['interactions']
            # Use the condition from the data, not from learner_id
            actual_condition = learner_data.get('condition', condition_key)
            
            for interaction in interactions:
                request = interaction['request']
                response = interaction['response']
                
                # Extract response data
                response_record = {
                    'learner_id': learner_id,
                    'condition': actual_condition,
                    'profile': profile,
                    'response_time_seconds': request.get('response_time_seconds'),
                    'is_correct': response.get('is_correct', False),
                    'option_changes': request.get('option_changes', 0),
                    'hints_used': request.get('hints_used', 0),
                    'pauses_during_response': request.get('pauses_during_response', 0),
                    'timestamp': interaction['timestamp']
                }
                responses.append(response_record)
                
                # Extract engagement metrics
                if 'engagement_score' in response:
                    engagement_record = {
                        'learner_id': learner_id,
                        'condition': actual_condition,
                        'response_time_seconds': request.get('response_time_seconds'),
                        'engagement_score': response.get('engagement_score'),
                        'engagement_level': response.get('engagement_level', 'medium'),
                        'accuracy_recent': response.get('accuracy_recent', 0.5),
                        'timestamp': interaction['timestamp']
                    }
                    engagement_metrics.append(engagement_record)
                
                # Extract adaptation events (all responses have action_type)
                if 'action_type' in response:
                    adapt_record = {
                        'learner_id': learner_id,
                        'condition': actual_condition,
                        'previous_difficulty': response.get('previous_difficulty'),
                        'new_difficulty': response.get('new_difficulty'),
                        'action_type': response.get('action_type', 'maintain'),
                        'reason': response.get('reason', ''),
                        'engagement_level': response.get('engagement_level'),
                        'timestamp': interaction['timestamp']
                    }
                    adaptations.append(adapt_record)
    
    return (
        pd.DataFrame(responses),
        pd.DataFrame(engagement_metrics),
        pd.DataFrame(adaptations)
    )

# ============================================================================
# CHAPTER 4 TABLE GENERATION
# ============================================================================

def generate_table_41(learners_info: Dict) -> pd.DataFrame:
    """Table 4.1: Participant Characteristics Summary"""
    
    adaptive_learners = [l for l in learners_info if l['condition'] == 'adaptive']
    nonadapt_learners = [l for l in learners_info if l['condition'] == 'non-adaptive']
    
    table = pd.DataFrame({
        'Characteristic': [
            'Number of participants',
            'Profile distribution',
            'Mean accuracy (baseline)',
            'Engagement recovery capability'
        ],
        'Adaptive (n=10)': [
            len(adaptive_learners),
            'Mixed archetypes',
            f"{np.mean([l['accuracy'] for l in adaptive_learners]):.2f}",
            'High (adaptive support)'
        ],
        'Non-Adaptive (n=10)': [
            len(nonadapt_learners),
            'Mixed archetypes',
            f"{np.mean([l['accuracy'] for l in nonadapt_learners]):.2f}",
            'None (fixed difficulty)'
        ]
    })
    
    return table

def generate_table_43(responses_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Table 4.3: Pre-Test and Post-Test Performance Scores"""
    
    # Group by learner and condition to get accuracy
    learner_accuracy = responses_df.groupby(['learner_id', 'condition']).agg({
        'is_correct': ['sum', 'count']
    }).reset_index()
    learner_accuracy.columns = ['learner_id', 'condition', 'correct', 'total']
    learner_accuracy['accuracy'] = learner_accuracy['correct'] / learner_accuracy['total'] * 100
    
    # Summary by condition
    summary = learner_accuracy.groupby('condition')['accuracy'].agg(['mean', 'std', 'count'])
    
    # Handle missing conditions gracefully
    adaptive_mean = summary.loc['adaptive', 'mean'] if 'adaptive' in summary.index else 0
    adaptive_std = summary.loc['adaptive', 'std'] if 'adaptive' in summary.index else 0
    nonadapt_mean = summary.loc['non-adaptive', 'mean'] if 'non-adaptive' in summary.index else 0
    nonadapt_std = summary.loc['non-adaptive', 'std'] if 'non-adaptive' in summary.index else 0
    
    # Handle NaN values
    adaptive_mean = adaptive_mean if not pd.isna(adaptive_mean) else 0
    adaptive_std = adaptive_std if not pd.isna(adaptive_std) else 0
    nonadapt_mean = nonadapt_mean if not pd.isna(nonadapt_mean) else 0
    nonadapt_std = nonadapt_std if not pd.isna(nonadapt_std) else 0
    
    table = pd.DataFrame({
        'Group': ['Adaptive', 'Non-Adaptive'],
        'Mean Accuracy': [
            f"{adaptive_mean:.1f}% ± {adaptive_std:.1f}%",
            f"{nonadapt_mean:.1f}% ± {nonadapt_std:.1f}%"
        ],
        'Total Questions': [
            int(learner_accuracy[learner_accuracy['condition']=='adaptive']['total'].sum()),
            int(learner_accuracy[learner_accuracy['condition']=='non-adaptive']['total'].sum())
        ]
    })
    
    return table, learner_accuracy

def generate_table_45(engagement_df: pd.DataFrame) -> pd.DataFrame:
    """Table 4.5: Engagement State Frequency and Duration"""
    
    if len(engagement_df) == 0:
        return pd.DataFrame()
    
    # Count engagement levels by condition
    engage_counts = engagement_df.groupby(['condition', 'engagement_level']).size().unstack(fill_value=0)
    engage_pct = engage_counts.div(engage_counts.sum(axis=1), axis=0) * 100
    
    # Ensure all levels exist
    for level in ['low', 'medium', 'high']:
        if level not in engage_pct.columns:
            engage_pct[level] = 0.0
    
    table = pd.DataFrame({
        'Engagement State': ['Low', 'Moderate', 'High'],
        'Adaptive (% Time)': [
            f"{engage_pct.loc['adaptive', 'low']:.1f}%" if 'adaptive' in engage_pct.index else "0.0%",
            f"{engage_pct.loc['adaptive', 'medium']:.1f}%" if 'adaptive' in engage_pct.index else "0.0%",
            f"{engage_pct.loc['adaptive', 'high']:.1f}%" if 'adaptive' in engage_pct.index else "0.0%"
        ],
        'Non-Adaptive (% Time)': [
            f"{engage_pct.loc['non-adaptive', 'low']:.1f}%" if 'non-adaptive' in engage_pct.index else "0.0%",
            f"{engage_pct.loc['non-adaptive', 'medium']:.1f}%" if 'non-adaptive' in engage_pct.index else "0.0%",
            f"{engage_pct.loc['non-adaptive', 'high']:.1f}%" if 'non-adaptive' in engage_pct.index else "0.0%"
        ]
    })
    
    return table

def generate_table_46(responses_df: pd.DataFrame) -> pd.DataFrame:
    """Table 4.6: Session-Level Behavioral Metrics Summary"""
    
    # Group by learner and condition
    behavior = responses_df.groupby(['learner_id', 'condition']).agg({
        'response_time_seconds': ['mean', 'std'],
        'option_changes': ['mean', 'std'],
        'hints_used': ['mean', 'std']
    }).reset_index()
    
    behavior.columns = ['learner_id', 'condition', 
                       'rt_mean', 'rt_std', 
                       'oc_mean', 'oc_std',
                       'hints_mean', 'hints_std']
    
    # Summary by condition
    adaptive_behavior = behavior[behavior['condition'] == 'adaptive']
    nonadapt_behavior = behavior[behavior['condition'] == 'non-adaptive']
    
    table = pd.DataFrame({
        'Metric': [
            'Average response time (seconds)',
            'Option changes per response',
            'Hints used per response'
        ],
        'Adaptive (Mean ± SD)': [
            f"{adaptive_behavior['rt_mean'].mean():.1f} ± {adaptive_behavior['rt_mean'].std():.1f}",
            f"{adaptive_behavior['oc_mean'].mean():.2f} ± {adaptive_behavior['oc_mean'].std():.2f}",
            f"{adaptive_behavior['hints_mean'].mean():.2f} ± {adaptive_behavior['hints_mean'].std():.2f}"
        ],
        'Non-Adaptive (Mean ± SD)': [
            f"{nonadapt_behavior['rt_mean'].mean():.1f} ± {nonadapt_behavior['rt_mean'].std():.1f}",
            f"{nonadapt_behavior['oc_mean'].mean():.2f} ± {nonadapt_behavior['oc_mean'].std():.2f}",
            f"{nonadapt_behavior['hints_mean'].mean():.2f} ± {nonadapt_behavior['hints_mean'].std():.2f}"
        ]
    })
    
    return table

def generate_table_47(adaptations_df: pd.DataFrame) -> pd.DataFrame:
    """Table 4.7: Distribution of Adaptive Actions"""
    
    if len(adaptations_df) == 0:
        return pd.DataFrame()
    
    action_counts = adaptations_df['action_type'].value_counts()
    action_pct = (action_counts / action_counts.sum() * 100)
    
    table = pd.DataFrame({
        'Action Type': ['Increase', 'Maintain', 'Decrease'],
        'Frequency': [
            action_counts.get('increase', 0),
            action_counts.get('maintain', 0),
            action_counts.get('decrease', 0)
        ],
        'Percentage (%)': [
            f"{action_pct.get('increase', 0):.1f}",
            f"{action_pct.get('maintain', 0):.1f}",
            f"{action_pct.get('decrease', 0):.1f}"
        ]
    })
    
    return table

# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_simulation_data(
    simulation_json: str,
    output_dir: str = "/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/processed"
) -> Dict[str, pd.DataFrame]:
    """
    Complete processing pipeline:
    1. Load simulation data
    2. Extract to dataframes
    3. Generate all tables
    4. Save outputs
    """
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*70)
    print("DATA PROCESSING PIPELINE")
    print("="*70)
    
    # Load raw data
    print("\n1. Loading simulation data...")
    responses_df, engagement_df, adaptations_df = extract_from_simulation(simulation_json)
    print(f"   ✓ Loaded {len(responses_df)} responses")
    print(f"   ✓ Loaded {len(engagement_df)} engagement metrics")
    print(f"   ✓ Loaded {len(adaptations_df)} adaptations")
    
    # Generate tables
    print("\n2. Generating Chapter 4 tables...")
    
    # Get learner info
    learners_info = responses_df.groupby('learner_id').agg({
        'condition': 'first',
        'profile': 'first',
        'is_correct': ['sum', 'count']
    }).reset_index()
    learners_info.columns = ['learner_id', 'condition', 'profile', 'correct', 'total']
    learners_info['accuracy'] = learners_info['correct'] / learners_info['total']
    
    # Table 4.1
    table_41 = generate_table_41(learners_info.to_dict('records'))
    print("   ✓ Table 4.1: Participant Characteristics")
    
    # Table 4.3
    table_43, learner_acc = generate_table_43(responses_df)
    print("   ✓ Table 4.3: Performance Scores")
    
    # Table 4.5
    table_45 = generate_table_45(engagement_df)
    print("   ✓ Table 4.5: Engagement Trajectory")
    
    # Table 4.6
    table_46 = generate_table_46(responses_df)
    print("   ✓ Table 4.6: Behavioral Metrics")
    
    # Table 4.7
    table_47 = generate_table_47(adaptations_df)
    print("   ✓ Table 4.7: Adaptation Distribution")
    
    # Save tables
    print("\n3. Saving outputs...")
    tables = {
        'Table_4.1': table_41,
        'Table_4.3': table_43,
        'Table_4.5': table_45,
        'Table_4.6': table_46,
        'Table_4.7': table_47
    }
    
    for name, table in tables.items():
        output_file = f"{output_dir}/{name}.csv"
        table.to_csv(output_file, index=False)
        print(f"   ✓ {name} → {output_file}")
    
    # Save raw dataframes
    responses_df.to_csv(f"{output_dir}/raw_responses.csv", index=False)
    engagement_df.to_csv(f"{output_dir}/raw_engagement.csv", index=False)
    adaptations_df.to_csv(f"{output_dir}/raw_adaptations.csv", index=False)
    print(f"   ✓ Raw data exported")
    
    # Print summary
    print("\n4. Summary Statistics:")
    print(f"   Adaptive learners: {len(learners_info[learners_info['condition']=='adaptive'])}")
    print(f"   Non-adaptive learners: {len(learners_info[learners_info['condition']=='non-adaptive'])}")
    print(f"   Total responses: {len(responses_df)}")
    print(f"   Total adaptations: {len(adaptations_df)}")
    
    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    
    return tables

if __name__ == "__main__":
    json_file = "/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/simulated/simulation_complete.json"
    
    if Path(json_file).exists():
        process_simulation_data(json_file)
    else:
        print(f"Error: {json_file} not found")
        print("Run learner_simulation.py first to generate simulation data")
