import pandas as pd
from adjustText import adjust_text
import matplotlib.pyplot as plt

def assessment(ID, score):
    # Get a list of all CSV files in the directories
    v1_ref_df = pd.read_csv(f'./sorted_dockq_data_v1.csv')
    v1_ref_df['Group'] = v1_ref_df['Model'].apply(lambda x: x.split('_')[0].split('v')[1][1:])
    v1_ref_df['Version'] = v1_ref_df['Model'].apply(lambda x: x.split(f'{ID}')[1][:2])

    v2_ref_df = pd.read_csv(f'./sorted_dockq_data_v2.csv')
    v2_ref_df['Group'] = v2_ref_df['Model'].apply(lambda x: x.split('_')[0].split('v')[1][1:])
    v2_ref_df['Version'] = v2_ref_df['Model'].apply(lambda x: x.split(f'{ID}')[1][:2])

    v1_ref_model_v1 = v1_ref_df[v1_ref_df['Model'].str.contains('v1')]
    v1_ref_model_v2 = v1_ref_df[v1_ref_df['Model'].str.contains('v2')]

    v2_ref_model_v1 = v2_ref_df[v2_ref_df['Model'].str.contains('v1')]
    v2_ref_model_v2 = v2_ref_df[v2_ref_df['Model'].str.contains('v2')]

    # STEP 1: Get best fit overall
    v1_ref_model_v1_try = v1_ref_model_v1.loc[v1_ref_model_v1.groupby('Group')[score].idxmax()]
    v1_ref_model_v2_try = v1_ref_model_v2.loc[v1_ref_model_v2.groupby('Group')[score].idxmax()]
    v2_ref_model_v1_try = v2_ref_model_v1.loc[v2_ref_model_v1.groupby('Group')[score].idxmax()]
    v2_ref_model_v2_try = v2_ref_model_v2.loc[v2_ref_model_v2.groupby('Group')[score].idxmax()]

    combined_df = pd.DataFrame()
    combined_df['Group'] = pd.concat([v1_ref_df['Group'], v2_ref_df['Group']]).unique()
    for Group in combined_df['Group']:
        #print(Group)
        best_fit_v1_v1 = v1_ref_model_v1_try[v1_ref_model_v1_try['Group'] == Group]
        best_fit_v1_v2 = v1_ref_model_v2_try[v1_ref_model_v2_try['Group'] == Group]
        best_fit_v2_v1 = v2_ref_model_v1_try[v2_ref_model_v1_try['Group'] == Group]
        best_fit_v2_v2 = v2_ref_model_v2_try[v2_ref_model_v2_try['Group'] == Group]

        best_fit = pd.concat([best_fit_v1_v1, best_fit_v1_v2, best_fit_v2_v1, best_fit_v2_v2]).sort_values(by=score, ascending=False).iloc[0][score]
        best_fit_source = ""
        if pd.notna(best_fit):
            if best_fit in best_fit_v1_v1[score].values:
                best_fit_source = 'v1_ref_model_v1_try'
            elif best_fit in best_fit_v1_v2[score].values:
                best_fit_source = 'v1_ref_model_v2_try'
            elif best_fit in best_fit_v2_v1[score].values:
                best_fit_source = 'v2_ref_model_v1_try'
            elif best_fit in best_fit_v2_v2[score].values:
                best_fit_source = 'v2_ref_model_v2_try'
            else:
                best_fit_source = 'unknown'
                raise
        else:
            best_fit_source = 'empty'
            raise

        def place_data(group, data_dest, dest_column, data_source, source_column):
            try:
                data_dest.loc[data_dest['Group'] == group, dest_column] = data_source[source_column].iloc[0]
            except:
                try:
                    data_dest.loc[data_dest['Group'] == group, dest_column] = data_source[source_column]
                except Exception as e:
                    print(e)
                    print(group)
                    print(data_dest)
                    print(data_source)
                    raise
            return data_dest
                    

        if best_fit_source[1] == '1': # group had a model with best fit to v1 ref
            combined_df.loc[combined_df['Group'] == Group, f'best_{score}_v1_ref'] = best_fit
            if best_fit_source.split('_')[-2][1] == '1': # best model fit came from v1 submission
                # need to find the best model fit from v2 submission to v2 ref
                if Group == 'TS015':
                    print("HERE")
                    print(best_fit_v2_v2)
                combined_df = place_data(Group, combined_df,  f'best_model_v1_ref', best_fit_v1_v1, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v1_ref', best_fit_v1_v1, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_model_v2_ref', best_fit_v2_v2, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v2_ref', best_fit_v2_v2, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_{score}_v2_ref', best_fit_v2_v2, score)
            elif best_fit_source.split('_')[-2][1] == '2': # best model fit came from v2 submission
                # need to find the best model fit from v1 submission to v2 ref
                combined_df = place_data(Group, combined_df,  f'best_model_v1_ref', best_fit_v1_v2, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v1_ref', best_fit_v1_v2, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_model_v2_ref', best_fit_v2_v1, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v2_ref', best_fit_v2_v1, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_{score}_v2_ref', best_fit_v2_v1, score)
            else:
                raise
        elif best_fit_source[1] == '2': # group had a model with best fit to v2 ref
            combined_df.loc[combined_df['Group'] == Group, f'best_{score}_v2_ref'] = best_fit
            if best_fit_source.split('_')[-2][1] == '1': # best model fit came from v1 submission
                # need to find the best model fit from v2 submission to v1 ref
                combined_df = place_data(Group, combined_df,  f'best_model_v2_ref', best_fit_v2_v1, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v2_ref', best_fit_v2_v1, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_model_v1_ref', best_fit_v1_v2, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v1_ref', best_fit_v1_v2, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_{score}_v1_ref', best_fit_v1_v2, score)
            elif best_fit_source.split('_')[-2][1] == '2': # best model fit came from v2 submission
                # need to find the best model fit from v1 submission to v1 ref
                combined_df = place_data(Group, combined_df,  f'best_model_v2_ref', best_fit_v2_v2, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v2_ref', best_fit_v2_v2, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_model_v1_ref', best_fit_v1_v1, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v1_ref', best_fit_v1_v1, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_{score}_v1_ref', best_fit_v1_v1, score)
            else:
                raise
        else:
            raise

    combined_df['best_v1_ref'] = combined_df[f'best_{score}_v1_ref'].fillna(0)
    combined_df['best_v2_ref'] = combined_df[f'best_{score}_v2_ref'].fillna(0)

    # Plot the data as a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(combined_df['best_v1_ref'], combined_df['best_v2_ref'], c='blue')
    texts = [plt.text(combined_df['best_v1_ref'].iloc[i], combined_df['best_v2_ref'].iloc[i], txt, fontsize=8) for i, txt in enumerate(combined_df['Group'])]
    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
    plt.xlabel(f'Best {score} v1 ref', fontsize=14, fontweight='bold')
    plt.ylabel(f'Best {score} v2 ref', fontsize=14, fontweight='bold')
    plt.title(f'Scatter plot of best {score} scores for {ID} V1 vs V2', fontsize=16, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    # Save the plot as an image file
    plt.savefig(f'{ID}_{score}_scatter_plot.png')
    # plt.show()
    plt.cla()

    combined_df['Combined_Score'] = combined_df['best_v1_ref'] + combined_df['best_v2_ref']

    combined_df.to_csv(f'{ID}_combined_metric.csv', index=False)
    print(combined_df)
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Save the combined metric to a CSV file
    combined_df.to_csv(f'{ID}_combined_metric.csv', index=False)
    # Create a stacked bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(combined_df['Group'], combined_df[f'best_v1_ref'], label=f'Best {score} v1 ref')
    plt.bar(combined_df['Group'], combined_df[f'best_v2_ref'], bottom=combined_df[f'best_v1_ref'], label=f'Best {score} v2 ref')
    plt.xlabel('Group', fontsize=14, fontweight='bold')
    plt.ylabel('Two-State Score', fontsize=14, fontweight='bold')
    plt.title(f'Aggregate {score} scores for {ID} V1 and V2', fontsize=14, fontweight='bold')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    # Save the plot as an image file
    plt.savefig(f'{ID}_{score}_combined_metric_plot.png')
    raise
    

    combined_df = pd.DataFrame()
    combined_df['Group'] = v1_ref_df['Group']

    # get best fit and version for each group to V1A and V1B
    combined_df['v1_ref'] = v1_ref_df[f'{score}']
    combined_df['v1_ref_model'] = v1_ref_df['Model']
    combined_df['v1_ref_version'] = v1_ref_df['Version']

    # get corresponding data for V1B
    V1B_GDTs = []
    V1B_versions = []
    V1B_models = []
    for Group in combined_df['Group']:
        V1B_GDTs.append(v2_ref_df[f'{score}'].loc[v2_ref_df['Group'] == Group].values[0])
        V1B_versions.append(v2_ref_df['Version'].loc[v2_ref_df['Group'] == Group].values[0])
        V1B_models.append(v2_ref_df['Model'].loc[v2_ref_df['Group'] == Group].values[0])
    combined_df['v2_ref'] = V1B_GDTs
    combined_df['v2_ref_version'] = V1B_versions
    combined_df['v2_ref_model'] = V1B_models

    # Add columns to store the final fit for each version
    combined_df[f'v1_ref_final_{score}'] = [0 for _ in range(len(combined_df['Group']))]
    combined_df[f'v2_ref_final_{score}'] = [0 for _ in range(len(combined_df['Group']))]

    # Now, find the best match over both V1A and V1B
    for i, group in enumerate(combined_df['Group']):
        if combined_df['v1_ref'].iloc[i] > combined_df['v2_ref'].iloc[i]:
            # The best match is coming from the match to V1A, find the model version used
            combined_df.at[i, f'v1_ref_final_{score}'] = combined_df['v1_ref'].iloc[i]
            combined_df.at[i, 'v1_ref_final_model'] = combined_df['v1_ref_model'].iloc[i]
            if combined_df['v1_ref_version'].iloc[i] == 'v2':
                # Handle empty results for v2_ref_model_v1
                if not v2_ref_model_v1[v2_ref_model_v1['Group'] == group].empty:
                    combined_df.at[i, f'v2_ref_final_{score}'] = v2_ref_model_v1[f'{score}'].loc[v2_ref_model_v1['Group'] == group].values[0]
                    combined_df.at[i, 'v2_ref_final_model'] = v2_ref_model_v1['Model'].loc[v2_ref_model_v1['Group'] == group].values[0]
            elif combined_df['v1_ref_version'].iloc[i] == 'v1':
                # Handle empty results for v2_ref_model_v2
                if not v2_ref_model_v2[v2_ref_model_v2['Group'] == group].empty:
                    combined_df.at[i, f'v2_ref_final_{score}'] = v2_ref_model_v2[f'{score}'].loc[v2_ref_model_v2['Group'] == group].values[0]
                    combined_df.at[i, 'v2_ref_final_model'] = v2_ref_model_v2['Model'].loc[v2_ref_model_v2['Group'] == group].values[0]
        else:
            # The best match is coming from the match to V1B, find the model version used
            combined_df.at[i, f'v2_ref_final_{score}'] = combined_df['v2_ref'].iloc[i]
            combined_df.at[i, 'v2_ref_final_model'] = combined_df['v2_ref_model'].iloc[i]
            if combined_df['v2_ref_version'].iloc[i] == 'v2':
                # Handle empty results for v1_ref_model_v1
                if not v1_ref_model_v1[v1_ref_model_v1['Group'] == group].empty:
                    combined_df.at[i, f'v1_ref_final_{score}'] = v1_ref_model_v1[f'{score}'].loc[v1_ref_model_v1['Group'] == group].values[0]
                    combined_df.at[i, 'v1_ref_final_model'] = v1_ref_model_v1['Model'].loc[v1_ref_model_v1['Group'] == group].values[0]
            elif combined_df['v2_ref_version'].iloc[i] == 'v1':
                # Handle empty results for v1_ref_model_v2
                if not v1_ref_model_v2[v1_ref_model_v2['Group'] == group].empty:
                    combined_df.at[i, f'v1_ref_final_{score}'] = v1_ref_model_v2[f'{score}'].loc[v1_ref_model_v2['Group'] == group].values[0]
                    combined_df.at[i, 'v1_ref_final_model'] = v1_ref_model_v2['Model'].loc[v1_ref_model_v2['Group'] == group].values[0]

    combined_df['Combined_Score'] = combined_df[f'v1_ref_final_{score}'] + combined_df[f'v2_ref_final_{score}']

    combined_df.to_csv(f'{ID}_combined_metric.csv', index=False)
    print(combined_df)
    raise
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Save the combined metric to a CSV file
    combined_df.to_csv(f'{ID}_combined_metric.csv', index=False)
    # Create a stacked bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(combined_df['Group'], combined_df[f'v1_ref_final_{score}'], label=f'v1_ref_final_{score}')
    plt.bar(combined_df['Group'], combined_df[f'v2_ref_final_{score}'], bottom=combined_df[f'v1_ref_final_{score}'], label=f'v2_ref_final_{score}')
    plt.xlabel('Group')
    plt.ylabel('Score')
    plt.title(f'Aggregate Global GDT_TS scores for {ID} V1A and V1B')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    # Save the plot as an image file
    plt.savefig(f'{ID}_combined_metric_plot.png')


assessment("T1249", "Average_dockq")