import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv

from process_two_state_score_full_axis import create_scatter

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


TARGET_SCORE_DICT = {"M1228": ["GDT_TS", "TMscore"], 
                     "M1239": ["GDT_TS", "TMscore"], 
                     "T1249": ["GDT_TS", "TMscore"], 
                     "T1228": ["GDT_TS", "TMscore"], 
                     "T1239": ["GDT_TS", "TMscore"],
                     "R1203": ["GDT_TS", "TMscore"],
                     }

def assessment(TARGET_SCORE_DICT):

    TARGET_SCORE_df_dict = {}
    for ID, scores in TARGET_SCORE_DICT.items():
        for score in scores:
            try:
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
                TARGET_SCORE_df_dict[ID+'_'+score] = combined_df
                print(f"[SUCCESS] Processed {ID} {score}")
            except Exception as e:
                TARGET_SCORE_df_dict[ID+'_'+score] = None
                print(f"[ERROR] Error processing {ID} {score}: {e}")
                continue

    order_of_id_scores = ['M1228_TMscore', 'T1228_TMscore', 'M1228_GDT_TS', 'T1228_GDT_TS', 
                          'M1239_TMscore', 'T1239_TMscore', 'M1239_GDT_TS', 'T1239_GDT_TS', 
                          'T1249_TMscore', 'R1203_TMscore', 'T1249_GDT_TS', 'R1203_GDT_TS']


    # INSERT_YOUR_CODE
    # Create a multi-panel figure with 3 rows and 4 columns of subplots
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 4, figsize=(24, 18))
    axes = axes.flatten()

    print(TARGET_SCORE_df_dict.keys())
    print(len(TARGET_SCORE_df_dict.keys()))
    # Plot the same scatter on all subplots as a placeholder
    for i, ax in enumerate(axes):

        ID_score = order_of_id_scores[i]
        print(ID_score)
        df = TARGET_SCORE_df_dict[ID_score]
        if df is None:
            continue
        score = '_'.join(ID_score.split('_')[1:])
        ID = ID_score.split('_')[0]

        kwargs = {}
        # Default scatter plot parameters
        kwargs.update({
            'x': df[f"Best_v1_ref"],
            'y': df[f"Best_v2_ref"],
            'group_labels': df['Group'],
            'xlabel': f'{score} (V1)',
            'ylabel': f'{score} (V2)',
            'title': f'{ID}',
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
        else:
            raise Exception(f"Score {score} not supported")
    
        kwargs['ax'] = ax
        subfix, subax = create_scatter(**kwargs)
        # ax = subax

    plt.tight_layout()
    

    plt.savefig(f'./PLOTS/GDT_TM_multi_panel.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return


assessment(TARGET_SCORE_DICT)


