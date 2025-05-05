import glob
import pandas as pd

# Get a list of all CSV files in the directories
V1A_df = pd.read_csv('./v1/best_global_gdt.csv')
V1B_df = pd.read_csv('./v2/best_global_gdt.csv')

V1A_by_v1 = pd.read_csv('./v1/best_global_gdt_by_group_v1.csv')
V1A_by_v2 = pd.read_csv('./v1/best_global_gdt_by_group_v2.csv')

V1B_by_v1 = pd.read_csv('./v2/best_global_gdt_by_group_v1.csv')
V1B_by_v2 = pd.read_csv('./v2/best_global_gdt_by_group_v2.csv')

combined_df = pd.DataFrame()
combined_df['Group'] = V1A_df['Group']
combined_df = combined_df.drop_duplicates(subset='Group', keep='first')

# get best fit and version for each group to V1A and V1B
combined_df['V1A'] = V1A_df['Global_GDT']
combined_df['V1A_version'] = V1A_df['Version']

# get corresponding data for V1B
V1B_GDTs = []
V1B_versions = []
for Group in combined_df['Group']:
    V1B_GDTs.append(V1B_df['Global_GDT'].loc[V1B_df['Group'] == Group].values[0])
    V1B_versions.append(V1B_df['Version'].loc[V1B_df['Group'] == Group].values[0])
combined_df['V1B'] = V1B_GDTs
combined_df['V1B_version'] = V1B_versions

# Add columns to store the final fit for each version
combined_df['V1A_final_fit'] = [0 for _ in range(len(combined_df['Group']))]
combined_df['V1B_final_fit'] = [0 for _ in range(len(combined_df['Group']))]

# Now, find the best match over both V1A and V1B
for i, group in enumerate(combined_df['Group']):
    if combined_df['V1A'].iloc[i] > combined_df['V1B'].iloc[i]:
        # The best match is coming from the match to V1A, find the model version used
        combined_df.at[i, 'V1A_final_fit'] = combined_df['V1A'].iloc[i]
        
        if combined_df['V1A_version'].iloc[i] == 'v2':
            # Handle empty results
            if not V1B_by_v1[V1B_by_v1['Group'] == group].empty:
                combined_df.at[i, 'V1B_final_fit'] = V1B_by_v1['Global_GDT'].loc[V1B_by_v1['Group'] == group].values[0]
        elif combined_df['V1A_version'].iloc[i] == 'v1':
            if not V1B_by_v2[V1B_by_v2['Group'] == group].empty:
                combined_df.at[i, 'V1B_final_fit'] = V1B_by_v2['Global_GDT'].loc[V1B_by_v2['Group'] == group].values[0]
    else:
        combined_df.at[i, 'V1B_final_fit'] = combined_df['V1B'].iloc[i]
        
        if combined_df['V1B_version'].iloc[i] == 'v2':
            if not V1A_by_v1[V1A_by_v1['Group'] == group].empty:
                combined_df.at[i, 'V1A_final_fit'] = V1A_by_v1['Global_GDT'].loc[V1A_by_v1['Group'] == group].values[0]
        elif combined_df['V1B_version'].iloc[i] == 'v1':
            if not V1A_by_v2[V1A_by_v2['Group'] == group].empty:
                combined_df.at[i, 'V1A_final_fit'] = V1A_by_v2['Global_GDT'].loc[V1A_by_v2['Group'] == group].values[0]

combined_df['Combined_Score'] = combined_df['V1A_final_fit'] + combined_df['V1B_final_fit']
combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
# Save the combined metric to a CSV file
combined_df.to_csv(f'T1228_GDT_two_state_1.csv', index=False)

from adjustText import adjust_text  
import matplotlib.pyplot as plt
# Plot the data as a scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(combined_df[f"V1A_final_fit"], combined_df[f"V1B_final_fit"], c='blue')
texts = [plt.text(combined_df[f"V1A_final_fit"].iloc[i], combined_df[f"V1B_final_fit"].iloc[i], txt, fontsize=8) for i, txt in enumerate(combined_df['Group'])]
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
plt.xlabel(f'Best Global_GDT V1A ref', fontsize=14, fontweight='bold')
plt.ylabel(f'Best Global_GDT V1B ref', fontsize=14, fontweight='bold')
plt.title(f'Scatter plot of best Global_GDT scores for 1228 V1A vs V1B', fontsize=16, fontweight='bold')
plt.legend()
plt.tight_layout()
# Save the plot as an image file
plt.savefig(f'T1228_Global_GDT_scatter_plot.png')
# plt.show()
plt.cla()

# combined_df['Combined_Score'] = combined_df['V1A_final_fit'] + combined_df['V1B_final_fit']
 
import matplotlib.pyplot as plt

# Sort the combined_df by 'Combined_Score' in descending order
combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
# Save the combined metric to a CSV file
combined_df.to_csv('combined_metric.csv', index=False)
# Create a stacked bar chart
plt.figure(figsize=(10, 6))
plt.bar(combined_df['Group'], combined_df['V1A_final_fit'], label='V1A_GDT_TS')
plt.bar(combined_df['Group'], combined_df['V1B_final_fit'], bottom=combined_df['V1A_final_fit'], label='V1B_GDT_TS')
plt.xlabel('Group', fontsize=14, fontweight='bold')
plt.ylabel('Two-State Score', fontsize=14, fontweight='bold')
plt.title('Aggregate Global GDT_TS scores for T1228 V1A and V1B', fontsize=16, fontweight='bold')
plt.legend()
plt.xticks(rotation=90)

# Save the plot as an image file
plt.savefig('T1228_combined_GDT_TS_plot.png')