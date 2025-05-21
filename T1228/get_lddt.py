import glob
import pandas as pd
import matplotlib.pyplot as plt

def assessment(ID, score):
    # Get a list of all CSV files in the directories
    v1_ref_df = pd.read_csv(f'./v1/valid_models_global_lddtv1.csv')
    v1_ref_df['Group'] = v1_ref_df['Model'].apply(lambda x: x.split('_')[0].split('v')[1][1:])
    v1_ref_df['Version'] = v1_ref_df['Model'].apply(lambda x: x.split(f'{ID}')[1][:2])

    v2_ref_df = pd.read_csv(f'./v2/valid_models_global_lddtv2.csv')
    v2_ref_df['Group'] = v2_ref_df['Model'].apply(lambda x: x.split('_')[0].split('v')[1][1:])
    v2_ref_df['Version'] = v2_ref_df['Model'].apply(lambda x: x.split(f'{ID}')[1][:2])

    v1_ref_model_v1 = v1_ref_df[v1_ref_df['Model'].str.contains('v1')]

    print(v1_ref_model_v1.columns)
    v2_ref_model_v2 = v2_ref_df[v2_ref_df['Model'].str.contains('v2')]

    # STEP 1: Get best fit overall
    v1_ref_model_v1_try = v1_ref_df.loc[v1_ref_model_v1.groupby('Group')[score].idxmax()]
    v2_ref_model_v2_try = v2_ref_df.loc[v2_ref_model_v2.groupby('Group')[score].idxmax()]

    combined_df = pd.DataFrame()
    combined_df['Group'] = pd.concat([v1_ref_df['Group'], v2_ref_df['Group']]).unique()
    for Group in combined_df['Group']:
        #print(Group)
        best_fit_v1_v1 = v1_ref_model_v1_try[v1_ref_model_v1_try['Group'] == Group]
        best_fit_v2_v2 = v2_ref_model_v2_try[v2_ref_model_v2_try['Group'] == Group]

        best_fit = pd.concat([best_fit_v1_v1, best_fit_v2_v2]).sort_values(by=score, ascending=False).iloc[0][score]
        best_fit_source = ""
        if pd.notna(best_fit):
            if best_fit in best_fit_v1_v1[score].values:
                best_fit_source = 'v1_ref_model_v1_try'
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

                combined_df = place_data(Group, combined_df,  f'best_model_v1_ref', best_fit_v1_v1, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v1_ref', best_fit_v1_v1, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_model_v2_ref', best_fit_v2_v2, 'Model')
                combined_df = place_data(Group, combined_df,  f'best_version_v2_ref', best_fit_v2_v2, 'Version')
                combined_df = place_data(Group, combined_df,  f'best_{score}_v2_ref', best_fit_v2_v2, score)
            else:
                raise
        elif best_fit_source[1] == '2': # group had a model with best fit to v2 ref
            combined_df.loc[combined_df['Group'] == Group, f'best_{score}_v2_ref'] = best_fit
            if best_fit_source.split('_')[-2][1] == '2': # best model fit came from v1 submission
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
    print(combined_df)
    from adjustText import adjust_text  

    # Create figure and main axes
    fig, ax_main = plt.subplots(figsize=(10, 6))
    
    # Add y=x line
    max_val = max(combined_df["best_v1_ref"].max(), combined_df["best_v2_ref"].max())
    ax_main.plot([0, max_val], [0, max_val], 'r--', label='y=x')
    scatter = ax_main.scatter(combined_df['best_v1_ref'], combined_df['best_v2_ref'], c='blue', label='Groups')
    
    # Create inset axes using inset_axes
    ax_inset = ax_main.inset_axes([0.5, 0.05, 0.475, 0.475])  # [left, bottom, width, height]
    ax_inset.plot([0, max_val], [0, max_val], 'r--')
    ax_inset.scatter(combined_df['best_v1_ref'], combined_df['best_v2_ref'], c='blue')
    ax_inset.set_xlim(0.74, 0.78)
    ax_inset.set_ylim(0.71, 0.75)
    ax_inset.set_xticks([0.74, 0.75, 0.76, 0.77, 0.78])
    ax_inset.set_yticks([0.71, 0.72, 0.73, 0.74, 0.75])
    ax_inset.tick_params(labelsize=8)
    ax_inset.grid(True, linestyle='--', alpha=0.7)
    
    # Add rectangle in main plot to show zoomed region
    rect = plt.Rectangle((0.74, 0.71), 0.04, 0.04, fill=False, color='red', linestyle='--')
    ax_main.add_patch(rect)
    
    # Set axis bounds with padding for main plot
    x_min = combined_df["best_v1_ref"].min()
    x_max = combined_df["best_v1_ref"].max()
    y_min = combined_df["best_v2_ref"].min()
    y_max = combined_df["best_v2_ref"].max()
    padding = 0.05  # 5% padding
    x_range = x_max - x_min
    y_range = y_max - y_min
    ax_main.set_xlim(x_min - x_range * padding, x_max + x_range * padding)
    ax_main.set_ylim(y_min - y_range * padding, y_max + y_range * padding)
    
    # Add labels and adjust text for main plot and inset
    inset_xlim = (0.74, 0.78)
    inset_ylim = (0.71, 0.75)
    
    # First handle inset texts
    inset_texts = []
    for i, (x, y, txt) in enumerate(zip(combined_df['best_v1_ref'], 
                                      combined_df['best_v2_ref'],
                                      combined_df['Group'].str.replace('TS', ''))):
        if (inset_xlim[0] <= x <= inset_xlim[1] and 
            inset_ylim[0] <= y <= inset_ylim[1]):
            inset_texts.append(ax_inset.text(x, y, txt, fontsize=8))
    
    # Adjust inset texts
    if inset_texts:
        adjust_text(inset_texts, 
                   ax=ax_inset,  # Specify the axis for inset
                   arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                   expand_points=(1.1, 1.1),
                   force_points=(0.1, 0.1))
    
    # Then handle main plot texts
    main_texts = []
    for i, (x, y, txt) in enumerate(zip(combined_df['best_v1_ref'], 
                                      combined_df['best_v2_ref'],
                                      combined_df['Group'].str.replace('TS', ''))):
        if not (inset_xlim[0] <= x <= inset_xlim[1] and 
                inset_ylim[0] <= y <= inset_ylim[1]):
            main_texts.append(ax_main.text(x, y, txt, fontsize=8))
    
    # Adjust main plot texts
    if main_texts:
        adjust_text(main_texts, 
                   ax=ax_main,  # Specify the axis for main plot
                   arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                   expand_points=(2.0, 2.0),  # Increased expansion to avoid points
                   force_text=(0.5, 0.5),    # Increased force to move text away
                   force_points=(0.5, 0.5),  # Increased force to avoid points
                   avoid_text=True,          # Enable text avoidance
                   avoid_points=True,        # Enable point avoidance
                   avoid_self=True)          # Enable self avoidance
    
    # Set labels and title for main plot
    ax_main.set_xlabel(f'Best {score} V1 ref', fontsize=18)
    ax_main.set_ylabel(f'Best {score} V2 ref', fontsize=18)
    ax_main.set_title(f'Scatter plot of best {score} scores for {ID} V1 vs V2', fontsize=18)
    ax_main.legend(fontsize=16)
    ax_main.tick_params(axis='both', labelsize=16)
    
    plt.tight_layout()
    # Save the plot as an image file
    fig.savefig(f'../PLOTS/{ID}_{score}_scatter_plot.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    combined_df['Combined_Score'] = combined_df['best_v1_ref'] + combined_df['best_v2_ref']


    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Save the combined metric to a CSV file
    combined_df.to_csv(f'{ID}_{score}_two_state.csv', index=False)
    # Create a stacked bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df[f'best_{score}_v1_ref'], label=f'<lDDT> (V1A)', color='blue')
    plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df[f'best_{score}_v2_ref'], bottom=combined_df[f'best_{score}_v1_ref'], label=f'<lDDT> (V1B)', color='orange')
    plt.xlabel('Group', fontsize=18)
    plt.ylabel('Two-State Score', fontsize=18)
    plt.title(f'Aggregate {score} scores for {ID} V1A and V1B', fontsize=18)
    plt.legend(loc='upper right', fontsize=16)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    # Save the plot as an image file
    plt.savefig(f'../PLOTS/{ID}_{score}_two_state.png')
assessment("T1228", "Global LDDT")