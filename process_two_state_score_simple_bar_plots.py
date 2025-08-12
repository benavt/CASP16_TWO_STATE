import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv

def frange(start, stop, step):
    vals = []
    while start <= stop:
        vals.append(start)
        start += step
    return vals

def get_v1_ref_df(ID, score):
    file = f'./DATA/{ID}_v1_{score}_scores.csv'
    df = pd.read_csv(file)
    return df

def get_v2_ref_df(ID, score):
    version = 'v2'
    if ID == "T1228":
        version = 'v2_1'
    elif ID == "T1239":
        version = 'v1_1'

    file = f'./DATA/{ID}_{version}_{score}_scores.csv'
    df = pd.read_csv(file)
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
    if 'Model Version' not in v1_df.columns or 'Model Version' not in v2_df.columns:
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

def create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = ""):
    score = score.replace('Updated_','')
    if score == 'Composite_Score_4':
        score = 'Σ4'
    import matplotlib.pyplot as plt
    num_groups = len(combined_df)
    per_group, min_size, max_size = 0.35, 6, 20
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))
    if horizontal:
        fig_size = (12, dynamic_size)
        bar_func, stack_param, line_func, line_param = plt.Axes.barh, 'left', plt.Axes.axvline, 'x'
        limit_set, label_prim, label_sec = plt.Axes.set_ylim, 'ylabel', 'xlabel'
        legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 24, 32, 0
    else:
        fig_size = (dynamic_size, 10)
        bar_func, stack_param, line_func, line_param = plt.Axes.bar, 'bottom', plt.Axes.axhline, 'y'
        limit_set, label_prim, label_sec = plt.Axes.set_xlim, 'xlabel', 'ylabel'
        legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 24, 32, 90
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
    v1_colors = ['tab:blue'] * num_groups
    v2_colors = ['#FA7E0F'] * num_groups

    if num_groups > 100:
        bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'{score} (V1)', 'color': v1_colors}
        bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'{score} (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    else:
        bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'{score} (V1)','color': v1_colors}
        bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'{score} (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    bars_v1 = bar_func(ax, group_labels, df_to_use[f'Best_v1_ref'], **bar_kwargs_v1)
    bars_v2 = bar_func(ax, group_labels, df_to_use[f'Best_v2_ref'], **bar_kwargs_v2)
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        total_score = df_to_use[f'Best_v1_ref'].iloc[idx_304] + df_to_use[f'Best_v2_ref'].iloc[idx_304]
        line_func(ax, **{line_param: total_score, 'color': 'grey', 'linestyle': '--', 'linewidth': 4, 'label': 'AF3 Score'})
        if star:
            # Add a gray star above (vertical) or to the right (horizontal) of the bar for group 304
            if horizontal:
                # y position is idx_304, x position is total_score
                ax.scatter(total_score + 0.02 * ax.get_xlim()[1], idx_304, marker='*', s=300, color='gray', edgecolor='black', zorder=5)
            else:
                # x position is idx_304, y position is total_score
                ax.scatter(idx_304, total_score + 0.02 * ax.get_ylim()[1], marker='*', s=300, color='gray', edgecolor='black', zorder=5)
    limit_set(ax, -0.5, len(group_labels) - 0.5)
    getattr(ax, f'set_{label_prim}')('Group', fontsize= 32)
    getattr(ax, f'set_{label_sec}')('Two-State Score', fontsize=32)
    ax.set_title(f'Two-State {score} scores for \n {ID} V1 and V2 reference states', fontsize=18)
    ax.legend(loc=legend_loc, fontsize=28)
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
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./OUTPUT/{ID}_{score}_two_state.csv', index=False)
  

    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_vertical_simple")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_horizontal_simple")
    print(f"Done creating stacked bar plots for {ID} {score}")



TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "R1203": ["GDT_TS", "GlobalLDDT", "Updated_Composite_Score_4", "TMscore"], 
                     "T1214": ["GDT_TS", "GlobalLDDT"],
                     "T1228": ["GDT_TS", "GlobalLDDT"], 
                     "T1239": ["GDT_TS", "GlobalLDDT"], 
                     "T1249": ["AvgDockQ", "GlobalLDDT", "GDT_TS", "TMscore"]}

for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            continue

