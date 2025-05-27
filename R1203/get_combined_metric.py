
import pandas as pd
import matplotlib.pyplot as plt

def assessment(merged_df_file, ID, score):

    # Get a list of all CSV files in the directories
    df = pd.read_csv(merged_df_file)
    df['Submission_ID'] = [ f.split()[0].split('R1203')[1] for f in df['Model'] ]
    df['Group_ID'] = df['Submission_ID'].str.extract(r'(\w+)_')[0]
 
    V1_df = df[df['Model'].str.endswith('v1')]
    V2_df = df[df['Model'].str.endswith('v2')]

    # Remove rows with the same Group_ID except the one with the maximum 'GDT_TS' value
    # V1_df = V1_df.loc[V1_df.groupby('Group_ID')[score].idxmax()]
    # V2_df = V2_df.loc[V2_df.groupby('Group_ID')[score].idxmax()]

    # print(f'V1_df: {V1_df.shape}')
    # print(f'V2_df: {V2_df.shape}')

    combined_df = pd.DataFrame({
        'Group_ID': pd.concat([V1_df['Group_ID'], V2_df['Group_ID']]).unique(),
    })
    # Remove rows with NaNs or empty data in the score column
    V1_df = V1_df.dropna(subset=[score])
    V2_df = V2_df.dropna(subset=[score])
    V1_df = V1_df[V1_df[score] != '']
    V2_df = V2_df[V2_df[score] != '']

    V1_df_try = V1_df.loc[V1_df.groupby('Group_ID')[score].idxmax()]
    V2_df_try = V2_df.loc[V2_df.groupby('Group_ID')[score].idxmax()]

    # For each Group_ID, find if the GDT_TS score is higher in V1_df_try or V2_df_try
    higher_GDT_TS = []
    print_bool = False
    for Group_ID in V1_df_try['Group_ID']:
        print_bool = False
        # if Group_ID == 'TS448':
        #     print_bool = True
        GDT_TS_V1 = 0
        GDT_TS_V2 = 0
        try:
            GDT_TS_V1 = V1_df_try[score].loc[V1_df_try['Group_ID'] == Group_ID].values[0]
            GDT_TS_V2 = V2_df_try[score].loc[V2_df_try['Group_ID'] == Group_ID].values[0]
        except:
            x = 0

        if GDT_TS_V1 > GDT_TS_V2: # best V1 is better than best V2
            V1_submission_id = V1_df_try['Submission_ID'].loc[V1_df_try['Group_ID'] == Group_ID].values[0]
            # if print_bool:
            #     print("V1 > V2", V1_submission_id)
            V1_df_try.loc[V1_df_try['Group_ID'] == Group_ID, score] = GDT_TS_V1
            # if print_bool:
            #     print("V2_df: ", V2_df)
            V2_df_copy = V2_df[~V2_df['Submission_ID'].isin([V1_submission_id])]
            try:
                # if print_bool:
                #     print("V2_df_copy: ", V2_df_copy)

                if V2_df_copy['Group_ID'].loc[V2_df_copy['Group_ID'] == Group_ID].empty:
                    V2_df_try.loc[V2_df_try['Group_ID'] == Group_ID, score] = 0
                    # print("V1 > V2", V1_submission_id)
                    # print(f"V2 {Group_ID} = 0")
                    continue
                V2_df_copy = V2_df_copy.loc[V2_df_copy.groupby('Group_ID')[score].idxmax()]
                # if print_bool:
                #     print("V2_df_copy: ", V2_df_copy)
                GDT_TS_V2_arr = V2_df_copy[score].loc[V2_df_copy['Group_ID'] == Group_ID]
                # print("GDT_TS_V2_arr: ", GDT_TS_V2_arr)
                GDT_TS_V2 = GDT_TS_V2_arr.values[0]
                # if print_bool:
                #     print("GDT_TS_V2: ", GDT_TS_V2)
                V2_df_try.loc[V2_df_try['Group_ID'] == Group_ID, score] = GDT_TS_V2
            except Exception as e:
                print(Group_ID)
                print(V2_df_copy['Group_ID'])
                print(V2_df_copy.loc[V2_df_copy.groupby('Group_ID')[score].idxmax()])
                print("V1 > V2", V1_submission_id)
                print(e)
                raise
        else: # best V2 is better than best V1
            V2_submission_id = V2_df_try['Submission_ID'].loc[V2_df_try['Group_ID'] == Group_ID].values[0]
            # print("V2 > V1", V2_submission_id)
            V2_df_try.loc[V2_df_try['Group_ID'] == Group_ID, score] = GDT_TS_V2
            V1_df_copy = V1_df[~V1_df['Submission_ID'].isin([V2_submission_id])]
            try:
                if V1_df_copy['Group_ID'].loc[V1_df_copy['Group_ID'] == Group_ID].empty:
                    V1_df_try.loc[V1_df_try['Group_ID'] == Group_ID, score] = 0
                    # print("V2 > V1", V1_submission_id)
                    # print(f"V1 {Group_ID} = 0")
                    continue
                V1_df_copy = V1_df_copy.loc[V1_df_copy.groupby('Group_ID')[score].idxmax()]
                GDT_TS_V1 = V1_df_copy[score].loc[V1_df_copy['Group_ID'] == Group_ID].values[0]
                # print("GDT_TS_V1: ", GDT_TS_V1)
                V1_df_try.loc[V1_df_try['Group_ID'] == Group_ID, score] = GDT_TS_V1
            except Exception as e:
                print("V2 > V1", V2_submission_id)
                print(e)
        if print_bool:
            print("Group_ID: ", Group_ID, f"{score}_V1: ", GDT_TS_V1, f"{score}_V2: ", GDT_TS_V2)

        # raise

    V1_df = V1_df_try
    V2_df = V2_df_try
    # print(f'V1_df: {V1_df.shape}')
    # print(f'V2_df: {V2_df.shape}')

    combined_df = pd.DataFrame({
        'Group_ID': pd.concat([V1_df['Group_ID'], V2_df['Group_ID']]).unique(),
    })

    # Find the GDT_TS from V1_df and V2_df for each group
    GDT_TS_V1 = []
    GDT_TS_V2 = []
    for Group_ID in combined_df['Group_ID']:
        GDT_TS_V1.append(V1_df[score].loc[V1_df['Group_ID'] == Group_ID].values[0] if not V1_df[score].loc[V1_df['Group_ID'] == Group_ID].empty else 0)
        GDT_TS_V2.append(V2_df[score].loc[V2_df['Group_ID'] == Group_ID].values[0] if not V2_df[score].loc[V2_df['Group_ID'] == Group_ID].empty else 0)
    combined_df[f"{score}_V1"] = GDT_TS_V1
    combined_df[f"{score}_V2"] = GDT_TS_V2
    from adjustText import adjust_text  
    # Plot the data as a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(combined_df[f"{score}_V1"], combined_df[f"{score}_V2"], c='blue')
    combined_df['Group_ID'] = combined_df['Group_ID'].str.replace('TS', '')
    texts = [plt.text(combined_df[f"{score}_V1"].iloc[i], combined_df[f"{score}_V2"].iloc[i], txt, fontsize=8) for i, txt in enumerate(combined_df['Group_ID'])]
    adjust_text(texts,arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                   expand_points=(2.0, 2.0),  # Increased expansion to avoid points
                   force_text=(0.5, 0.5),    # Increased force to move text away
                   force_points=(0.5, 0.5),  # Increased force to avoid points
                   avoid_text=True,          # Enable text avoidance
                   avoid_points=True,        # Enable point avoidance
                   avoid_self=True)     
    plt.xlabel(f'Best {score} score (V1 reference state)', fontsize=18)
    plt.ylabel(f'Best {score} score \n (V2 reference state)', fontsize=18)
    plt.title(f'Scatter plot of best {score} scores for {ID} V1 vs V2', fontsize=18)
    plt.legend(loc='upper right', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    # Save the plot as an image file
    plt.savefig(f'../PLOTS/{ID}_{score}_scatter_plot.png')
    # plt.show()
    plt.cla()
    # Add the values into another column (GDT_TS_both)
    combined_df[f"{score}_both"] = combined_df[f"{score}_V1"] + combined_df[f"{score}_V2"]
    print(combined_df[[f"{score}_both", f"{score}_V1", f"{score}_V2", 'Group_ID']])
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by=f"{score}_both", ascending=False)
    # Save the combined metric to a CSV file
    combined_df.to_csv(f'{ID}_combined_metric.csv', index=False)
    # For the five data points with the highest GDT_TS_both values, print the Group and GDT_TS_both values
    print(f'Top 5 GDT_TS aggregate values for {ID}')
    combined_df = combined_df.sort_values(by=f"{score}_both", ascending=False)
    print(combined_df[['Group_ID', f"{score}_both"]].head(5))
    #print(combined_df['Group'])
    # Create a stacked bar chart


    plt.close()
    plt.figure(figsize=(10, 6))
    plt.bar(combined_df['Group_ID'], combined_df[f"{score}_V1"], label=f"<{score}> (V1")
    plt.bar(combined_df['Group_ID'], combined_df[f"{score}_V2"], bottom=combined_df[f"{score}_V1"].values, label=f"<{score}> (V2)")
    plt.xlabel('Submission Group', fontsize=18)
    plt.ylabel('Two-State Score', fontsize=18)
    plt.title(f'Aggregate {score} scores for {ID} V1 and V2', fontsize=18)
    plt.legend(loc='upper right', fontsize=16)
    plt.xticks(rotation=90, fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    # Save the plot as an image file
    plt.savefig(f'../PLOTS/{ID}_combined_{score}_plot.png')


assessment('./composite_score_4_merged_model_scores.csv', 'R1203', 'Composite_Score_4')
assessment('./lddt.csv', 'R1203', 'Global_LDDT_normalized')