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

def calc_TSBI_score(v1_ref, v2_ref):
    if v1_ref == 0 or v2_ref == 0:  
        return 0, -1
    balance = 1 - abs(v1_ref - v2_ref) / (v1_ref + v2_ref)
    tsbi = balance * (v1_ref + v2_ref)
    return balance, tsbi

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
        (
            ('Model Version' in v1_df.columns and (v1_df['Model Version'].isna().all() or (v1_df['Model Version'] == 'N/A').all())) and
            ('Model Version' in v2_df.columns and (v2_df['Model Version'].isna().all() or (v2_df['Model Version'] == 'N/A').all()))
        )
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
        balance, TSBI_score = calc_TSBI_score(best_v1_ref, best_v2_ref)
        # print(f"Group: {group}, Balance: {balance}, TSBI_score: {TSBI_score}")
        if cumulative_score > 0: # only include groups with a positive cumulative score
            # Store results
            results.append({
                'Group': group,
                'Group_Name': group_name,
                'TSBI_Score': TSBI_score,
                'Balance': balance,
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
    import matplotlib.pyplot as plt

    # Use TSBI_Score for the bar plot
    if 'TSBI_Score' not in combined_df.columns:
        raise ValueError("TSBI_Score column not found in combined_df.")

    # Sort by TSBI_Score descending for correct bar order
    df_to_use = combined_df.sort_values(by='TSBI_Score', ascending=False).reset_index(drop=True)
    num_groups = len(df_to_use)
    per_group, min_size, max_size = 0.35, 6, 20
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))

    # Prepare group labels (show group name and number if available)
    group_name_lookup = get_group_name_lookup()

    # Set TSBI_Score == -1 to 0 for plotting
    tsbi_scores_for_plot = df_to_use['TSBI_Score'].copy()
    tsbi_scores_for_plot = tsbi_scores_for_plot.apply(lambda x: 0 if x == -1 else x)

    # Plotting
    if horizontal:
        group_labels = []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_id}")

        # Reverse the order of the data for plotting
        fig, ax = plt.subplots(figsize=(dynamic_size, 12))
        # Reverse the order of the data
        x_pos = range(num_groups)
        bars = ax.bar(x_pos, tsbi_scores_for_plot, color='#1A80BB')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(group_labels, rotation=90, fontsize=14)
        ax.set_ylabel('TSBI Score', fontsize=18)
        ax.set_xlabel('Submission Group', fontsize=18)
        ax.set_ylim(bottom=0)
    else:
        group_labels = []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_name} ({group_id})")

        fig, ax = plt.subplots(figsize=(12, dynamic_size))
        # Order bars in decreasing order of TSBI_Score (already sorted above)
        y_pos = range(num_groups)
        tsbi_scores_for_plot_reversed = tsbi_scores_for_plot[::-1]
        bars = ax.barh(y_pos, tsbi_scores_for_plot_reversed, color='#1A80BB')
        group_labels_reversed = group_labels[::-1]
        ax.set_yticks(y_pos)
        ax.set_yticklabels(group_labels_reversed, fontsize=14)
        ax.set_xlabel('TSBI Score', fontsize=18)
        ax.set_ylabel('Submission Group', fontsize=18)
        ax.set_xlim(left=0)

    # Highlight AF3-server (group 304) if present
    if '304' in [str(int(''.join(filter(str.isdigit, g)))).zfill(3) for g in df_to_use['Group']]:
        idx_304 = None
        for idx, group in enumerate(df_to_use['Group']):
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            if group_id == '304':
                idx_304 = idx
                break
        if not(horizontal):
            idx_304 = num_groups - idx_304 - 1
        if idx_304 is not None:
            if horizontal:
                bars[idx_304].set_color('#4F81BD')
            else:
                bars[idx_304].set_color('#4F81BD')
            if star:
                # Add a gray star above (vertical) or to the right (horizontal) of the bar for group 304
                if horizontal:
                    ax.scatter(idx_304, tsbi_scores_for_plot.iloc[idx_304] + 0.02 * ax.get_ylim()[1], marker='*', s=300, color='gray', edgecolor='black', zorder=5)
                else:
                    ax.scatter(tsbi_scores_for_plot_reversed.iloc[idx_304] + 0.02 * ax.get_xlim()[1], idx_304, marker='*', s=300, color='gray', edgecolor='black', zorder=5)

                    
    # Title
    ax.set_title(f'TSBI Score for {ID}', fontsize=20)

    # Style
    plt.tight_layout()
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_edgecolor('black')

    plt.savefig(f'./TSBI_PLOTS/{ID}_{score}_TSBI_bar{outfile_suffix}.png', dpi=300)
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

    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_vertical_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_horizontal_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_vertical_no_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_horizontal_no_star")
    print(f"Done creating stacked bar plots for {ID} {score}")



TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "R1203": ["GDT_TS", "GlobalLDDT", "Composite_Score_4", "TMscore"], 
                     "T1214": ["GDT_TS", "GlobalLDDT", "Composite_Score_4"],
                     "T1228": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1239": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1249": ["AvgDockQ", "GlobalLDDT", "GDT_TS", "TMscore"]}


for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        print(f"Processing {ID} {score}")
        assessment(ID, score)
        print(f"[SUCCESS] Processed {ID} {score}")
        

