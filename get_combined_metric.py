import pandas as pd
import matplotlib.pyplot as plt

# DO T1228 Assessment:
def assessment(ID):
    # Get a list of all CSV files in the directories
    V1A_df = pd.read_csv(f'./{ID}/V1A/best_global_gdt_combined_sorted_descending.csv')
    V1B_df = pd.read_csv(f'./{ID}/V1B/best_global_gdt_combined_sorted_descending.csv')

    V1A_by_v1 = pd.read_csv(f'./{ID}/V1A/best_global_gdt_by_group_v1.csv')
    V1A_by_v2 = pd.read_csv(f'./{ID}/V1A/best_global_gdt_by_group_v2.csv')

    V1B_by_v1 = pd.read_csv(f'./{ID}/V1B/best_global_gdt_by_group_v1.csv')
    V1B_by_v2 = pd.read_csv(f'./{ID}/V1B/best_global_gdt_by_group_v2.csv')

    combined_df = pd.DataFrame()
    combined_df['Group'] = V1A_df['Group']

    # get best fit and version for each group to V1A and V1B
    combined_df['V1A'] = V1A_df['Global_GDT']
    combined_df['V1A_model'] = V1A_df['Model']
    combined_df['V1A_version'] = V1A_df['Version']

    # get corresponding data for V1B
    V1B_GDTs = []
    V1B_versions = []
    V1B_models = []
    for Group in combined_df['Group']:
        V1B_GDTs.append(V1B_df['Global_GDT'].loc[V1B_df['Group'] == Group].values[0])
        V1B_versions.append(V1B_df['Version'].loc[V1B_df['Group'] == Group].values[0])
        V1B_models.append(V1B_df['Model'].loc[V1B_df['Group'] == Group].values[0])
    combined_df['V1B'] = V1B_GDTs
    combined_df['V1B_version'] = V1B_versions
    combined_df['V1B_model'] = V1B_models

    # Add columns to store the final fit for each version with proper dtype
    combined_df['V1A_final_fit'] = pd.Series(0.0, index=combined_df.index, dtype='float64')
    combined_df['V1B_final_fit'] = pd.Series(0.0, index=combined_df.index, dtype='float64')
    combined_df['V1A_final_model'] = ''
    combined_df['V1B_final_model'] = ''

    # Now, find the best match over both V1A and V1B
    for i, group in enumerate(combined_df['Group']):
        if combined_df['V1A'].iloc[i] > combined_df['V1B'].iloc[i]:
            # The best match is coming from the match to V1A, find the model version used
            combined_df.at[i, 'V1A_final_fit'] = combined_df['V1A'].iloc[i]
            combined_df.at[i, 'V1A_final_model'] = combined_df['V1A_model'].iloc[i]
            if combined_df['V1A_version'].iloc[i] == 'v2':
                # Handle empty results
                if not V1B_by_v1[V1B_by_v1['Group'] == group].empty:
                    combined_df.at[i, 'V1B_final_fit'] = V1B_by_v1['Global_GDT'].loc[V1B_by_v1['Group'] == group].values[0]
                    combined_df.at[i, 'V1B_final_model'] = V1B_by_v1['Model'].loc[V1B_by_v1['Group'] == group].values[0]
            elif combined_df['V1A_version'].iloc[i] == 'v1':
                if not V1B_by_v2[V1B_by_v2['Group'] == group].empty:
                    combined_df.at[i, 'V1B_final_fit'] = V1B_by_v2['Global_GDT'].loc[V1B_by_v2['Group'] == group].values[0]
                    combined_df.at[i, 'V1B_final_model'] = V1B_by_v2['Model'].loc[V1B_by_v2['Group'] == group].values[0]
        else:
            combined_df.at[i, 'V1B_final_fit'] = combined_df['V1B'].iloc[i]
            combined_df.at[i, 'V1B_final_model'] = combined_df['V1B_model'].iloc[i]
            if combined_df['V1B_version'].iloc[i] == 'v2':
                if not V1A_by_v1[V1A_by_v1['Group'] == group].empty:
                    combined_df.at[i, 'V1A_final_fit'] = V1A_by_v1['Global_GDT'].loc[V1A_by_v1['Group'] == group].values[0]
                    combined_df.at[i, 'V1A_final_model'] = V1A_by_v1['Model'].loc[V1A_by_v1['Group'] == group].values[0]
            elif combined_df['V1B_version'].iloc[i] == 'v1':
                if not V1A_by_v2[V1A_by_v2['Group'] == group].empty:
                    combined_df.at[i, 'V1A_final_fit'] = V1A_by_v2['Global_GDT'].loc[V1A_by_v2['Group'] == group].values[0]
                    combined_df.at[i, 'V1A_final_model'] = V1A_by_v2['Model'].loc[V1A_by_v2['Group'] == group].values[0]

    combined_df['Combined_Score'] = combined_df['V1A_final_fit'] + combined_df['V1B_final_fit']

    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Save the combined metric to a CSV file
    combined_df.to_csv(f'{ID}_combined_metric.csv', index=False)
    # Create a stacked bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(combined_df['Group'], combined_df['V1A_final_fit'], label='V1A_GDT_TS')
    plt.bar(combined_df['Group'], combined_df['V1B_final_fit'], bottom=combined_df['V1A_final_fit'], label='V1B_GDT_TS')

    # Update font size and make text bold
    plt.xlabel('Group', fontsize=14, fontweight='bold')
    plt.ylabel('Two-State Score', fontsize=14, fontweight='bold')
    plt.title(f'Aggregate Global GDT_TS scores for {ID} V1A and V1B', fontsize=16, fontweight='bold')

    # Update legend font size and weight
    plt.legend(fontsize=12)

    # Update x-ticks rotation and font size
    plt.xticks(rotation=90, fontsize=12, fontweight='bold')

    # Update y-ticks font size and weight
    plt.yticks(fontsize=12, fontweight='bold')

    plt.tight_layout()
    #plt.show()
    # Save the plot as an image file
    plt.savefig(f'{ID}_combined_metric_plot.png')

assessment('T1228')
assessment('T1239')