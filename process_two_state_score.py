import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv

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
    if ID == 'R1203':
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


def create_scatter(
    x,
    y,
    group_labels,
    xlabel,
    ylabel,
    title,
    legend_label='Submission Groups',
    main_xlim=None,
    main_ylim=None,
    inset=False,
    inset_position=[0.5, 0.05, 0.475, 0.475],
    inset_xlim=None,
    inset_ylim=None,
    inset_xticks=None,
    inset_yticks=None,
    highlight_inset_rect=False,
    rect_xy=None,
    rect_width=None,
    rect_height=None,
    adjust_texts=True,
    save_path=None,
    dpi=300
):
    """
    Create a scatterplot with optional inset.
    Parameters:
        x, y: Data for scatterplot
        group_labels: Labels for each point
        xlabel, ylabel, title: Axis and plot labels
        legend_label: Label for legend
        main_xlim, main_ylim: Tuple for main plot axis limits
        inset: Whether to create an inset
        inset_position: [left, bottom, width, height] for inset axes
        inset_xlim, inset_ylim: Tuple for inset axis limits
        inset_xticks, inset_yticks: Ticks for inset axes
        highlight_inset_rect: Whether to draw a rectangle on main plot
        rect_xy: (x, y) for rectangle lower left
        rect_width, rect_height: Rectangle width and height
        adjust_texts: Whether to adjust text to avoid overlap
        save_path: If provided, save the figure to this path
        dpi: Dots per inch for saving
    Returns:
        fig, ax_main, ax_inset (if inset=True)
    """
    fig, ax_main = plt.subplots(figsize=(10, 6))
    max_val = max(max(x), max(y))
    ax_main.plot([0, max_val], [0, max_val], 'r-', label='y=x')
    scatter = ax_main.scatter(x, y, c='blue', label=legend_label)

    # Set axis bounds with padding for main plot if not provided
    if main_xlim is None:
        x_min, x_max = min(x), max(x)
        padding = 0.05
        x_range = x_max - x_min
        main_xlim = (x_min - x_range * padding, x_max + x_range * padding)
    if main_ylim is None:
        y_min, y_max = min(y), max(y)
        padding = 0.05
        y_range = y_max - y_min
        main_ylim = (y_min - y_range * padding, y_max + y_range * padding)
    ax_main.set_xlim(*main_xlim)
    ax_main.set_ylim(*main_ylim)

    ax_inset = None
    if inset:
        ax_inset = ax_main.inset_axes(inset_position)
        ax_inset.plot([0, max_val], [0, max_val], 'r-')
        ax_inset.scatter(x, y, c='blue')
        if inset_xlim:
            ax_inset.set_xlim(*inset_xlim)
        if inset_ylim:
            ax_inset.set_ylim(*inset_ylim)
        if inset_xticks:
            ax_inset.set_xticks(inset_xticks)
        if inset_yticks:
            ax_inset.set_yticks(inset_yticks)
        ax_inset.tick_params(labelsize=8)
        ax_inset.grid(True, linestyle='--', alpha=0.7)
        # Add rectangle in main plot to show zoomed region
        if highlight_inset_rect and rect_xy and rect_width and rect_height:
            rect = plt.Rectangle(rect_xy, rect_width, rect_height, fill=False, color='red', linestyle='--')
            ax_main.add_patch(rect)

    # Add labels and adjust text for main plot and inset
    texts_main = []
    texts_inset = []
    for i, (xv, yv, txt) in enumerate(zip(x, y, group_labels)):
        txt = str(txt)
        if inset and inset_xlim and inset_ylim and (inset_xlim[0] <= xv <= inset_xlim[1] and inset_ylim[0] <= yv <= inset_ylim[1]):
            texts_inset.append(ax_inset.text(xv, yv, txt.replace('TS', ''), fontsize=8))
        else:
            texts_main.append(ax_main.text(xv, yv, txt.replace('TS', ''), fontsize=8))
    if adjust_texts:
        if texts_inset:
            adjust_text(texts_inset, 
                        ax=ax_inset, 
                        arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                        expand_points=(1.1, 1.1),
                        force_points=(0.1, 0.1))
        if texts_main:
            adjust_text(texts_main, 
                        ax=ax_main, 
                        arrowprops=dict(arrowstyle='->', color='red', lw=0.5),
                        expand_points=(2.0, 2.0),
                        force_text=(0.5, 0.5),
                        force_points=(0.5, 0.5),
                        avoid_text=True,
                        avoid_points=True,
                        avoid_self=True)
    ax_main.set_xlabel(xlabel, fontsize=18)
    ax_main.set_ylabel(ylabel, fontsize=18)
    ax_main.set_title(title, fontsize=18)
    ax_main.legend(fontsize=16)
    ax_main.tick_params(axis='both', labelsize=16)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    if inset:
        return fig, ax_main, ax_inset
    else:
        return fig, ax_main

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./OUTPUT/{ID}_{score}_two_state.csv', index=False)
    

    if ID == "T1228" and score == 'GlobalLDDT':
        fig, ax_main, ax_inset = create_scatter(combined_df[f"Best_v1_ref"], \
                combined_df[f"Best_v2_ref"], \
                combined_df['Group'], f'{score} Score (V1)', \
                f'{score} Score (V2)', f'Scatter plot of {score} scores for \n {ID} V1 vs V2 reference states', \
                save_path=f'./PLOTS/{ID}_{score}_scatter_plot.png',
                inset=True,
                inset_position=[0.2, 0.05, 0.475, 0.475],   # [left, bottom, width, height]
                inset_xlim=[0.74, 0.78],
                inset_ylim=[0.70, 0.75],
                inset_xticks=[0.74, 0.75, 0.76, 0.77, 0.78],  # [0.0, 0.5]
                inset_yticks=[0.70, 0.72, 0.74, 0.75],
                highlight_inset_rect=True,
                rect_xy=(0.74, 0.70),
                rect_width=0.04,
                rect_height=0.05,
                )
    elif ID == "T1249" and score == "GlobalLDDT":
        fig, ax_main, ax_inset = create_scatter(combined_df[f"Best_v1_ref"], \
                combined_df[f"Best_v2_ref"], \
                combined_df['Group'], f'{score} Score (V1)', \
                f'{score} Score (V2)', f'Scatter plot of {score} scores for \n {ID} V1 vs V2 reference states', \
                save_path=f'./PLOTS/{ID}_{score}_scatter_plot.png',
                inset=True,
                inset_position=[0.25, 0.05, 0.475, 0.475],   # [left, bottom, width, height]
                inset_xlim=[0.74, 0.82],
                inset_ylim=[0.70, 0.8],
                inset_xticks=[0.74, 0.76, 0.78, 0.80, 0.82],
                inset_yticks=[0.70, 0.72, 0.74, 0.76, 0.78, 0.80],
                highlight_inset_rect=True,
                rect_xy=(0.74, 0.70),
                rect_width=0.08,
                rect_height=0.1,
                )
    elif ID == "T1239" and score == "GlobalLDDT":
        fig, ax_main, ax_inset = create_scatter(combined_df[f"Best_v1_ref"], \
                combined_df[f"Best_v2_ref"], \
                combined_df['Group'], f'{score} Score (V1)', \
                f'{score} Score (V2)', f'Scatter plot of {score} scores for \n {ID} V1 vs V2 reference states', \
                save_path=f'./PLOTS/{ID}_{score}_scatter_plot.png',
                inset=True,
                inset_position=[0.25, 0.05, 0.475, 0.475],   # [left, bottom, width, height]
                inset_xlim=[0.66, 0.84],
                inset_ylim=[0.72, 0.86],
                inset_xticks=[0.66, 0.72, 0.78, 0.84],
                inset_yticks=[0.72, 0.78, 0.84, 0.86],
                highlight_inset_rect=True,
                rect_xy=(0.66, 0.72),
                rect_width=0.18,
                rect_height=0.14,
                )
    elif ID == "R1203" and score == "GlobalLDDT":
        fig, ax_main, ax_inset = create_scatter(combined_df[f"Best_v1_ref"], \
                combined_df[f"Best_v2_ref"], \
                combined_df['Group'], f'{score} Score (V1)', \
                f'{score} Score (V2)', f'Scatter plot of {score} scores for \n {ID} V1 vs V2 reference states', \
                save_path=f'./PLOTS/{ID}_{score}_scatter_plot.png',
                inset=True,
                inset_position=[0.25, 0.05, 0.475, 0.475],   # [left, bottom, width, height]
                inset_xlim=[0.68, 0.84],
                inset_ylim=[0.68, 0.84],
                inset_xticks=[0.68, 0.74, 0.80, 0.84],
                inset_yticks=[0.68, 0.74, 0.80, 0.84],
                highlight_inset_rect=True,
                rect_xy=(0.68, 0.68),
                rect_width=0.16,
                rect_height=0.16,
                )
    else:
        fig, ax_main = create_scatter(combined_df[f"Best_v1_ref"], \
                    combined_df[f"Best_v2_ref"], \
                    combined_df['Group'], f'{score} Score (V1)', \
                    f'{score} Score (V2)', f'Scatter plot of {score} scores for \n {ID} V1 vs V2 reference states', \
                    save_path=f'./PLOTS/{ID}_{score}_scatter_plot.png')

    
    # Create a stacked bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df[f'Best_v1_ref'], label=f'<{score}> (V1)')
    plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df[f'Best_v2_ref'], bottom=combined_df[f'Best_v1_ref'], label=f'<{score}> (V2)')
    plt.xlabel('Submission Group', fontsize=18)
    plt.ylabel('Two-State Score', fontsize=18)
    plt.title(f'Aggregate {score} scores for \n {ID} V1 and V2 reference states', fontsize=18)
    plt.legend(loc='upper right', fontsize=16)
    plt.xticks(rotation=90, fontsize=10)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    # Save the plot as an image file
    
    plt.savefig(f'./PLOTS/{ID}_{score}_two_state.png', dpi=300)


TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "R1203": ["GDT_TS", "GlobalLDDT", "Composite_Score_4"], 
                     "T1228": ["GDT_TS", "GlobalLDDT"], 
                     "T1239": ["GDT_TS", "GlobalLDDT"], 
                     "T1249": ["AvgDockQ", "GlobalLDDT"]}

assessment("R1203", "GlobalLDDT")
assessment("R1203", "Composite_Score_4")
assessment("R1203", "GDT_TS")
raise Exception("Stop here")

for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            continue

