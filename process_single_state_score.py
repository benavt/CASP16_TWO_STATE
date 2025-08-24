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


def get_group_name_lookup():
    lookup = {}
    with open('group_number_name_correspondance.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lookup[row['Group Number'].zfill(3)] = row['Group Name']
    return lookup   


def get_best_fit(ID, v1_df, score):
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
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 18, 18, 0
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 18, 18, 0
    else:
        fig_size = (dynamic_size, 10)
        bar_func, stack_param, line_func, line_param = plt.Axes.bar, 'bottom', plt.Axes.axhline, 'y'
        limit_set, label_prim, label_sec = plt.Axes.set_xlim, 'xlabel', 'ylabel'
        if ID != "M1228":
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 18, 18, 90
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 18, 18, 90
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
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        v1_colors[idx_304] = 'cyan' 
    if num_groups > 100:
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<{score.replace('Updated_','')}> (V1)', 'color': v1_colors}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<TM-score> (V1)', 'color': v1_colors}
    else:
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<{score.replace('Updated_','')}> (V1)', 'edgecolor': 'black', 'linewidth': 1, 'color': v1_colors}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'<TM-score> (V1)', 'edgecolor': 'black', 'linewidth': 1, 'color': v1_colors}
    bars_v1 = bar_func(ax, group_labels, df_to_use[f'Best_v1_ref'], **bar_kwargs_v1)
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        total_score = df_to_use[f'Best_v1_ref'].iloc[idx_304]
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
    plt.savefig(f'./PLOTS/{ID}_{score}_single_state{outfile_suffix}.png', dpi=300)
    plt.close()

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, score)

    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)

    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./OUTPUT/{ID}_{score}_single_state.csv', index=False)
    

    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_vertical_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_horizontal_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_vertical_no_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_horizontal_no_star")
    print(f"Done creating stacked bar plots for {ID} {score}")



TARGET_SCORE_DICT = {"T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_4"]}

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

