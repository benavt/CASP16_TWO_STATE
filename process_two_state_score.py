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

def create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = ""):
    import matplotlib.pyplot as plt
    num_groups = len(combined_df)
    per_group, min_size, max_size = 0.35, 6, 20
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))
    if horizontal:
        fig_size = (12, dynamic_size)
        bar_func, stack_param, line_func, line_param = plt.Axes.barh, 'left', plt.Axes.axvline, 'x'
        limit_set, label_prim, label_sec = plt.Axes.set_ylim, 'ylabel', 'xlabel'
        if ID != "M1228":
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 12, 18, 0
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 16, 20, 0
    else:
        fig_size = (dynamic_size, 10)
        bar_func, stack_param, line_func, line_param = plt.Axes.bar, 'bottom', plt.Axes.axhline, 'y'
        limit_set, label_prim, label_sec = plt.Axes.set_xlim, 'xlabel', 'ylabel'
        if ID != "M1228":
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 12, 18, 90
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 16, 20, 90
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
        bar_size_param, bar_size = 'height', 0.9
    else:
        df_to_use = combined_df
        group_labels = group_labels_raw
        check_labels = group_labels.values
        bar_size_param, bar_size = 'width', 0.9
    v1_colors = ['#1A80BB'] * num_groups
    v2_colors = ['#EA801C'] * num_groups
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        if not star:
            v1_colors[idx_304] = '#4F81BD'  # bluish
            v2_colors[idx_304] = '#FFA500'  # orangish
    if num_groups > 100:
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<{score.replace('Updated_','')}> (V1)', 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<{score.replace('Updated_','')}> (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<TM-score> (V1)', 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<TM-score> (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    else:
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<{score.replace('Updated_','')}> (V1)', 'edgecolor': 'black', 'linewidth': 1, 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<{score.replace('Updated_','')}> (V2)', 'edgecolor': 'black', 'linewidth': 1, 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<TM-score> (V1)', 'edgecolor': 'black', 'linewidth': 1, 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'<TM-score> (V2)', 'edgecolor': 'black', 'linewidth': 1, 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    bars_v1 = bar_func(ax, group_labels, df_to_use[f'Best_v1_ref'], **bar_kwargs_v1)
    bars_v2 = bar_func(ax, group_labels, df_to_use[f'Best_v2_ref'], **bar_kwargs_v2)
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        total_score = df_to_use[f'Best_v1_ref'].iloc[idx_304] + df_to_use[f'Best_v2_ref'].iloc[idx_304]
        line_func(ax, **{line_param: total_score, 'color': 'green', 'linestyle': '--', 'linewidth': 4, 'label': 'AF3 Baseline Score'})
        if star:
            # Add a gray star above (vertical) or to the right (horizontal) of the bar for group 304
            if horizontal:
                # y position is idx_304, x position is total_score
                ax.scatter(total_score + 0.02 * ax.get_xlim()[1], idx_304, marker='*', s=300, color='gray', edgecolor='black', zorder=5)
            else:
                # x position is idx_304, y position is total_score
                ax.scatter(idx_304, total_score + 0.02 * ax.get_ylim()[1], marker='*', s=300, color='gray', edgecolor='black', zorder=5)
    limit_set(ax, -0.5, len(group_labels) - 0.5)
    getattr(ax, f'set_{label_prim}')('Submission Group', fontsize=18)
    getattr(ax, f'set_{label_sec}')('Two-State Score', fontsize=18)
    if score != "TMscore":
        ax.set_title(f'Aggregate {score.replace('Updated_','')} scores for \n {ID} V1 and V2 reference states', fontsize=18)
    else:
        ax.set_title(f'Aggregate TM-scores for \n {ID} V1 and V2 reference states', fontsize=18)
    ax.legend(loc=legend_loc, fontsize=16)
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
    plt.tight_layout()
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_edgecolor('black')
    plt.savefig(f'./PLOTS/{ID}_{score}_two_state{outfile_suffix}.png', dpi=300)
    plt.close()

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
        kwargs['text_fontsize'] = 12

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS/{ID}_{score}_scatter_plot.png',
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
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_vertical_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_horizontal_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_vertical_no_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_horizontal_no_star")
    print(f"Done creating stacked bar plots for {ID} {score}")



TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "R1203": ["GDT_TS", "GlobalLDDT", "Composite_Score_4", "TMscore"], 
                     "T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_4"],
                     "T1228": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1239": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1249": ["AvgDockQ", "GlobalLDDT", "GDT_TS", "TMscore"]}

assessment("R1203", "Composite_Score_4")
assessment("T1214", "Composite_Score_4")
raise Exception("Stop here")

for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            continue

