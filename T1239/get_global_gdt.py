import glob
import pandas as pd

def combine_gdt_scores(
    V1A_df: pd.DataFrame,
    V1B_df: pd.DataFrame,
    V1A_by_v1: pd.DataFrame,
    V1A_by_v2: pd.DataFrame,
    V1B_by_v1: pd.DataFrame,
    V1B_by_v2: pd.DataFrame,
    metric: str = 'Global_GDT'
) -> pd.DataFrame:
    """
    Combine scores from different reference structures and model versions into a single dataframe.
    
    This function takes scores for protein structure predictions against two reference structures (V1A and V1B)
    and combines them, ensuring compatible model versions are used for each reference.
    
    Args:
        V1A_df (pd.DataFrame): Best scores against V1A reference
        V1B_df (pd.DataFrame): Best scores against V1B reference
        V1A_by_v1 (pd.DataFrame): V1A scores using version 1 models
        V1A_by_v2 (pd.DataFrame): V1A scores using version 2 models
        V1B_by_v1 (pd.DataFrame): V1B scores using version 1 models
        V1B_by_v2 (pd.DataFrame): V1B scores using version 2 models
        metric (str, optional): The metric column name to use for scoring. Defaults to 'Global_GDT'.
        
    Returns:
        pd.DataFrame: Combined dataframe containing:
            - Group: Group identifier
            - V1A, V1B: Best scores for each reference
            - V1A_version, V1B_version: Original versions that achieved best scores
            - V1A_final_fit, V1B_final_fit: Final scores used in combination
            - V1A_final_model_name, V1B_final_model_name: Specific models used for final scores
            - Combined_Score: Sum of final fit scores
    """
    # Create a new dataframe to store combined results
    combined_df = pd.DataFrame()
    combined_df['Group'] = V1A_df['Group']  # Get list of all participating groups
    combined_df = combined_df.drop_duplicates(subset='Group', keep='first').reset_index(drop=True)  # Remove any duplicate group entries and reset index

    # Get the best scores and corresponding versions for V1A reference by finding max metric per group
    V1A_best = V1A_df.loc[V1A_df.groupby('Group')[metric].idxmax()]
    combined_df['V1A'] = combined_df['Group'].map(dict(zip(V1A_best['Group'], V1A_best[metric])))
    combined_df['V1A_version'] = combined_df['Group'].map(dict(zip(V1A_best['Group'], V1A_best['Version'])))

    # Get the best scores and corresponding versions for V1B reference by finding max metric per group
    V1B_best = V1B_df.loc[V1B_df.groupby('Group')[metric].idxmax()]
    combined_df['V1B'] = combined_df['Group'].map(dict(zip(V1B_best['Group'], V1B_best[metric])))
    combined_df['V1B_version'] = combined_df['Group'].map(dict(zip(V1B_best['Group'], V1B_best['Version'])))

    # Initialize columns for final combined scores
    # These will store the best possible combination of scores for each reference
    combined_df['V1A_final_fit'] = pd.Series((0.0 for _ in range(len(combined_df['Group']))), dtype='float64')
    combined_df['V1B_final_fit'] = pd.Series((0.0 for _ in range(len(combined_df['Group']))), dtype='float64')
    # Add columns to track the specific model names used for each reference
    combined_df['V1A_final_model_name'] = pd.Series(('' for _ in range(len(combined_df['Group']))), dtype='str')
    combined_df['V1B_final_model_name'] = pd.Series(('' for _ in range(len(combined_df['Group']))), dtype='str')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(combined_df)


    # For each group, determine the best possible combination of scores
    # This involves finding the best score for each reference structure while ensuring
    # we use compatible model versions (v1 or v2) for both references
    for i, group in enumerate(combined_df['Group']):
        if combined_df.at[i, 'V1A'] > combined_df.at[i, 'V1B']:
            # If V1A score is better, use that as the primary score
            combined_df.at[i, 'V1A_final_fit'] = combined_df.at[i, 'V1A']
            
            # Then find the corresponding V1B score using the appropriate model version
            if combined_df.at[i, 'V1A_version'] == 'v2':
                combined_df.at[i, 'V1B_version'] = 'v1'
                # If V1A used v2, look for V1B score using v1
                if not V1B_by_v1[V1B_by_v1['Group'] == group].empty:
                    combined_df.at[i, 'V1B_final_fit'] = V1B_by_v1[metric].loc[V1B_by_v1['Group'] == group].values[0]
                    combined_df.at[i, 'V1B_final_model_name'] = V1B_by_v1['Model'].loc[V1B_by_v1['Group'] == group].values[0]
            elif combined_df.at[i, 'V1A_version'] == 'v1':
                combined_df.at[i, 'V1B_version'] = 'v2'
                # If V1A used v1, look for V1B score using v2
                if not V1B_by_v2[V1B_by_v2['Group'] == group].empty:
                    combined_df.at[i, 'V1B_final_fit'] = V1B_by_v2[metric].loc[V1B_by_v2['Group'] == group].values[0]
                    combined_df.at[i, 'V1B_final_model_name'] = V1B_by_v2['Model'].loc[V1B_by_v2['Group'] == group].values[0]
        else:
            # If V1B score is better, use that as the primary score
            combined_df.at[i, 'V1B_final_fit'] = combined_df.at[i, 'V1B']
            
            # Then find the corresponding V1A score using the appropriate model version
            if combined_df.at[i, 'V1B_version'] == 'v2':
                combined_df.at[i, 'V1A_version'] = 'v1'
                # If V1B used v2, look for V1A score using v1
                if not V1A_by_v1[V1A_by_v1['Group'] == group].empty:
                    combined_df.at[i, 'V1A_final_fit'] = V1A_by_v1[metric].loc[V1A_by_v1['Group'] == group].values[0]
                    combined_df.at[i, 'V1A_final_model_name'] = V1A_by_v1['Model'].loc[V1A_by_v1['Group'] == group].values[0]
            elif combined_df.at[i, 'V1B_version'] == 'v1':
                combined_df.at[i, 'V1A_version'] = 'v2'
                # If V1B used v1, look for V1A score using v2
                if not V1A_by_v2[V1A_by_v2['Group'] == group].empty:
                    combined_df.at[i, 'V1A_final_fit'] = V1A_by_v2[metric].loc[V1A_by_v2['Group'] == group].values[0]
                    combined_df.at[i, 'V1A_final_model_name'] = V1A_by_v2['Model'].loc[V1A_by_v2['Group'] == group].values[0]

    # Calculate the final combined score by adding the best scores for both references
    combined_df['Combined_Score'] = combined_df['V1A_final_fit'] + combined_df['V1B_final_fit']
    # Sort groups by their combined score in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    return combined_df

# Load the input dataframes
V1A_df = pd.read_csv('./v1/best_global_gdt.csv')  # Best scores against V1A reference
V1B_df = pd.read_csv('./v2/best_global_gdt.csv')  # Best scores against V1B reference
V1A_by_v1 = pd.read_csv('./v1/best_global_gdt_by_group_v1.csv')  # V1A scores using version 1 models
V1A_by_v2 = pd.read_csv('./v1/best_global_gdt_by_group_v2.csv')  # V1A scores using version 2 models
V1B_by_v1 = pd.read_csv('./v2/best_global_gdt_by_group_v1.csv')  # V1B scores using version 1 models
V1B_by_v2 = pd.read_csv('./v2/best_global_gdt_by_group_v2.csv')  # V1B scores using version 2 models

# Get the combined results
combined_df = combine_gdt_scores(
    V1A_df=V1A_df,
    V1B_df=V1B_df,
    V1A_by_v1=V1A_by_v1,
    V1A_by_v2=V1A_by_v2,
    V1B_by_v1=V1B_by_v1,
    V1B_by_v2=V1B_by_v2,
    metric='Global_GDT'  # Specify the metric to use
)
# combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
# Save the combined metric to a CSV file


from adjustText import adjust_text  
import matplotlib.pyplot as plt
# Plot the data as a scatter plot
plt.figure(figsize=(10, 6))
# Add y=x line
max_val = max(combined_df[f"V1A_final_fit"].max(), combined_df[f"V1B_final_fit"].max())
plt.plot([0, max_val], [0, max_val], 'r--', label='y=x')
plt.scatter(combined_df[f"V1A_final_fit"], combined_df[f"V1B_final_fit"], c='blue', label='Groups')
# Set axis bounds with padding
x_min = combined_df[f"V1A_final_fit"].min()
x_max = combined_df[f"V1A_final_fit"].max()
y_min = combined_df[f"V1B_final_fit"].min()
y_max = combined_df[f"V1B_final_fit"].max()
padding = 0.05  # 5% padding
x_range = x_max - x_min
y_range = y_max - y_min
plt.xlim(x_min - x_range * padding, x_max + x_range * padding)
plt.ylim(y_min - y_range * padding, y_max + y_range * padding)
texts = [plt.text(combined_df[f"V1A_final_fit"].iloc[i], combined_df[f"V1B_final_fit"].iloc[i], txt, fontsize=8) for i, txt in enumerate(combined_df['Group'].str.replace('TS', ''))]
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                   expand_points=(2.0, 2.0),  # Increased expansion to avoid points
                   force_text=(0.5, 0.5),    # Increased force to move text away
                   force_points=(0.5, 0.5),  # Increased force to avoid points
                   avoid_text=True,          # Enable text avoidance
                   avoid_points=True,        # Enable point avoidance
                   avoid_self=True)          # Enable self avoidance)
plt.xlabel(f'Best Global_GDT V1A ref', fontsize=18)
plt.ylabel(f'Best Global_GDT V1B ref', fontsize=18)
plt.title(f'Scatter plot of best Global_GDT scores for 1239 V1A vs V1B', fontsize=18)
plt.legend(fontsize=16)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
# Save the plot as an image file
plt.savefig(f'../PLOTS/T1239_Global_GDT_scatter_plot.png')
# plt.show()
plt.cla()

combined_df['Combined_Score'] = combined_df['V1A_final_fit'] + combined_df['V1B_final_fit']

# Sort the combined_df by 'Combined_Score' in descending order
combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
# Save the combined metric to a CSV file
combined_df.to_csv(f'T1239_GDT_two_state.csv', index=False)

# Create a stacked bar chart
plt.figure(figsize=(10, 6))
# Convert Group to string type to ensure it's treated as categorical data
combined_df['Group'] = combined_df['Group'].astype(str)
plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df['V1A_final_fit'], label='<GDT_TS> (V1A)', color='blue')
plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df['V1B_final_fit'], bottom=combined_df['V1A_final_fit'], label='<GDT_TS> (V1B)', color='orange')
plt.xlabel('Group', fontsize=18)
plt.ylabel('Two-State Score', fontsize=18)
plt.title('Aggregate Global GDT_TS scores for T1239 V1A and V1B', fontsize=18)
plt.legend(loc='upper right', fontsize=16)
plt.xticks(rotation=90, fontsize=8)
plt.yticks(fontsize=18)
plt.tight_layout()
# Save the plot as an image file
plt.savefig('../PLOTS/T1239_global_gdt_plot.png')