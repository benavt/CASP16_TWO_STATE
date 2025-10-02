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
from process_two_state_score import frange, get_group_name_lookup, get_v1_ref_df, get_best_fit_single_state, create_stacked_bar



def get_best_fit(ID, v1_df, score):
    return get_best_fit_single_state(ID, v1_df, score)

# Note: directly using create_stacked_bar imported from process_two_state_score
# But we'll call it with single_state=True in assessment()

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, score)

    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)

    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_single_state.csv', index=False)
    

    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_vertical", single_state=True, ylabel='Single-State Score', baseline_color='gray', v1_color_304='cyan', tick_fs_prim_horizontal=18, tick_fs_sec_horizontal=18, tick_fs_prim_vertical=18, tick_fs_sec_vertical=18, output_dir='./output/PLOTS')
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_horizontal", single_state=True, ylabel='Single-State Score', baseline_color='gray', v1_color_304='cyan', tick_fs_prim_horizontal=18, tick_fs_sec_horizontal=18, tick_fs_prim_vertical=18, tick_fs_sec_vertical=18, output_dir='./output/PLOTS')
    print(f"Done creating stacked bar plots for {ID} {score}")


if __name__ == "__main__":
    TARGET_SCORE_DICT = {"T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4"]}

    for ID, scores in TARGET_SCORE_DICT.items():
        for score in scores:
            try:
                assessment(ID, score)
                print(f"[SUCCESS] Processed {ID} {score}")
            except Exception as e:
                print(f"[ERROR] Error processing {ID} {score}: {e}")
                raise Exception("Stop here")
                continue

