"""
MIT License

Copyright (c) 2025 Tiburon Leon Benavides

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Author: Tiburon Leon Benavides
Contribution: Main contributor
Date: 2025-09-01
"""

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv
from os.path import exists

def frange(start, stop, step):
    vals = []
    while start <= stop:
        vals.append(start)
        start += step
    return vals

def get_v1_ref_df(ID, score):
    file = f'./data/{ID}_v1_{score}_scores.csv'
    df = pd.read_csv(file)
    if ID == "T1214":
        df['Model Version'] = 'v1'
    df = df.dropna()
    return df

def get_v2_ref_df(ID, score):
    version = 'v2'
    if ID == "T1228":
        version = 'v1_1'
        if not(exists(f'./data/{ID}_{version}_{score}_scores.csv')):
            version = 'v2_1'
    elif ID == "T1239":
        version = 'v1_1'

    file = f'./data/{ID}_{version}_{score}_scores.csv'
    df = pd.read_csv(file)
    if ID == "T1214":
        df['Model Version'] = 'v2'
    df = df.dropna()
    return df

def get_group_name_lookup():
    lookup = {}
    with open('./data/group_number_name_correspondance.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lookup[row['Group Number'].zfill(3)] = row['Group Name']
    return lookup

def get_best_fit(ID, v1_df, v2_df, score):
    group_name_lookup = get_group_name_lookup()
    if (
        'Model Version' not in v1_df.columns or 
        'Model Version' not in v2_df.columns or
        (('Model Version' in v1_df.columns and v1_df['Model Version'].isna().all()) and
         ('Model Version' in v2_df.columns and v2_df['Model Version'].isna().all()))
    ):
        v1_df_by_model_v1 = v1_df
        v2_df_by_model_v2 = v2_df
        v1_df_by_model_v2 = v1_df
        v2_df_by_model_v1 = v2_df
    else:
        v1_df_by_model_v1 = v1_df[v1_df['Model Version'] == 'v1']
        v1_df_by_model_v2 = v1_df[v1_df['Model Version'] == 'v2']
        v2_df_by_model_v1 = v2_df[v2_df['Model Version'] == 'v1']
        v2_df_by_model_v2 = v2_df[v2_df['Model Version'] == 'v2']
    

    # Initialize empty lists to store results
    groups = pd.concat([v1_df['Group'], v2_df['Group']]).unique()
    results = []

    one_group_only = False
    if ID == 'R1203' or ID == 'T1214':
        one_group_only = True

    # Loop through each group
    for group in groups:

        if not(one_group_only):

            # Get indices of max scores for each group, excluding groups where all scores are NaN
            v1_v1_indices = v1_df_by_model_v1.groupby('Group')[score].idxmax()
            v1_v2_indices = v1_df_by_model_v2.groupby('Group')[score].idxmax()
            v2_v1_indices = v2_df_by_model_v1.groupby('Group')[score].idxmax()
            v2_v2_indices = v2_df_by_model_v2.groupby('Group')[score].idxmax()

            # Filter out groups where idxmax returned NaN (all scores were NaN)
            v1_df_by_model_v1 = v1_df_by_model_v1.loc[v1_v1_indices.dropna()]
            v1_df_by_model_v2 = v1_df_by_model_v2.loc[v1_v2_indices.dropna()]
            v2_df_by_model_v1 = v2_df_by_model_v1.loc[v2_v1_indices.dropna()]
            v2_df_by_model_v2 = v2_df_by_model_v2.loc[v2_v2_indices.dropna()]

            v1_df_by_model_v1 = v1_df_by_model_v1.sort_values(by=score, ascending=False)
            v1_df_by_model_v2 = v1_df_by_model_v2.sort_values(by=score, ascending=False)
            v2_df_by_model_v1 = v2_df_by_model_v1.sort_values(by=score, ascending=False)
            v2_df_by_model_v2 = v2_df_by_model_v2.sort_values(by=score, ascending=False)

            # Get best scores for each version/model combination for this group
            v1_v1_group = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]
            v1_v2_group = v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group]
            v2_v1_group = v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group]
            v2_v2_group = v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group]

            v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0
            v1_v2_best = v1_v2_group[score].max() if len(v1_v2_group) > 0 else 0.0
            v2_v1_best = v2_v1_group[score].max() if len(v2_v1_group) > 0 else 0.0
            v2_v2_best = v2_v2_group[score].max() if len(v2_v2_group) > 0 else 0.0

            # Get model numbers for the best scores
            v1_v1_model_number = (
                v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
            )
            v1_v2_model_number = (
                v1_v2_group.loc[v1_v2_group[score].idxmax(), 'Model Number'] if len(v1_v2_group) > 0 else None
            )
            v2_v1_model_number = (
                v2_v1_group.loc[v2_v1_group[score].idxmax(), 'Model Number'] if len(v2_v1_group) > 0 else None
            )
            v2_v2_model_number = (
                v2_v2_group.loc[v2_v2_group[score].idxmax(), 'Model Number'] if len(v2_v2_group) > 0 else None
            )

            # Find the best overall score for this group
            scores = [s for s in [v1_v1_best, v1_v2_best, v2_v1_best, v2_v2_best] if s != 0.0]
            if scores:  
                best_score = max(scores)
                # Determine which version/model combination produced the best score
                if best_score == v1_v1_best:
                    best_source = 'v1_v1'
                elif best_score == v2_v2_best:
                    best_source = 'v2_v2'
                elif best_score == v1_v2_best:
                    best_source = 'v1_v2'
                elif best_score == v2_v1_best:
                    best_source = 'v2_v1'
            else:
                best_score = 0.0
                best_source = 'v1_v1'
        else:
            v1_df_by_model_v1 = v1_df_by_model_v1.sort_values(by=score, ascending=False)
            v1_df_by_model_v2 = v1_df_by_model_v2.sort_values(by=score, ascending=False)
            v2_df_by_model_v1 = v2_df_by_model_v1.sort_values(by=score, ascending=False)
            v2_df_by_model_v2 = v2_df_by_model_v2.sort_values(by=score, ascending=False)

            # Get best scores for each version/model combination for this group
            v1_v1_group = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]
            v1_v2_group = v1_df_by_model_v2[v1_df_by_model_v2['Group'] == group]
            v2_v1_group = v2_df_by_model_v1[v2_df_by_model_v1['Group'] == group]
            v2_v2_group = v2_df_by_model_v2[v2_df_by_model_v2['Group'] == group]

            v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0
            v2_v2_best = v2_v2_group[score].max() if len(v2_v2_group) > 0 else 0.0
            v1_v2_best = None
            v2_v1_best = None
            v1_v2_model_number = None
            v2_v1_model_number = None

            if v1_v1_best > v2_v2_best:
                best_source = 'v1_v1'
                best_score = v1_v1_best
                v1_v1_model_number = (
                    v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
                )
                v2_v2_group = v2_v2_group[v2_v2_group['Model Number'] != v1_v1_model_number]

                v2_v2_model_number = (
                    v2_v2_group.loc[v2_v2_group[score].idxmax(), 'Model Number'] if len(v2_v2_group) > 0 else None
                )
                v2_v2_best = v2_v2_group[score].max() if len(v2_v2_group) > 0 else 0.0
            else:
                best_source = 'v2_v2'
                best_score = v2_v2_best
                v2_v2_model_number = (
                    v2_v2_group.loc[v2_v2_group[score].idxmax(), 'Model Number'] if len(v2_v2_group) > 0 else None
                )
                v1_v1_group = v1_v1_group[v1_v1_group['Model Number'] != v2_v2_model_number]

                v1_v1_model_number = (
                    v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
                )
                v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0



        cumulative_score = 0
        best_v1_ref = 0
        best_v2_ref = 0
        best_v1_ref_model_number = 0
        best_v2_ref_model_number = 0
        if best_source == 'v1_v1':
            cumulative_score = v1_v1_best + v2_v2_best
            best_v1_ref = v1_v1_best
            best_v2_ref = v2_v2_best
            best_v1_ref_model_number = 'v1' + '_' + str(v1_v1_model_number)
            best_v2_ref_model_number = 'v2' + '_' + str(v2_v2_model_number)
        elif best_source == 'v1_v2':
            cumulative_score = v1_v2_best + v2_v1_best
            best_v1_ref = v1_v2_best
            best_v2_ref = v2_v1_best
            best_v1_ref_model_number = 'v2' + '_' + str(v1_v2_model_number)
            best_v2_ref_model_number = 'v1' + '_' + str(v2_v1_model_number)
        elif best_source == 'v2_v1':
            cumulative_score = v2_v1_best + v1_v2_best
            best_v2_ref = v2_v1_best
            best_v1_ref = v1_v2_best
            best_v2_ref_model_number = 'v1' + '_' + str(v2_v1_model_number)
            best_v1_ref_model_number = 'v2' + '_' + str(v1_v2_model_number)
        elif best_source == 'v2_v2':
            cumulative_score = v2_v2_best + v1_v1_best
            best_v2_ref = v2_v2_best
            best_v1_ref = v1_v1_best
            best_v2_ref_model_number = 'v2' + '_' + str(v2_v2_model_number)
            best_v1_ref_model_number = 'v1' + '_' + str(v1_v1_model_number)
        else:
            raise

        # Extract group number from group string (e.g., TS314 -> 314)
        group_number = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
        group_name = group_name_lookup.get(group_number, "Unknown").strip()

        if cumulative_score > 0: # only include groups with a positive cumulative score
            # Store results
            results.append({
                'Group': group,
                'Group_Name': group_name,
                'Combined_Score': cumulative_score,
                'Best_v1_ref': best_v1_ref,
                'Best_v2_ref': best_v2_ref,
                'V1_Model_For_Combined_Score': group + '_' + best_v1_ref_model_number,
                'V2_Model_For_Combined_Score': group + '_' + best_v2_ref_model_number,
                'Best_Score': best_score,
                'Best_Source': best_source,
                'v1_v1_Score': v1_v1_best,
                'v1_v2_Score': v1_v2_best,
                'v2_v1_Score': v2_v1_best,
                'v2_v2_Score': v2_v2_best,
                'v1_v1_ModelNumber': v1_v1_model_number,
                'v1_v2_ModelNumber': v1_v2_model_number,
                'v2_v1_ModelNumber': v2_v1_model_number,
                'v2_v2_ModelNumber': v2_v2_model_number
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    return results_df

def get_best_fit_single_state(ID, v1_df, score):
    """Single state version of get_best_fit - only uses v1 data"""
    group_name_lookup = get_group_name_lookup()
    if (
        'Model Version' not in v1_df.columns or 
        (('Model Version' in v1_df.columns and v1_df['Model Version'].isna().all()))
    ):
        v1_df_by_model_v1 = v1_df
    else:
        v1_df_by_model_v1 = v1_df[v1_df['Model Version'] == 'v1']
    

    # Initialize empty lists to store results
    groups = v1_df['Group'].unique()
    results = []

    one_group_only = False
    if ID == 'R1203' or ID == 'T1214':
        one_group_only = True

    # Loop through each group
    for group in groups:

        if not(one_group_only):

            # Get indices of max scores for each group, excluding groups where all scores are NaN
            v1_v1_indices = v1_df_by_model_v1.groupby('Group')[score].idxmax()

            # Filter out groups where idxmax returned NaN (all scores were NaN)
            v1_df_by_model_v1 = v1_df_by_model_v1.loc[v1_v1_indices.dropna()]

            v1_df_by_model_v1 = v1_df_by_model_v1.sort_values(by=score, ascending=False)

            # Get best scores for each version/model combination for this group
            v1_v1_group = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]

            v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0

            # Get model numbers for the best scores
            v1_v1_model_number = (
                v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
            )

            # Find the best overall score for this group
            if v1_v1_best != 0.0:  
                best_score = v1_v1_best
                best_source = 'v1_v1'
            else:
                best_score = 0.0
                best_source = 'v1_v1'
        else:
            v1_df_by_model_v1 = v1_df_by_model_v1.sort_values(by=score, ascending=False)

            # Get best scores for each version/model combination for this group
            v1_v1_group = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]

            v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0

            if v1_v1_best != 0.0:
                best_source = 'v1_v1'
                best_score = v1_v1_best
                v1_v1_model_number = (
                    v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
                )
            else:
                best_source = 'v1_v1'
                best_score = v1_v1_best


        cumulative_score = 0
        best_v1_ref = 0
        best_v1_ref_model_number = 0
        if best_source == 'v1_v1':
            cumulative_score = v1_v1_best
            best_v1_ref = v1_v1_best
            best_v1_ref_model_number = 'v1' + '_' + str(v1_v1_model_number)
        else:
            raise

        # Extract group number from group string (e.g., TS314 -> 314)
        group_number = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
        group_name = group_name_lookup.get(group_number, "Unknown").strip()

        if cumulative_score > 0: # only include groups with a positive cumulative score
            # Store results
            results.append({
                'Group': group,
                'Group_Name': group_name,   
                'Combined_Score': cumulative_score,
                'Best_v1_ref': best_v1_ref,
                'V1_Model_For_Combined_Score': group + '_' + best_v1_ref_model_number,
                'Best_Score': best_score,
                'Best_Source': best_source,
                'v1_v1_Score': v1_v1_best,
                'v1_v1_ModelNumber': v1_v1_model_number,
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    return results_df

def get_best_fit_dual_state(ID, v1_df, v2_df, score):
    """Dual state version of get_best_fit - finds best v1, then matching v2"""
    group_name_lookup = get_group_name_lookup()
    if (
        'Model Version' not in v1_df.columns or 
        (('Model Version' in v1_df.columns and v1_df['Model Version'].isna().all()))
    ):
        v1_df_by_model_v1 = v1_df
    else:
        v1_df_by_model_v1 = v1_df[v1_df['Model Version'] == 'v1']
    

    # Initialize empty lists to store results
    groups = v1_df['Group'].unique()
    results = []

    one_group_only = False
    if ID == 'R1203' or ID == 'T1214':
        one_group_only = True

    # Loop through each group
    for group in groups:

        if not(one_group_only):

            # Get indices of max scores for each group, excluding groups where all scores are NaN
            v1_v1_indices = v1_df_by_model_v1.groupby('Group')[score].idxmax()

            # Filter out groups where idxmax returned NaN (all scores were NaN)
            v1_df_by_model_v1 = v1_df_by_model_v1.loc[v1_v1_indices.dropna()]

            v1_df_by_model_v1 = v1_df_by_model_v1.sort_values(by=score, ascending=False)

            # Get best scores for each version/model combination for this group
            v1_v1_group = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]

            v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0

            # Get model numbers for the best scores
            v1_v1_model_number = (
                v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
            )

            # Find the best overall score for this group
            if v1_v1_best != 0.0:  
                best_score = v1_v1_best
                best_source = 'v1_v1'
            else:
                best_score = 0.0
                best_source = 'v1_v1'
        else:
            v1_df_by_model_v1 = v1_df_by_model_v1.sort_values(by=score, ascending=False)

            # Get best scores for each version/model combination for this group
            v1_v1_group = v1_df_by_model_v1[v1_df_by_model_v1['Group'] == group]

            v1_v1_best = v1_v1_group[score].max() if len(v1_v1_group) > 0 else 0.0

            if v1_v1_best != 0.0:
                best_source = 'v1_v1'
                best_score = v1_v1_best
                v1_v1_model_number = (
                    v1_v1_group.loc[v1_v1_group[score].idxmax(), 'Model Number'] if len(v1_v1_group) > 0 else None
                )
            else:
                best_source = 'v1_v1'
                best_score = v1_v1_best


        cumulative_score = 0
        best_v1_ref = 0
        best_v1_ref_model_number = 0
        if best_source == 'v1_v1':
            cumulative_score = v1_v1_best
            best_v1_ref = v1_v1_best
            best_v1_ref_model_number = 'v1' + '_' + str(v1_v1_model_number)
        else:
            raise

        # Extract group number from group string (e.g., TS314 -> 314)
        group_number = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
        group_name = group_name_lookup.get(group_number, "Unknown").strip()

        v2_score_row = v2_df[(v2_df['Group'] == group) & (v2_df['Model Number'] == v1_v1_model_number)]
        v2_score = v2_score_row[score].values[0] if not v2_score_row.empty else None

        if v2_score is not None:
            cumulative_score += v2_score

        if cumulative_score > 0: # only include groups with a positive cumulative score
            # Store results
            results.append({
                'Group': group,
                'Group_Name': group_name,   
                'Combined_Score': cumulative_score,
                'Best_v1_ref': best_v1_ref,
                'Best_v2_ref': v2_score,
                'V1_Model_For_Combined_Score': group + '_' + best_v1_ref_model_number,
                'v1_v1_Score': v1_v1_best,
                'v1_v1_ModelNumber': v1_v1_model_number,
                'v2_v2_Score': v2_score,
                'v2_v2_ModelNumber': v2_score_row['Model Number'].values[0] if not v2_score_row.empty else None,
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    return results_df

def create_scatter(
    x,
    y,
    group_labels,
    xlabel,
    ylabel,
    title,
    legend_label='Submission Groups',
    main_xlim=None,
    main_ylim=None,
    inset=False,
    inset_position=[0.5, 0.05, 0.475, 0.475],
    inset_xlim=None,
    inset_ylim=None,
    inset_xticks=None,
    inset_yticks=None,
    highlight_inset_rect=False,
    rect_xy=None,
    rect_width=None,
    rect_height=None,
    adjust_texts=True,
    save_path=None,
    dpi=300,
    legend_position='upper right',
    score = None,
    xlim=None,           # New optional parameter for x-axis range
    ylim=None,           # New optional parameter for y-axis range
    xticks=None,         # New optional parameter for x-axis ticks
    yticks=None,         # New optional parameter for y-axis ticks
    text_fontsize=8,     # New optional parameter for text fontsize
    AF3_baseline=False,  # New optional parameter for AF3 baseline highlighting
    AF3_fill_between=True,  # New optional parameter to control fill_between for AF3 baseline
    show_group_labels=True,  # New optional parameter to control whether to show group text labels
    show_legend=True,    # New optional parameter to control whether to show legend
    ax=None,             # Optional parameter for existing axes object
    figsize=(10, 6),     # Figure size tuple
    diagonal_line_color='r',  # Color of diagonal y=x line
    diagonal_line_style='-',  # Style of diagonal y=x line  
    scatter_size=None,   # Scatter point size (None uses default)
    show_grid=False,     # Whether to show grid
    xlabel_fontsize=20,  # X-axis label font size
    ylabel_fontsize=20,  # Y-axis label font size
    title_fontsize=20,   # Title font size
    tick_labelsize=20    # Tick label size
):
    """
    Create a scatterplot with optional inset.
    Parameters:
        x, y: Data for scatterplot
        group_labels: Labels for each point
        xlabel, ylabel, title: Axis and plot labels
        legend_label: Label for legend
        main_xlim, main_ylim: Tuple for main plot axis limits
        inset: Whether to create an inset
        inset_position: [left, bottom, width, height] for inset axes
        inset_xlim, inset_ylim: Tuple for inset axis limits
        inset_xticks, inset_yticks: Ticks for inset axes
        highlight_inset_rect: Whether to draw a rectangle on main plot
        rect_xy: (x, y) for rectangle lower left
        rect_width, rect_height: Rectangle width and height
        adjust_texts: Whether to adjust text to avoid overlap
        save_path: If provided, save the figure to this path
        dpi: Dots per inch for saving
        legend_position: Position for the legend
        xlim, ylim: Explicit x/y axis range for main plot (overrides main_xlim/main_ylim if provided)
        xticks, yticks: Explicit x/y axis tick values for main plot
        text_fontsize: Font size for group label texts (default 8)
        AF3_fill_between: Whether to use fill_between for AF3 baseline highlighting (default True)
        show_group_labels: Whether to show group text labels on scatter points (default True)
        show_legend: Whether to show the legend (default True)
        ax: Optional existing axes object to plot on
        figsize: Tuple for figure size (default (10, 6))
        diagonal_line_color: Color of diagonal y=x line (default 'r')
        diagonal_line_style: Style of diagonal y=x line (default '-')
        scatter_size: Scatter point size (default None)
        show_grid: Whether to show grid (default False)
        xlabel_fontsize: X-axis label font size (default 20)
        ylabel_fontsize: Y-axis label font size (default 20)
        title_fontsize: Title font size (default 20)
        tick_labelsize: Tick label size (default 20)
    Returns:
        fig, ax_main, ax_inset (if inset=True)
    """

    # Use provided axes or create new ones
    if ax is not None:
        ax_main = ax
        fig = ax.figure
        ax_main.clear()  # Clear the existing axes
    else:
        fig, ax_main = plt.subplots(figsize=figsize)
    
    max_val = max(max(x), max(y))
    max_val_for_plotting = max_val
    if xlim is not None and ylim is not None:
        max_val_for_plotting = max(max_val, max(xlim), max(ylim))
    max_val = max(max_val, max_val_for_plotting)

    # Plot diagonal line - handle different styles
    if diagonal_line_color == 'black':
        # For black line, use [0, max_val] range
        ax_main.plot([0, max_val], [0, max_val], color=diagonal_line_color, linestyle=diagonal_line_style, label='y=x')
    else:
        # For other colors (like red), use [-100, 100] range
        ax_main.plot([-100, 100], [-100, 100], diagonal_line_color + diagonal_line_style, label='y=x')
    
    # Scatter plot with optional size parameter
    if scatter_size is not None:
        scatter = ax_main.scatter(x, y, c='blue', label=legend_label, s=scatter_size)
    else:
        scatter = ax_main.scatter(x, y, c='blue', label=legend_label)

    # --- AF3 Baseline Highlighting ---
    if AF3_baseline:
        for i, (xv, yv, txt) in enumerate(zip(x, y, group_labels)):
            group_num = str(int(''.join(filter(str.isdigit, str(txt))))).zfill(3)
            if group_num == '304':
                ax_main.axhline(yv, color='gray', linestyle='--', linewidth=2)
                ax_main.axvline(xv, color='gray', linestyle='--', linewidth=2)
                # Shade the area y > y_304 and x > x_304 (only if AF3_fill_between is True)
                if AF3_fill_between:
                    x_min, x_max = ax_main.get_xlim()
                    y_min, y_max = ax_main.get_ylim()
                    x_max += 0.05
                    y_max += 0.05
                    ax_main.fill_betweenx([yv, y_max], xv, x_max, color='yellow', alpha=0.2, zorder=0)
    # --- End AF3 Baseline Highlighting ---

    # Set axis bounds with padding for main plot if not provided
    if xlim is not None:
        ax_main.set_xlim(*xlim)
    elif main_xlim is None:
        x_min, x_max = min(x), max(x)
        padding = 0.05
        x_range = x_max - x_min
        main_xlim = (x_min - x_range * padding, x_max + x_range * padding)
        ax_main.set_xlim(*main_xlim)
    else:
        ax_main.set_xlim(*main_xlim)

    if ylim is not None:
        ax_main.set_ylim(*ylim)
    elif main_ylim is None:
        y_min, y_max = min(y), max(y)
        padding = 0.05
        y_range = y_max - y_min
        main_ylim = (y_min - y_range * padding, y_max + y_range * padding)
        ax_main.set_ylim(*main_ylim)
    else:
        ax_main.set_ylim(*main_ylim)

    if xticks is not None:
        ax_main.set_xticks(xticks)
    if yticks is not None:
        ax_main.set_yticks(yticks)

    ax_inset = None
    if inset:
        ax_inset = ax_main.inset_axes(inset_position)
        ax_inset.plot([-100, 100], [-100, 100], 'r-')
        ax_inset.scatter(x, y, c='blue')
        if inset_xlim:
            ax_inset.set_xlim(*inset_xlim)
        if inset_ylim:
            ax_inset.set_ylim(*inset_ylim)
        if inset_xticks:
            ax_inset.set_xticks(inset_xticks)
        if inset_yticks:
            ax_inset.set_yticks(inset_yticks)
        ax_inset.tick_params(labelsize=8)
        ax_inset.grid(True, linestyle='--', alpha=0.7)
        # Add rectangle in main plot to show zoomed region
        if highlight_inset_rect and rect_xy and rect_width and rect_height:
            rect = plt.Rectangle(rect_xy, rect_width, rect_height, fill=False, color='red', linestyle='--')
            ax_main.add_patch(rect)
        # --- AF3 Baseline Highlighting ---
        if AF3_baseline:
            for i, (xv, yv, txt) in enumerate(zip(x, y, group_labels)):
                group_num = str(int(''.join(filter(str.isdigit, str(txt))))).zfill(3)
                if group_num == '304':
                    ax_inset.axhline(yv, color='gray', linestyle='--', linewidth=2)
                    ax_inset.axvline(xv, color='gray', linestyle='--', linewidth=2)
                    # Shade the area y > y_304 and x > x_304 (only if AF3_fill_between is True)
                    if AF3_fill_between:
                        x_min, x_max = ax_inset.get_xlim()
                        y_min, y_max = ax_inset.get_ylim()
                        x_max += padding
                        y_max += padding
                        ax_inset.fill_betweenx([yv, y_max], xv, x_max, color='yellow', alpha=0.2, zorder=0)
        # --- End AF3 Baseline Highlighting ---

    # Add labels and adjust text for main plot and inset (only if show_group_labels is True)
    texts_main = []
    texts_inset = []
    if show_group_labels:
        for i, (xv, yv, txt) in enumerate(zip(x, y, group_labels)):
            txt = str(txt)
            if inset and inset_xlim and inset_ylim and (inset_xlim[0] <= xv <= inset_xlim[1] and inset_ylim[0] <= yv <= inset_ylim[1]):
                texts_inset.append(ax_inset.text(xv, yv, txt.replace('TS', ''), fontsize=text_fontsize))
            else:
                texts_main.append(ax_main.text(xv, yv, txt.replace('TS', ''), fontsize=text_fontsize))
        if adjust_texts:
            if texts_inset:
                adjust_text(texts_inset, 
                            ax=ax_inset, 
                            arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                            expand_points=(1.1, 1.1),
                            force_points=(0.1, 0.1))
            if texts_main:
                adjust_text(texts_main, 
                            ax=ax_main, 
                            arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                            expand_points=(2.0, 2.0),
                            force_text=(0.5, 0.5),
                            force_points=(0.5, 0.5),
                            avoid_text=True,
                            avoid_points=True,
                            avoid_self=True)
    ax_main.set_xlabel(xlabel, fontsize=xlabel_fontsize)
    ax_main.set_ylabel(ylabel, fontsize=ylabel_fontsize)
    ax_main.set_title(title, fontsize=title_fontsize)
    
    # Show grid if requested
    if show_grid:
        ax_main.grid(True, linestyle='--', alpha=0.7)
    
    # Show legend only if show_legend is True
    if show_legend:
        # Automatic legend placement to find best location with maximum white space
        legend = ax_main.legend(fontsize=16, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Try to find the best position automatically
        # This will place the legend in the location with the most white space
        ax_main.legend(fontsize=16, loc='best')
    
    ax_main.tick_params(axis='both', labelsize=tick_labelsize)
    
    if ax is None:  # Only call tight_layout if we created a new figure
        plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        if ax is None:  # Only close the figure if we created it
            plt.close(fig)
    if inset:
        return fig, ax_main, ax_inset
    else:
        return fig, ax_main

def create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, \
    output_dir = "./output/PLOTS", outfile_suffix = "", save_path = None,
    # New kwargs to reduce hardcoding
    per_group=0.35, min_size=6, max_size=20,  # Dynamic sizing parameters
    fig_width_horizontal=12, fig_width_vertical=None,  # Figure width overrides
    fig_height_horizontal=None, fig_height_vertical=10,  # Figure height overrides
    legend_loc_horizontal='lower right', legend_loc_vertical='upper right',  # Legend locations
    tick_fs_prim_horizontal=12, tick_fs_sec_horizontal=18,  # Font sizes for horizontal
    tick_fs_prim_vertical=12, tick_fs_sec_vertical=18,  # Font sizes for vertical
    rot_prim_horizontal=0, rot_prim_vertical=90,  # Rotation for primary axis
    v1_color='#1A80BB', v2_color='#EA801C',  # Default colors
    v1_color_304='#4F81BD', v2_color_304='#FFA500',  # Colors for group 304
    bar_size=0.9,  # Bar width/height
    edgecolor='black', linewidth=1,  # Bar edge styling
    show_edges=True,  # Whether to show bar edges
    xlabel='Submission Group', ylabel='Two-State Score',  # Axis labels
    title_prefix='Aggregate', title_suffix='scores for',  # Title components
    legend_fontsize=16, title_fontsize=18,  # Font sizes
    label_fontsize=18,  # Axis label font size
    spine_linewidth=3, spine_edgecolor='black',  # Spine styling
    baseline_color='green', baseline_linestyle='--', baseline_linewidth=4,  # Baseline styling
    baseline_label='AF3 Baseline Score',  # Baseline label
    star_marker='*', star_size=300, star_color='gray', star_edgecolor='black',  # Star styling
    star_offset_factor=0.02,  # Star offset as fraction of axis range
    score_column_v1='Best_v1_ref', score_column_v2='Best_v2_ref',  # Data columns
    single_state=False,  # Whether this is single-state (only v1)
    # Axis limits
    xlim=None, ylim=None,  # Axis limits (None for auto)
    # ID-specific overrides
    special_ids=None,  # Dict of special ID configurations
    # Score-specific overrides  
    special_scores=None,  # Dict of special score configurations
    # Composite score handling
    replace_updated=True,  # Whether to replace 'Updated_' in score names
    composite_score_4_replacement='Σ4'  # Replacement for Composite_Score_4
):
    import matplotlib.pyplot as plt
    
    # Handle score name replacements
    if replace_updated:
        score = score.replace('Updated_', '')
    if score == 'Composite_Score_4':
        score = composite_score_4_replacement
    
    # Handle special configurations
    if special_ids is None:
        special_ids = {}
    if special_scores is None:
        special_scores = {}
    
    # Get ID-specific overrides
    id_config = special_ids.get(ID, {})
    num_groups = len(combined_df)
    
    # Calculate dynamic size
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))
    
    # Determine figure size based on orientation and overrides
    if horizontal:
        fig_width = fig_width_horizontal if fig_width_horizontal is not None else 12
        fig_height = fig_height_horizontal if fig_height_horizontal is not None else dynamic_size
        fig_size = (fig_width, fig_height)
        bar_func, stack_param, line_func, line_param = plt.Axes.barh, 'left', plt.Axes.axvline, 'x'
        limit_set, label_prim, label_sec = plt.Axes.set_ylim, 'ylabel', 'xlabel'
        
        # Get legend and font settings for horizontal
        legend_loc = id_config.get('legend_loc_horizontal', legend_loc_horizontal)
        tick_fs_prim = id_config.get('tick_fs_prim_horizontal', tick_fs_prim_horizontal)
        tick_fs_sec = id_config.get('tick_fs_sec_horizontal', tick_fs_sec_horizontal)
        rot_prim = id_config.get('rot_prim_horizontal', rot_prim_horizontal)
    else:
        fig_width = fig_width_vertical if fig_width_vertical is not None else dynamic_size
        fig_height = fig_height_vertical if fig_height_vertical is not None else 10
        fig_size = (fig_width, fig_height)
        bar_func, stack_param, line_func, line_param = plt.Axes.bar, 'bottom', plt.Axes.axhline, 'y'
        limit_set, label_prim, label_sec = plt.Axes.set_xlim, 'xlabel', 'ylabel'
        
        # Get legend and font settings for vertical
        legend_loc = id_config.get('legend_loc_vertical', legend_loc_vertical)
        tick_fs_prim = id_config.get('tick_fs_prim_vertical', tick_fs_prim_vertical)
        tick_fs_sec = id_config.get('tick_fs_sec_vertical', tick_fs_sec_vertical)
        rot_prim = id_config.get('rot_prim_vertical', rot_prim_vertical)

    # Regular stacked bar logic
    fig, ax = plt.subplots(figsize=fig_size)
    group_labels_raw = combined_df['Group'].str.replace('TS', '')
    
    if horizontal:
        df_to_use = combined_df.iloc[::-1]
        group_name_lookup = get_group_name_lookup()
        group_labels, check_labels = [], []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_name} ({group_id})")
            check_labels.append(group_id)
        bar_size_param = 'height'
    else:
        df_to_use = combined_df
        group_labels = group_labels_raw
        check_labels = group_labels.values
        bar_size_param = 'width'
    
    # Set up colors
    v1_colors = [v1_color] * num_groups
    v2_colors = [v2_color] * num_groups if not single_state else []
    
    # Handle group 304 coloring
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        v1_colors[idx_304] = v1_color_304
        if not single_state:
            v2_colors[idx_304] = v2_color_304
    # Create bar kwargs
    if num_groups > 100:
        # For large numbers of groups, no edges
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<{score}> (V1)', 'color': v1_colors}
            if not single_state:
                bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<{score}> (V2)', 'color': v2_colors, stack_param: df_to_use[score_column_v1]}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<TM-score> (V1)', 'color': v1_colors}
            if not single_state:
                bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<TM-score> (V2)', 'color': v2_colors, stack_param: df_to_use[score_column_v1]}
    else:
        # For smaller numbers of groups, add edges if requested
        edge_kwargs = {}
        if show_edges:
            edge_kwargs = {'edgecolor': edgecolor, 'linewidth': linewidth}
        
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<{score}> (V1)', 'color': v1_colors, **edge_kwargs}
            if not single_state:
                bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<{score}> (V2)', 'color': v2_colors, stack_param: df_to_use[score_column_v1], **edge_kwargs}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<TM-score> (V1)', 'color': v1_colors, **edge_kwargs}
            if not single_state:
                bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<TM-score> (V2)', 'color': v2_colors, stack_param: df_to_use[score_column_v1], **edge_kwargs}
    
    # Create bars
    bars_v1 = bar_func(ax, group_labels, df_to_use[score_column_v1], **bar_kwargs_v1)
    if not single_state:
        bars_v2 = bar_func(ax, group_labels, df_to_use[score_column_v2], **bar_kwargs_v2)
    # Handle group 304 baseline and star
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        if single_state:
            total_score = df_to_use[score_column_v1].iloc[idx_304]
        else:
            total_score = df_to_use[score_column_v1].iloc[idx_304] + df_to_use[score_column_v2].iloc[idx_304]
        
        # Draw baseline
        line_func(ax, **{line_param: total_score, 'color': baseline_color, 'linestyle': baseline_linestyle, 
                        'linewidth': baseline_linewidth, 'label': baseline_label})
        
        if star:
            # Add star above (vertical) or to the right (horizontal) of the bar for group 304
            if horizontal:
                # y position is idx_304, x position is total_score
                ax.scatter(total_score + star_offset_factor * ax.get_xlim()[1], idx_304, 
                          marker=star_marker, s=star_size, color=star_color, edgecolor=star_edgecolor, zorder=5)
            else:
                # x position is idx_304, y position is total_score
                ax.scatter(idx_304, total_score + star_offset_factor * ax.get_ylim()[1], 
                          marker=star_marker, s=star_size, color=star_color, edgecolor=star_edgecolor, zorder=5)
    
    # Set axis limits and labels
    limit_set(ax, -0.5, len(group_labels) - 0.5)
    
    # Calculate maximum combined score for automatic limit setting
    if single_state:
        max_combined_score = df_to_use[score_column_v1].max()
    else:
        max_combined_score = (df_to_use[score_column_v1] + df_to_use[score_column_v2]).max()
    
    num_groups = len(group_labels)
    
    # Apply custom axis limits if provided, otherwise set automatic limits
    if horizontal:
        # For horizontal plots, xlim controls the score values (x-axis)
        if xlim is not None:
            ax.set_xlim(*xlim)
        else:
            # Set automatic xlim based on maximum combined score with some padding
            ax.set_xlim(0, max_combined_score * 1.1)
        ax.set_ylim(-0.5, num_groups - 0.5)
    else:
        # For vertical plots, ylim controls the score values (y-axis)
        if ylim is not None:
            ax.set_ylim(*ylim)
        else:
            # Set automatic ylim based on maximum combined score with some padding
            ax.set_ylim(0, max_combined_score * 1.1)
        ax.set_xlim(-0.5, num_groups - 0.5)

    getattr(ax, f'set_{label_prim}')(xlabel, fontsize=label_fontsize)
    getattr(ax, f'set_{label_sec}')(ylabel, fontsize=label_fontsize)
    
    # Set title
    if single_state:
        if score != "TMscore":
            ax.set_title(f'{title_prefix} {score} {title_suffix} \n {ID} V1 reference state', fontsize=title_fontsize)
        else:
            ax.set_title(f'{title_prefix} TM-scores {title_suffix} \n {ID} V1 reference state', fontsize=title_fontsize)
    else:
        if score != "TMscore":
            ax.set_title(f'{title_prefix} {score} {title_suffix} \n {ID} V1 and V2 reference states', fontsize=title_fontsize)
        else:
            ax.set_title(f'{title_prefix} TM-scores {title_suffix} \n {ID} V1 and V2 reference states', fontsize=title_fontsize)
    
    # Add legend
    ax.legend(loc=legend_loc, fontsize=legend_fontsize)
    
    # Set ticks and labels
    if horizontal:
        ax.set_yticks(range(len(group_labels)))
        ax.set_yticklabels(group_labels, fontsize=tick_fs_prim)
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=tick_fs_sec)
    else:
        ax.set_xticks(range(len(group_labels)))
        ax.set_xticklabels(group_labels, rotation=rot_prim, fontsize=tick_fs_prim)
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=tick_fs_sec)
    
    # Style
    plt.tight_layout()
    for spine in ax.spines.values():
        spine.set_linewidth(spine_linewidth)
        spine.set_edgecolor(spine_edgecolor)
    
    # Save
    if save_path:
        plt.savefig(save_path, dpi=300)
    else:
        if single_state:
            plt.savefig(f'{output_dir}/{ID}_{score}_single_state{outfile_suffix}.png', dpi=300)
        else:
            plt.savefig(f'{output_dir}/{ID}_{score}_two_state{outfile_suffix}.png', dpi=300)
    plt.close()

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)
    
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)

    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        if max(combined_df['Best_v1_ref']) <= 1:
            combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        if max(combined_df['Best_v2_ref']) <= 1:
            combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_two_state.csv', index=False)
    
    kwargs = {}
    # Set text fontsize for specific IDs
    if ID in ["M1239", "M1228"]:
        kwargs['text_fontsize'] = 12

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./output/PLOTS/{ID}_{score}_scatter_plot.png',
        'score': score
    })

    if score == 'TMscore':
        kwargs.update({
            'xlabel': f'TM-score (V1)',
            'ylabel': f'TM-score (V2)',
            'title': f'Scatter plot of Combined TM-score for \n {ID} V1 vs V2 reference states',
        })
    else:
        kwargs.update({
            'xlabel': f'{score} Score (V1)',
            'ylabel': f'{score} Score (V2)',
            'title': f'Scatter plot of Combined {score} scores for \n {ID} V1 vs V2 reference states',
        })

    if ID == 'R1203':
        kwargs.update({'AF3_baseline': True})

    # Special cases for insets and axis limits
    if ID == "T1228" and score == 'GlobalLDDT':
        kwargs.update({
            'inset': True,
            'inset_position': [0.2, 0.05, 0.475, 0.475],
            'inset_xlim': [0.74, 0.78],
            'inset_ylim': [0.70, 0.75],
            'inset_xticks': [0.74, 0.75, 0.76, 0.77, 0.78],
            'inset_yticks': [0.70, 0.72, 0.74, 0.75],
            'highlight_inset_rect': True,
            'rect_xy': (0.74, 0.70),
            'rect_width': 0.04,
            'rect_height': 0.05,
            'legend_position': 'upper left',
        })
    elif ID == "T1249" and score == "GlobalLDDT":
        kwargs.update({
            'inset': True,
            'inset_position': [0.25, 0.05, 0.475, 0.475],
            'inset_xlim': [0.74, 0.82],
            'inset_ylim': [0.70, 0.8],
            'inset_xticks': [0.74, 0.76, 0.78, 0.80, 0.82],
            'inset_yticks': [0.70, 0.72, 0.74, 0.76, 0.78, 0.80],
            'highlight_inset_rect': True,
            'rect_xy': (0.74, 0.70),
            'rect_width': 0.08,
            'rect_height': 0.1,
            'legend_position': 'upper left',
        })
    elif ID == "T1239" and score == "GlobalLDDT":
        kwargs.update({
            'inset': True,
            'inset_position': [0.25, 0.05, 0.475, 0.475],
            'inset_xlim': [0.66, 0.84],
            'inset_ylim': [0.72, 0.86],
            'inset_xticks': [0.66, 0.72, 0.78, 0.84],
            'inset_yticks': [0.72, 0.78, 0.84, 0.86],
            'highlight_inset_rect': True,
            'rect_xy': (0.66, 0.72),
            'rect_width': 0.18,
            'rect_height': 0.14,
            'legend_position': 'upper left',
        })
    elif ID == "R1203" and score == "GlobalLDDT":
        kwargs.update({
            'inset': True,
            'inset_position': [0.25, 0.05, 0.475, 0.475],
            'inset_xlim': [0.68, 0.84],
            'inset_ylim': [0.68, 0.84],
            'inset_xticks': [0.68, 0.74, 0.80, 0.84],
            'inset_yticks': [0.68, 0.74, 0.80, 0.84],
            'highlight_inset_rect': True,
            'rect_xy': (0.68, 0.68),
            'rect_width': 0.16,
            'rect_height': 0.16,
            'legend_position': 'upper left',
        })
    elif ID == "T1214" and score == "GlobalLDDT":
        kwargs.update({
            'inset': True,
            'inset_position': [0.25, 0.05, 0.475, 0.475],
            'inset_xlim': [0.78, 0.90],
            'inset_ylim': [0.78, 0.96],
            'inset_xticks': [0.78, 0.84, 0.90],
            'inset_yticks': [0.78, 0.84, 0.90, 0.96],
            'highlight_inset_rect': True,
            'rect_xy': (0.78, 0.78),
            'rect_width': 0.12,
            'rect_height': 0.18,
            'legend_position': 'upper left',
        })
    elif ID == "T1214" and score == "GDT_TS":
        kwargs.update({
            'inset': True,
            'inset_position': [0.25, 0.05, 0.475, 0.475],
            'inset_xlim': [88, 98],
            'inset_ylim': [90, 100],
            'inset_xticks': [88, 92, 96],
            'inset_yticks': [90, 94, 98],
            'highlight_inset_rect': True,
            'rect_xy': (88, 90),
            'rect_width': 10,
            'rect_height': 10,
            'legend_position': 'upper left',
        })
    elif ID == "T1214" and score == "TMscore":
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'inset': True,
            'inset_position': [0.25, 0.05, 0.475, 0.475],
            'inset_xlim': [.94, 1.00],
            'inset_ylim': [.94, 1.00],
            'inset_xticks': [.94, .96, .98, 1.00],
            'inset_yticks': [.94, .96, .98, 1.00],
            'highlight_inset_rect': True,
            'rect_xy': (.94, .94),
            'rect_width': .06,
            'rect_height': .06,
            'legend_position': 'upper left',
        })
    elif ID == "M1228" and score == "TMscore":
        kwargs.update({
            'main_xlim': (0.6, 0.8),
            'ylim': (0.65, 0.85),
            'xticks': [round(x, 2) for x in list(frange(0.6, 0.8+0.001, 0.05))],
            'yticks': [round(y, 2) for y in list(frange(0.65, 0.85+0.001, 0.05))],
            'AF3_baseline': True
        })
    elif ID == "M1228" and score == "GDT_TS":
        kwargs.update({
            'main_xlim': (10, 40),
            'ylim': (10, 40),
            'xticks': [round(x, 2) for x in list(frange(10, 40+0.001, 5))],
            'yticks': [round(y, 2) for y in list(frange(10, 40+0.001, 5))],
            'AF3_baseline': True
        })
    elif ID == "M1228" and score == "GlobDockQ":
        kwargs.update({
            'main_xlim': (0.20, 0.40),
            'ylim': (0.20, 0.40),
            'xticks': [round(x, 2) for x in list(frange(0.20, 0.40+0.001, 0.05))],
            'yticks': [round(y, 2) for y in list(frange(0.20, 0.40+0.001, 0.05))],
            'AF3_baseline': True
        })
    elif ID == "M1239" and score == "GDT_TS":
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xlim': (14, 32),
            'ylim': (14, 30),
            'xticks': [round(x, 2) for x in list(frange(14, 32+0.001, 2))],
            'yticks': [round(y, 2) for y in list(frange(14, 30+0.001, 2))],
        })
    elif ID == "M1239" and score == "GlobalLDDT":
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xlim': (0.35, 0.75),
            'ylim': (0.35, 0.75),
            'xticks': [round(x, 2) for x in list(frange(0.35, 0.75+0.001, 0.05))],
            'yticks': [round(y, 2) for y in list(frange(0.35, 0.75+0.001, 0.05))],
        })
    elif ID == "M1239" and score == "GlobDockQ":
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xlim': (0.15, 0.40),
            'ylim': (0.15, 0.40),
            'xticks': [round(x, 2) for x in list(frange(0.15, 0.40+0.001, 0.05))],
            'yticks': [round(y, 2) for y in list(frange(0.15, 0.40+0.001, 0.05))],
        })


    # Call create_scatter once with all kwargs
    result = create_scatter(**kwargs)


    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_vertical")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_horizontal")
    print(f"Done creating stacked bar plots for {ID} {score}")

if __name__ == "__main__":

    TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                        "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                        "R1203": ["GDT_TS", "GlobalLDDT", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3","Composite_Score_4", "TMscore"], 
                        "T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4"],
                        "T1228": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                        "T1239": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                        "T1249": ["AvgDockQ", "GlobalLDDT", "GDT_TS", "TMscore"]}

    for ID, scores in TARGET_SCORE_DICT.items():
        for score in scores:
            try:
                assessment(ID, score)
                print(f"[SUCCESS] Processed {ID} {score}")
            except Exception as e:
                print(f"[ERROR] Error processing {ID} {score}: {e}")
                raise Exception("Stop here")
                continue

