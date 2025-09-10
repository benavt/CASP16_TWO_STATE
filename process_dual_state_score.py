"""
MIT License

Copyright (c) 2025 Tiburon Leon Benavides

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Author: Tiburon Leon Benavides
Contribution: Main contributor
Date: 2025-09-10
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
    file = f'./DATA/{ID}_v1_{score}_scores.csv'
    df = pd.read_csv(file)
    if ID == "T1214":
        df['Model Version'] = 'v1'
    df = df.dropna()
    return df

def get_v2_ref_df(ID, score):
    version = 'v2'
    if ID == "T1228":
        version = 'v1_1'
        if not(exists(f'./DATA/{ID}_{version}_{score}_scores.csv')):
            version = 'v2_1'
    elif ID == "T1239":
        version = 'v1_1'

    file = f'./DATA/{ID}_{version}_{score}_scores.csv'
    df = pd.read_csv(file)
    if ID == "T1214":
        df['Model Version'] = 'v2'
    df = df.dropna()
    return df

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

def create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = ""):
    score = score.replace('Updated_','')
    if score == 'Composite_Score_4':
        score = 'Σ4'
    import matplotlib.pyplot as plt
    num_groups = len(combined_df)
    per_group, min_size, max_size = 0.35, 6, 20
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))

    if horizontal:
        if ID != "M1228" and ID != "R1203":
            fig_size = (dynamic_size, 12)
        elif ID == "R1203" and score == "Σ4":
            fig_size = (20, 12)
        else:
            fig_size = (10, 15)
        bar_func, stack_param, line_func, line_param = plt.Axes.bar, 'bottom', plt.Axes.axvline, 'x'
        limit_set, label_prim, label_sec = plt.Axes.set_xlim, 'xlabel', 'ylabel'

        if ID != "M1228" and ID != "R1203":
            if ID == "T1214":
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 18, 24, 90
            else:
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 24, 32, 90
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 24, 32, 90
    else:
        if ID != "M1228" and ID != "R1203":
            fig_size = (12, dynamic_size)
        elif ID == "R1203" and score == "Composite_Score_4":
            fig_size = (25, 12)
        else:
            fig_size = (15, 10)
        bar_func, stack_param, line_func, line_param = plt.Axes.barh, 'left', plt.Axes.axhline, 'y'
        limit_set, label_prim, label_sec = plt.Axes.set_ylim, 'ylabel', 'xlabel'
        if ID != "M1228":
            if ID == "T1214":
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 18, 24, 0
            else:
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 24, 32, 0
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 32, 32, 0
    
    fig, ax = plt.subplots(figsize=fig_size)
    group_labels_raw = combined_df['Group'].str.replace('TS', '')
    if horizontal:
        df_to_use = combined_df
        group_labels = group_labels_raw
        check_labels = group_labels.values
        bar_size_param, bar_size = 'width', 0.9
    else:
        df_to_use = combined_df.iloc[::-1]
        group_name_lookup = get_group_name_lookup()
        group_labels, check_labels = [], []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_name} ({group_id})")
            check_labels.append(group_id)
        bar_size_param, bar_size = 'height', 0.9
    v1_colors = ['tab:blue'] * num_groups
    v2_colors = ['#FA7E0F'] * num_groups
    
    # # Color group 304 bars with teal
    # if '304' in check_labels:
    #     idx_304 = list(check_labels).index('304')
    #     v1_colors[idx_304] = 'cyan'
    #     v2_colors[idx_304] = 'yellow'

    if num_groups > 100:

        if score != "TMscore":  
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'{score} (V1)', 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'{score} (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'TM-score (V1)', 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'TM-score (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    else:
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'{score} (V1)','color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'{score} (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'TM-score (V1)','color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'TM-score (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    bars_v1 = bar_func(ax, group_labels, df_to_use[f'Best_v1_ref'], **bar_kwargs_v1)
    bars_v2 = bar_func(ax, group_labels, df_to_use[f'Best_v2_ref'], **bar_kwargs_v2)
    
    # Add star above group 304 bar
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        total_score = df_to_use[f'Best_v1_ref'].iloc[idx_304] + df_to_use[f'Best_v2_ref'].iloc[idx_304]
        print("Total score for 304: ", total_score)
        
        # Calculate position for the star
        if horizontal:
            # For horizontal bars (vertical bars), star goes above the bar
            star_x = idx_304
            star_y = total_score + 1  # Slightly above the bar
            ax.plot(star_x, star_y, 'k*', markersize=15, markeredgecolor='black', markerfacecolor='yellow')
            # Draw horizontal line at y position of group 304
            ax.axhline(y=total_score, color='grey', linestyle='--', linewidth=4, label='AF3 Score')
        else:
            # For vertical bars (horizontal bars), star goes above the bar
            star_x = total_score + 1  # Slightly to the right of the bar
            star_y = idx_304
            ax.plot(star_x, star_y, 'k*', markersize=15, markeredgecolor='black', markerfacecolor='yellow')
            # Draw vertical line at x position of group 304
            ax.axvline(x=total_score, color='grey', linestyle='--', linewidth=4, label='AF3 Score')
    limit_set(ax, -0.5, len(group_labels) - 0.5)
    getattr(ax, f'set_{label_prim}')('Group', fontsize= 32)
    getattr(ax, f'set_{label_sec}')('Dual-State Score', fontsize=32)
    if score != "TMscore":
        ax.set_title(f'Dual-State {score} scores for \n {ID} V1 and V2 reference states', fontsize=18)
    else:
        ax.set_title(f'Dual-State TM-scores for \n {ID} V1 and V2 reference states', fontsize=14)
    if ID != 'T1214':
        if ID != "M1228":
            ax.legend(loc=legend_loc, fontsize=28)
        else:
            ax.legend(loc=legend_loc, fontsize=14)
    if horizontal:
        ax.set_xticks(range(len(group_labels)))
        ax.set_xticklabels(group_labels, rotation=rot_prim, fontsize=tick_fs_prim)
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=tick_fs_sec)
    else:
        ax.set_yticks(range(len(group_labels)))
        ax.set_yticklabels(group_labels, fontsize=tick_fs_prim)
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=tick_fs_sec)
    plt.tight_layout()
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_edgecolor('black')
    plt.savefig(f'./PLOTS/{ID}_{score}_dual_state{outfile_suffix}.png', dpi=300)
    plt.close()


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
    AF3_baseline=False   # New optional parameter for AF3 baseline highlighting
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
    Returns:
        fig, ax_main, ax_inset (if inset=True)
    """

    fig, ax_main = plt.subplots(figsize=(10, 6))
    max_val = max(max(x), max(y))
    max_val_for_plotting = max_val
    if xlim is not None and ylim is not None:
        max_val_for_plotting = max(max_val, max(xlim), max(ylim))
    max_val = max(max_val, max_val_for_plotting)

    ax_main.plot([-100, 100], [-100, 100], 'r-', label='y=x')
    scatter = ax_main.scatter(x, y, c='blue', label=legend_label)

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
                    # Shade the area y > y_304 and x > x_304
                    x_min, x_max = ax_inset.get_xlim()
                    y_min, y_max = ax_inset.get_ylim()
                    x_max += padding
                    y_max += padding
                    ax_inset.fill_betweenx([yv, y_max], xv, x_max, color='yellow', alpha=0.2, zorder=0)
        # --- End AF3 Baseline Highlighting ---

    # Add labels and adjust text for main plot and inset
    texts_main = []
    texts_inset = []
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
    ax_main.set_xlabel(xlabel, fontsize=20)
    ax_main.set_ylabel(ylabel, fontsize=20)
    ax_main.set_title(title, fontsize=20)
    
    # Automatic legend placement to find best location with maximum white space
    legend = ax_main.legend(fontsize=16, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Try to find the best position automatically
    # This will place the legend in the location with the most white space
    ax_main.legend(fontsize=16, loc='best')
    
    ax_main.tick_params(axis='both', labelsize=20)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    if inset:
        return fig, ax_main, ax_inset
    else:
        return fig, ax_main


def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)

    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)

    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
        combined_df['v1_v1_Score'] = combined_df['v1_v1_Score'] * 100
        combined_df['v2_v2_Score'] = combined_df['v2_v2_Score'] * 100
        combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./OUTPUT/{ID}_{score}_dual_state.csv', index=False)
    

    # print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_vertical_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_horizontal_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_vertical_no_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_horizontal_no_star")
    
    kwargs = {}
    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS/{ID}_{score}_scatter_plot_dual_state.png',
        'score': score,
        'xlabel': f'{score} (V1)',
        'ylabel': f'{score} (V2)',
        'title': f'{ID} {score} Dual-State Score',})
    
    if ID == 'T1214' and score == 'TMscore':
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xticks': [0.80, 0.85, 0.90, 0.95, 1.00],
            'inset': True,
            'inset_position': [0.2, 0.05, 0.4, 0.4],
            'inset_xlim': [0.98, 1.00],
            'inset_ylim': [0.97, 0.99],
            'inset_xticks': [0.98, 0.99, 1.00],
            'inset_yticks': [0.97, 0.98, 0.99],
            'highlight_inset_rect': True,
            'rect_xy': (0.98, 0.97),
            'rect_width': 0.02,
            'rect_height': 0.02,
            'legend_position': 'upper left',
        })
    elif ID == 'T1214' and score == 'GDT_TS':
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xlim': (60, 100),
            'ylim': (60, 100),
            'xticks': [60, 70, 80, 90, 100],
            'yticks': [60, 70, 80, 90, 100],
            'inset': True,
            'inset_position': [0.2, 0.05, 0.4, 0.6],
            'inset_xlim': [92, 96],
            'inset_ylim': [90, 96],
            'inset_xticks': [92, 94, 96],
            'inset_yticks': [90, 92, 94, 96],
            'highlight_inset_rect': True,
            'rect_xy': (92, 90),
            'rect_width': 4,
            'rect_height': 6,
            'legend_position': 'upper left',
        })
    elif ID == 'T1214' and score == 'GlobalLDDT':
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'inset': True,
            'inset_position': [0.05, 0.4, 0.4, 0.4],
            'inset_xlim': [.82, .86],
            'inset_ylim': [.8, .84],
            'inset_xticks': [.82, .84, .86],
            'inset_yticks': [.80, .82, .84],
            'highlight_inset_rect': True,
            'rect_xy': (.82, .80),
            'rect_width': .04,
            'rect_height': .04,
            'legend_position': 'upper left',
        })
    create_scatter(**kwargs)
    print(f"Done creating stacked bar plots for {ID} {score}")

TARGET_SCORE_DICT = {"T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4"]}


for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            raise Exception("Stop here")
            continue



