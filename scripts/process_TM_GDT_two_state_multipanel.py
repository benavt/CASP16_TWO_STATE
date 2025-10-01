"""
MIT License

Copyright (c) 2025 Tiburon Leon Benavides

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Author: Tiburon Leon Benavides
Contribution: Main contributor
Date: 2025-09-01
"""

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv
from os.path import exists
from process_two_state_score_full_axis import create_scatter_full_axis
from process_two_state_score import get_v1_ref_df, get_v2_ref_df, frange, get_group_name_lookup, get_best_fit


# get_best_fit function is now imported from process_two_state_score


TARGET_SCORE_DICT = {"M1228": ["GDT_TS", "TMscore"], 
                     "M1239": ["GDT_TS", "TMscore"], 
                     "T1249": ["GDT_TS", "TMscore"], 
                     "T1228": ["GDT_TS", "TMscore"], 
                     "T1239": ["GDT_TS", "TMscore"],
                     "R1203": ["GDT_TS", "TMscore"],
                     }

def assessment(TARGET_SCORE_DICT, output_dir = "./PLOTS", save_path = None):

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
                    if max(combined_df['Best_v1_ref']) < 1:
                        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
                    if max(combined_df['Best_v2_ref']) < 1:
                        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

                # Save the combined metric to a CSV file
                combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_two_state.csv', index=False)
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
        subfix, subax = create_scatter_full_axis(**kwargs)
        # ax = subax

    plt.tight_layout()
    

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.savefig(f'./output/{output_dir}/GDT_TM_multi_panel.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return


assessment(TARGET_SCORE_DICT, output_dir = "./PLOTS", save_path = None)


