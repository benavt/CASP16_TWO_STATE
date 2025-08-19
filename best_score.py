#!/usr/bin/env python3
"""
Best Score Finder for CASP Assessment

This script takes a target ID, score type, and version as input and finds the best scores
for that combination across all groups and model versions.

Usage:
    python best_score.py <TARGET> <SCORE_TYPE> <VERSION>

Examples:
    python best_score.py M1228 GDT_TS v1
    python best_score.py T1228 TMscore v2
    python best_score.py R1203 composite_score_4 both
"""

import pandas as pd
import sys
import os
from pathlib import Path

def get_v1_ref_df(target_id, score_type):
    """Get the v1 reference dataframe for a given target and score type."""
    file_path = f'./DATA/{target_id}_v1_{score_type}_scores.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path)
    return df

def get_v2_ref_df(target_id, score_type):
    """Get the v2 reference dataframe for a given target and score type."""
    # Handle special cases for different targets
    version = 'v2'
    if target_id == "T1228":
        version = 'v2_1'
    elif target_id == "T1239":
        version = 'v1_1'
    
    file_path = f'./DATA/{target_id}_{version}_{score_type}_scores.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path)
    return df

def get_group_name_lookup():
    """Get the mapping between group numbers and group names."""
    lookup = {}
    lookup_file = 'group_number_name_correspondance.csv'
    
    if os.path.exists(lookup_file):
        with open(lookup_file, newline='') as csvfile:
            import csv
            reader = csv.DictReader(csvfile)
            for row in reader:
                lookup[row['Group Number'].zfill(3)] = row['Group Name']
    
    return lookup

def find_best_scores(target_id, score_type, version):
    """Find the best scores for a given target, score type, and version."""
    
    try:
        # Load the data based on version
        if version == 'v1':
            v1_df = get_v1_ref_df(target_id, score_type)
            v2_df = None
            print(f"Processing {target_id} with {score_type} scores for v1 only...")
            print(f"v1 data: {len(v1_df)} rows")
        elif version == 'v2':
            v1_df = None
            v2_df = get_v2_ref_df(target_id, score_type)
            print(f"Processing {target_id} with {score_type} scores for v2 only...")
            print(f"v2 data: {len(v2_df)} rows")
        else:  # both versions
            v1_df = get_v1_ref_df(target_id, score_type)
            v2_df = get_v2_ref_df(target_id, score_type)
            print(f"Processing {target_id} with {score_type} scores for both versions...")
            print(f"v1 data: {len(v1_df)} rows")
            print(f"v2 data: {len(v2_df)} rows")
        
        # Get group name lookup
        group_name_lookup = get_group_name_lookup()
        
        # Handle different data structures
        if 'Model Version' not in v1_df.columns or 'Model Version' not in v2_df.columns:
            # Simple case: no model version column
            v1_df_by_model_v1 = v1_df
            v1_df_by_model_v2 = v1_df
            v2_df_by_model_v1 = v2_df
            v2_df_by_model_v2 = v2_df
        else:
            # Complex case: separate by model version
            v1_df_by_model_v1 = v1_df[v1_df['Model Version'] == 'v1']
            v1_df_by_model_v2 = v1_df[v1_df['Model Version'] == 'v2']
            v2_df_by_model_v1 = v2_df[v2_df['Model Version'] == 'v1']
            v2_df_by_model_v2 = v2_df[v2_df['Model Version'] == 'v2']
        
        # Get unique groups based on version
        if version == 'v1':
            groups = v1_df['Group'].unique()
        elif version == 'v2':
            groups = v2_df['Group'].unique()
        else:  # both versions
            groups = pd.concat([v1_df['Group'], v2_df['Group']]).unique()
        
        print(f"Found {len(groups)} unique groups")
        
        # Initialize results
        results = []
        
        # Check if this target only has one group
        one_group_only = target_id in ['R1203', 'T1214']
        
        # Process each group
        for group in groups:
            if version == 'v1':
                # Process v1 only
                if 'Model Version' in v1_df.columns:
                    v1_v1_best = v1_df[(v1_df['Group'] == group) & (v1_df['Model Version'] == 'v1')][score_type].max() if len(v1_df[(v1_df['Group'] == group) & (v1_df['Model Version'] == 'v1')]) > 0 else 0.0
                    v1_v2_best = v1_df[(v1_df['Group'] == group) & (v1_df['Model Version'] == 'v2')][score_type].max() if len(v1_df[(v1_df['Group'] == group) & (v1_df['Model Version'] == 'v2')]) > 0 else 0.0
                    best_score = max(v1_v1_best, v1_v2_best)
                    best_source = 'v1_v1' if v1_v1_best > v1_v2_best else 'v1_v2'
                else:
                    best_score = v1_df[v1_df['Group'] == group][score_type].max() if len(v1_df[v1_df['Group'] == group]) > 0 else 0.0
                    best_source = 'v1'
                
                group_name = group_name_lookup.get(group, group)
                results.append({
                    'Group': group,
                    'Group_Name': group_name,
                    'Best_Score': best_score,
                    'Best_Source': best_source,
                    'v1_Score': best_score
                })
                
            elif version == 'v2':
                # Process v2 only
                if 'Model Version' in v2_df.columns:
                    v2_v1_best = v2_df[(v2_df['Group'] == group) & (v2_df['Model Version'] == 'v1')][score_type].max() if len(v2_df[(v2_df['Group'] == group) & (v2_df['Model Version'] == 'v1')]) > 0 else 0.0
                    v2_v2_best = v2_df[(v2_df['Group'] == group) & (v2_df['Model Version'] == 'v2')][score_type].max() if len(v2_df[(v2_df['Group'] == group) & (v2_df['Model Version'] == 'v2')]) > 0 else 0.0
                    best_score = max(v2_v1_best, v2_v2_best)
                    best_source = 'v2_v1' if v2_v1_best > v2_v2_best else 'v2_v2'
                else:
                    best_score = v2_df[v2_df['Group'] == group][score_type].max() if len(v2_df[v2_df['Group'] == group]) > 0 else 0.0
                    best_source = 'v2'
                
                group_name = group_name_lookup.get(group, group)
                results.append({
                    'Group': group,
                    'Group_Name': group_name,
                    'Best_Score': best_score,
                    'Best_Source': best_source,
                    'v2_Score': best_score
                })
                
            else:  # both versions
                if not one_group_only:
                    # Get best scores for each model/version combination
                    v1_v1_best = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group][score_type].max() if len(v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]) > 0 else 0.0
                    v1_v2_best = v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group][score_type].max() if len(v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group]) > 0 else 0.0
                    v2_v1_best = v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group][score_type].max() if len(v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group]) > 0 else 0.0
                    v2_v2_best = v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group][score_type].max() if len(v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group]) > 0 else 0.0
                    
                    # Find the best overall score
                    scores = [v1_v1_best, v1_v2_best, v2_v1_best, v2_v2_best]
                    best_score = max(scores)
                    best_source_idx = scores.index(best_score)
                    best_source = ['v1_v1', 'v1_v2', 'v2_v1', 'v2_v2'][best_source_idx]
                    
                    # Get model numbers for best scores
                    v1_v1_model = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group].loc[v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group][score_type].idxmax(), 'Model Number'] if len(v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]) > 0 else None
                    v1_v2_model = v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group].loc[v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group][score_type].idxmax(), 'Model Number'] if len(v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group]) > 0 else None
                    v2_v1_model = v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group].loc[v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group][score_type].idxmax(), 'Model Number'] if len(v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group]) > 0 else None
                    v2_v2_model = v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group].loc[v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group][score_type].idxmax(), 'Model Number'] if len(v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group]) > 0 else None
                    
                    # Calculate combined score
                    combined_score = v1_v1_best + v2_v2_best
                    
                    # Get group name if available
                    group_name = group_name_lookup.get(group, group)
                    
                    results.append({
                        'Group': group,
                        'Group_Name': group_name,
                        'Combined_Score': combined_score,
                        'Best_v1_ref': v1_v1_best,
                        'Best_v2_ref': v2_v2_best,
                        'V1_Model_For_Combined_Score': f"{group}_v1_{v1_v1_model}" if v1_v1_model else None,
                        'V2_Model_For_Combined_Score': f"{group}_v2_{v2_v2_model}" if v2_v2_model else None,
                        'Best_Score': best_score,
                        'Best_Source': best_source,
                        'v1_v1_Score': v1_v1_best,
                        'v1_v2_Score': v1_v2_best,
                        'v2_v1_Score': v2_v1_best,
                        'v2_v2_Score': v2_v2_best,
                        'v1_v1_ModelNumber': v1_v1_model,
                        'v1_v2_ModelNumber': v1_v2_model,
                        'v2_v1_ModelNumber': v2_v1_model,
                        'v2_v2_ModelNumber': v2_v2_model
                    })
                else:
                    # For targets with only one group, simplify the analysis
                    v1_best = v1_df[v1_df['Group'] == group][score_type].max() if len(v1_df[v1_df['Group'] == group]) > 0 else 0.0
                    v2_best = v2_df[v2_df['Group'] == group][score_type].max() if len(v2_df[v2_df['Group'] == group]) > 0 else 0.0
                    
                    best_score = max(v1_best, v2_best)
                    best_source = 'v1' if v1_best > v2_best else 'v2'
                    
                    group_name = group_name_lookup.get(group, group)
                    
                    results.append({
                        'Group': group,
                        'Group_Name': group_name,
                        'Best_Score': best_score,
                        'Best_Source': best_source,
                        'v1_Score': v1_best,
                        'v2_Score': v2_best
                    })
        
        # Convert to DataFrame and sort by best score
        results_df = pd.DataFrame(results)
        if 'Best_Score' in results_df.columns:
            results_df = results_df.sort_values('Best_Score', ascending=False)
        
        return results_df
        
    except Exception as e:
        print(f"Error processing {target_id} with {score_type}: {str(e)}")
        return None


def print_summary(results_df, target_id, score_type):
    """Print a summary of the results."""
    if results_df is None or len(results_df) == 0:
        print(f"No results found for {target_id} with {score_type}")
        return
    
    print(f"\n=== SUMMARY FOR {target_id} - {score_type} ===")
    print(f"Total groups analyzed: {len(results_df)}")
    
    if 'Best_Score' in results_df.columns:
        print(f"Best overall score: {results_df['Best_Score'].max():.4f}")
        print(f"Average best score: {results_df['Best_Score'].mean():.4f}")
        print(f"Score range: {results_df['Best_Score'].min():.4f} - {results_df['Best_Score'].max():.4f}")
        
        # Show top 5 groups
        print(f"\nTop 5 groups by {score_type}:")
        top_5 = results_df.head(5)
        for _, row in top_5.iterrows():
            group_name = row.get('Group_Name', row['Group'])
            print(f"  {row['Group']} ({group_name}): {row['Best_Score']:.4f}")

def main():
    """Main function to run the script."""
    if len(sys.argv) != 4:
        print(__doc__)
        print(f"\nError: Expected 3 arguments, got {len(sys.argv)-1}")
        print("Usage: python best_score.py <TARGET> <SCORE_TYPE> <VERSION>")
        sys.exit(1)
    
    target_id = sys.argv[1].upper()
    score_type = sys.argv[2]
    version = sys.argv[3].lower()
    
    # Validate target ID
    valid_targets = ['M1228', 'M1239', 'R1203', 'T1214', 'T1228', 'T1239', 'T1249']
    if target_id not in valid_targets:
        print(f"Error: Invalid target ID '{target_id}'")
        print(f"Valid targets: {', '.join(valid_targets)}")
        sys.exit(1)
    
    # Validate score type
    valid_scores = ['GDT_TS', 'TMscore', 'GlobalLDDT', 'BestDockQ', 'GlobDockQ', 'AvgDockQ', 'composite_score_4']
    if score_type not in valid_scores:
        print(f"Error: Invalid score type '{score_type}'")
        print(f"Valid score types: {', '.join(valid_scores)}")
        sys.exit(1)
    
    # Validate version
    valid_versions = ['v1', 'v2', 'both']
    if version not in valid_versions:
        print(f"Error: Invalid version '{version}'")
        print(f"Valid versions: {', '.join(valid_versions)}")
        sys.exit(1)
    
    print(f"Finding best scores for target {target_id} with score type {score_type} (version: {version})")
    print("=" * 60)
    
        # Find best scores
    results = find_best_scores(target_id, score_type, version)
    
    if results is not None:
        # Print summary
        print_summary(results, target_id, score_type)
        
        # Save result
        print(f"Script completed successfully!")
    else:
        print("Script failed to process the data.")
        sys.exit(1)

if __name__ == "__main__":
    main()
