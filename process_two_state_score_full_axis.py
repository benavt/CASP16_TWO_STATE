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
from process_two_state_score import get_v1_ref_df, get_v2_ref_df


def frange(start, stop, step):
    vals = []
    while start <= stop:
        vals.append(start)
        start += step
    return vals

def get_group_name_lookup():
    lookup = {}
    with open('group_number_name_correspondance.csv', newline='') as csvfile:
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
    text_fontsize=12,     # New optional parameter for text fontsize
    AF3_baseline=False,   # New optional parameter for AF3 baseline highlighting
    ax=None              # Optional parameter for existing axes object
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
        text_fontsize: Font size for group label texts (default 12)
        AF3_baseline: Whether to highlight AF3 baseline (default False)
        ax: Optional existing axes object to plot on (default None)
    Returns:
        fig, ax_main, ax_inset (if inset=True)
    """

    # Use provided axes or create new ones
    if ax is not None:
        ax_main = ax
        fig = ax.figure
        ax_main.clear()  # Clear the existing axes
    else:
        fig, ax_main = plt.subplots(figsize=(8, 8))
    
    max_val = max(max(x), max(y))
    max_val_for_plotting = max_val
    if xlim is not None and ylim is not None:
        max_val_for_plotting = max(max_val, max(xlim), max(ylim))
    max_val = max(max_val, max_val_for_plotting)

    ax_main.plot([0, max_val], [0, max_val], color='black', linestyle='--', label='y=x')
    scatter = ax_main.scatter(x, y, c='blue', label=legend_label, s=100)

    # --- AF3 Baseline Highlighting ---
    if AF3_baseline:
        for i, (xv, yv, txt) in enumerate(zip(x, y, group_labels)):
            group_num = str(int(''.join(filter(str.isdigit, str(txt))))).zfill(3)
            if group_num == '304':
                ax_main.axhline(yv, color='gray', linestyle='--', linewidth=2)
                ax_main.axvline(xv, color='gray', linestyle='--', linewidth=2)
                # Shade the area y > y_304 and x > x_304
                x_min, x_max = ax_main.get_xlim()
                y_min, y_max = ax_main.get_ylim()
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
  
    ax_main.set_xlabel(xlabel, fontsize=30)
    ax_main.set_ylabel(ylabel, fontsize=30)
    ax_main.set_title(title, fontsize=20)
    
    # Add grid with dashed lines at each x-tick and y-tick
    ax_main.grid(True, linestyle='--', alpha=0.7)
    
    ax_main.tick_params(axis='both', labelsize=25)
    if ax is None:  # Only call tight_layout if we created a new figure
        plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        if ax is None:  # Only close the figure if we created it
            plt.close(fig)

    return fig, ax_main

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        if max(combined_df['Best_v1_ref']) < 1:
            combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        if max(combined_df['Best_v2_ref']) < 1:
            combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./OUTPUT/{ID}_{score}_two_state.csv', index=False)
    
    kwargs = {}
    # Set text fontsize for specific IDs
    if ID in ["M1239", "M1228"]:
        kwargs['text_fontsize'] = 16
    if score == 'TMscore':
        label = 'TM-score'
    else:
        label = score

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'xlabel': f'{label} (V1)',
        'ylabel': f'{label} (V2)',
        'title': f'{ID} {label}',
        'save_path': f'./PLOTS/{ID}_{score}_scatter_plot_full_axis.png',
        'score': score
    })

    if score == 'TMscore':
        kwargs.update({
            'xlim': (0.0, 1.0),
            'ylim': (0.0, 1.0),
            'xticks': [0.0, 0.5, 1.0],
            'yticks': [0.0, 0.5, 1.0],
        })
    elif score == 'GDT_TS':
        kwargs.update({
            'xlim': (0.0, 100.0),
            'ylim': (0.0, 100.0),
            'xticks': [0, 50, 100],
            'yticks': [0, 50, 100],
        })
    # Call create_scatter once with all kwargs
    result = create_scatter(**kwargs)
    return

TARGET_SCORE_DICT = {"M1228": ["GDT_TS", "TMscore"], 
                     "M1239": ["GDT_TS", "TMscore"], 
                     "R1203": ["GDT_TS", "TMscore"], 
                     "T1228": ["GDT_TS", "TMscore"], 
                     "T1239": ["GDT_TS", "TMscore"],
                     "T1249": ["GDT_TS", "TMscore"],
                     "T1214": ["GDT_TS", "TMscore"]}


for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            raise Exception("Stop here")
            continue

