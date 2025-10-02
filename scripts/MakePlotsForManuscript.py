
from process_two_state_score import get_v1_ref_df, get_v2_ref_df, get_best_fit, get_best_fit_single_state, create_stacked_bar, create_scatter, frange

def Figure1_C():
    # Creates figure 1C - Single state plot for T1214 Composite_Score_4
    v1_df = get_v1_ref_df('T1214', 'Composite_Score_4')
    combined_df = get_best_fit_single_state('T1214', v1_df, 'Composite_Score_4')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plots
    create_stacked_bar(combined_df, 'T1214', 'Composite_Score_4', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_no_star", save_path="./output/PLOTS_MANUSCRIPT/Figure1_C.png",
                      single_state=True, ylabel='Single-State Score', baseline_color='gray', v1_color_304='cyan',
                      tick_fs_prim_vertical=20, tick_fs_sec_vertical=28, label_fontsize=28,
                      output_dir='./output/PLOTS_MANUSCRIPT')
    
    create_stacked_bar(combined_df, 'T1214', 'Composite_Score_4', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_no_star", save_path="./output/PLOTS_MANUSCRIPT/FigS1.png",
                      single_state=True, ylabel='Single-State Score', baseline_color='gray', v1_color_304='cyan',
                      tick_fs_prim_vertical=20, tick_fs_sec_vertical=28, label_fontsize=28,
                      output_dir='./output/PLOTS_MANUSCRIPT')

def Figure2_B_C():
    # Creates figure 2B and C - Two state plots for M1228 TMscore
    v1_df = get_v1_ref_df('M1228', 'TMscore')
    v2_df = get_v2_ref_df('M1228', 'TMscore')
    combined_df = get_best_fit('M1228', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plots
    create_stacked_bar(combined_df, 'M1228', 'TMscore', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/Figure2_B.png",
                      fig_width_vertical=16, fig_height_vertical=12, output_dir='./output/PLOTS_MANUSCRIPT',
                      tick_fs_prim_vertical=24, tick_fs_sec_vertical=28, label_fontsize=28)
    
    create_stacked_bar(combined_df, 'M1228', 'TMscore', horizontal=True, star=False, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/FigS3_A1.png",
                      fig_width_horizontal=16, fig_height_horizontal=12, output_dir='./output/PLOTS_MANUSCRIPT',
                      tick_fs_prim_horizontal=24, tick_fs_sec_horizontal=28, label_fontsize=28)

    # Create scatter plots
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/Figure2_C.png',
        'score': 'TMscore',
        'xlabel': 'TM-score (V1)',
        'ylabel': 'TM-score (V2)',
        'title': 'Scatter plot of Combined TM-score for \n M1228 V1 vs V2 reference states',
        'main_xlim': (0.6, 0.8),
        'ylim': (0.65, 0.85),
        'xticks': [round(x, 2) for x in list(frange(0.6, 0.8+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.65, 0.85+0.001, 0.05))],
        'AF3_baseline': True,
        'text_fontsize': 16
    }
    create_scatter(**scatter_kwargs)
    
    scatter_kwargs['save_path'] = "./output/PLOTS_MANUSCRIPT/FigS3_A2.png"
    create_scatter(**scatter_kwargs)

def Figure4_C():
    # Creates figure 4C - Two state plots for T1228 GDT_TS
    v1_df = get_v1_ref_df('T1228', 'GDT_TS')
    v2_df = get_v2_ref_df('T1228', 'GDT_TS')
    combined_df = get_best_fit('T1228', v1_df, v2_df, 'GDT_TS')
    combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100
    combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plots with larger axis labels and ticks
    create_stacked_bar(
        combined_df, 'T1228', 'GDT_TS', horizontal=True, star=True, 
        outfile_suffix="_vertical_star", 
        save_path="./output/PLOTS_MANUSCRIPT/Figure4_C.png",
        output_dir='./output/PLOTS_MANUSCRIPT',
        label_fontsize=24,  # Larger axis label font size
        tick_fs_prim_horizontal=20,  # Larger primary axis tick font size
        tick_fs_sec_horizontal=20    # Larger secondary axis tick font size
    )

    create_stacked_bar(
        combined_df, 'T1228', 'GDT_TS', horizontal=False, star=True, 
        outfile_suffix="_vertical_star", 
        save_path="./output/PLOTS_MANUSCRIPT/FigS4A1.png",
        output_dir='./output/PLOTS_MANUSCRIPT',
        label_fontsize=24,  # Larger axis label font size
        tick_fs_prim_vertical=20,    # Larger primary axis tick font size
        tick_fs_sec_vertical=20      # Larger secondary axis tick font size
    )
    
    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS4A2.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': 'GDT_TS Score (V1)',
        'ylabel': 'GDT_TS Score (V2)',
        'title': 'Scatter plot of Combined GDT_TS scores for \n T1228 V1 vs V2 reference states',
        'text_fontsize': 12
    }
    create_scatter(**scatter_kwargs)

def Figure5_C():
    # Creates figure 5C - Two state scatter plots for M1239 TMscore and T1239 GDT_TS
    
    # M1239 TMscore
    v1_df = get_v1_ref_df('M1239', 'TMscore')
    v2_df = get_v2_ref_df('M1239', 'TMscore')
    combined_df = get_best_fit('M1239', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
   
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/Figure5_C1.png',
        'score': 'TMscore',
        'AF3_baseline': True,
        'xlabel': 'TM-score (V1)',
        'ylabel': 'TM-score (V2)',
        'title': 'Scatter plot of Combined TM-score for \n M1239 V1 vs V2 reference states',
        'text_fontsize': 12,
        'AF3_fill_between': False
    }
    create_scatter(**scatter_kwargs)

    # T1239 GDT_TS
    v1_df = get_v1_ref_df('T1239', 'GDT_TS')
    v2_df = get_v2_ref_df('T1239', 'GDT_TS')
    combined_df = get_best_fit('T1239', v1_df, v2_df, 'GDT_TS')
    combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100
    combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    # Convert GDT_TS scores to percentage
        
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
   
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/Figure5_C2.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': 'GDT_TS Score (V1)',
        'ylabel': 'GDT_TS Score (V2)',
        'title': 'Scatter plot of Combined GDT_TS scores for \n T1239 V1 vs V2 reference states',
        'text_fontsize': 12,
        'AF3_fill_between': False
    }
    create_scatter(**scatter_kwargs)

def Figure6_B_C():
    # Creates figure 6B and C - Two state plots for T1249 AvgDockQ
    v1_df = get_v1_ref_df('T1249', 'AvgDockQ')
    v2_df = get_v2_ref_df('T1249', 'AvgDockQ')
    combined_df = get_best_fit('T1249', v1_df, v2_df, 'AvgDockQ')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plots
    create_stacked_bar(combined_df, 'T1249', 'AvgDockQ', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/Figure6_B.png",
                      output_dir='./output/PLOTS_MANUSCRIPT', ylim=(0, 1.0))
    
    create_stacked_bar(combined_df, 'T1249', 'AvgDockQ', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/FigS8A1.png",
                      output_dir='./output/PLOTS_MANUSCRIPT', ylim=(0, 1.0))

    # Create scatter plots
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/Figure6_C.png',
        'score': 'DockQ',
        'AF3_baseline': True,
        'xlabel': 'DockQ Score (V1)',
        'ylabel': 'DockQ Score (V2)',
        'title': 'Scatter plot of Combined DockQ scores for \n T1249 V1 vs V2 reference states'
    }
    create_scatter(**scatter_kwargs)
    
    scatter_kwargs['save_path'] = "./output/PLOTS_MANUSCRIPT/FigS8A2.png"
    create_scatter(**scatter_kwargs)

def Figure7_C_D():
    # Creates figure 7C and D - Two state plots for R1203 Composite_Score_4
    v1_df = get_v1_ref_df('R1203', 'Composite_Score_4')
    v2_df = get_v2_ref_df('R1203', 'Composite_Score_4')
    combined_df = get_best_fit('R1203', v1_df, v2_df, 'Composite_Score_4')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plots
    create_stacked_bar(combined_df, 'R1203', 'Composite_Score_4', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/Figure7_C.png",
                      output_dir='./output/PLOTS_MANUSCRIPT')
    
    create_stacked_bar(combined_df, 'R1203', 'Composite_Score_4', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/FigS9A1.png",
                      output_dir='./output/PLOTS_MANUSCRIPT')

    # Create scatter plots
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/Figure7_D.png',
        'score': 'Composite_Score_4',
        'AF3_baseline': True,
        'xlabel': 'Composite Score (V1)',
        'ylabel': 'Composite Score (V2)',
        'title': 'Scatter plot of Combined Composite Score scores for \n R1203 V1 vs V2 reference states'
    }
    
    create_scatter(**scatter_kwargs)
    scatter_kwargs['save_path'] = "./output/PLOTS_MANUSCRIPT/FigS9A2.png"
    create_scatter(**scatter_kwargs)

def FigS3():
    # Creates figure S3 - M1228 GDT_TS and GlobDockQ
    
    # M1228 GDT_TS
    v1_df = get_v1_ref_df('M1228', 'GDT_TS')
    v2_df = get_v2_ref_df('M1228', 'GDT_TS')
    combined_df = get_best_fit('M1228', v1_df, v2_df, 'GDT_TS')
    combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100
    combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
    # Convert GDT_TS scores to percentage

    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'M1228', 'GDT_TS', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/FigS3_B.png",
                      output_dir='./output/PLOTS_MANUSCRIPT',
                      fig_width_vertical=16, fig_height_vertical=8,
                      tick_fs_prim_vertical=24, tick_fs_sec_vertical=28, label_fontsize=28)
    
    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS3_C.png',
        'score': 'GDT_TS',
        'xlabel': 'GDT_TS Score (V1)',
        'ylabel': 'GDT_TS Score (V2)',
        'title': 'Scatter plot of Combined GDT_TS scores for \n M1228 V1 vs V2 reference states',
        'main_xlim': (10, 40),
        'ylim': (10, 40),
        'xticks': [round(x, 2) for x in list(frange(10, 40+0.001, 5))],
        'yticks': [round(y, 2) for y in list(frange(10, 40+0.001, 5))],
        'AF3_baseline': True,
        'text_fontsize': 12
    }
    create_scatter(**scatter_kwargs)
    
    # M1228 GlobDockQ
    v1_df = get_v1_ref_df('M1228', 'GlobDockQ')
    v2_df = get_v2_ref_df('M1228', 'GlobDockQ')
    combined_df = get_best_fit('M1228', v1_df, v2_df, 'GlobDockQ')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)

    # Create stacked bar plot
    create_stacked_bar(combined_df, 'M1228', 'GlobDockQ', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/FigS3_D.png",
                      output_dir='./output/PLOTS_MANUSCRIPT',
                      fig_width_vertical=16, fig_height_vertical=8,
                      tick_fs_prim_vertical=24, tick_fs_sec_vertical=28, label_fontsize=28)
    
    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS3_E.png',
        'score': 'GlobDockQ',
        'xlabel': 'GlobDockQ Score (V1)',
        'ylabel': 'GlobDockQ Score (V2)',
        'title': 'Scatter plot of Combined GlobDockQ scores for \n M1228 V1 vs V2 reference states',
        'main_xlim': (0.20, 0.40),
        'ylim': (0.20, 0.40),
        'xticks': [round(x, 2) for x in list(frange(0.20, 0.40+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.20, 0.40+0.001, 0.05))],
        'AF3_baseline': True,
        'text_fontsize': 12
    }
    create_scatter(**scatter_kwargs)

def FigS5():
    # Creates figure S5 - M1239 GDT_TS and GlobDockQ
    
    # M1239 GDT_TS
    v1_df = get_v1_ref_df('M1239', 'GDT_TS')
    v2_df = get_v2_ref_df('M1239', 'GDT_TS')
    combined_df = get_best_fit('M1239', v1_df, v2_df, 'GDT_TS')
    combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100
    combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'M1239', 'GDT_TS', horizontal=False, star=True, 
                      save_path="./output/PLOTS_MANUSCRIPT/FigS5_B.png",
                      output_dir='./output/PLOTS_MANUSCRIPT',
                      fig_width_vertical=16, fig_height_vertical=8,
                      tick_fs_prim_vertical=24, tick_fs_sec_vertical=28, label_fontsize=28)
    
    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS5_C.png',
        'score': 'GDT_TS',
        'xlabel': 'GDT_TS Score (V1)',
        'ylabel': 'GDT_TS Score (V2)',
        'title': 'Scatter plot of Combined GDT_TS scores for \n M1239 V1 vs V2 reference states',
        'xlim': (14, 32),
        'ylim': (14, 30),
        'xticks': [round(x, 2) for x in list(frange(14, 32+0.001, 2))],
        'yticks': [round(y, 2) for y in list(frange(14, 30+0.001, 2))],
        'text_fontsize': 12
    }
    create_scatter(**scatter_kwargs)
    
    # M1239 GlobDockQ
    v1_df = get_v1_ref_df('M1239', 'GlobDockQ')
    v2_df = get_v2_ref_df('M1239', 'GlobDockQ')
    combined_df = get_best_fit('M1239', v1_df, v2_df, 'GlobDockQ')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'M1239', 'GlobDockQ', horizontal=False, star=True, 
                      outfile_suffix="_horizontal_star", save_path="./output/PLOTS_MANUSCRIPT/FigS5_D.png",
                      output_dir='./output/PLOTS_MANUSCRIPT',
                      fig_width_vertical=16, fig_height_vertical=8,
                      tick_fs_prim_vertical=24, tick_fs_sec_vertical=28, label_fontsize=28)
    
    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS5_E.png',
        'score': 'GlobDockQ',
        'xlabel': 'GlobDockQ Score (V1)',
        'ylabel': 'GlobDockQ Score (V2)',
        'title': 'Scatter plot of Combined GlobDockQ scores for \n M1239 V1 vs V2 reference states',
        'xlim': (0.15, 0.40),
        'ylim': (0.15, 0.40),
        'xticks': [round(x, 2) for x in list(frange(0.15, 0.40+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.15, 0.40+0.001, 0.05))],
        'text_fontsize': 12
    }
    create_scatter(**scatter_kwargs)

def FigS6():
    # Create Figure S6 - M1228 and M1239 TMscore
    
    # M1228 TMscore
    v1_df = get_v1_ref_df('M1228', 'TMscore')
    v2_df = get_v2_ref_df('M1228', 'TMscore')
    combined_df = get_best_fit('M1228', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'M1228', 'TMscore', horizontal=True, star=True, 
                      outfile_suffix="_vertical_star", save_path="./output/PLOTS_MANUSCRIPT/FigS6_A.png",
                      output_dir='./output/PLOTS_MANUSCRIPT')

    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS6_B.png',
        'score': 'TMscore',
        'xlabel': 'TM-score (V1)',
        'ylabel': 'TM-score (V2)',
        'title': 'Scatter plot of Combined TM-score for \n M1228 V1 vs V2 reference states',
        'main_xlim': (0.6, 0.8),
        'ylim': (0.65, 0.85),
        'xticks': [round(x, 2) for x in list(frange(0.6, 0.8+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.65, 0.85+0.001, 0.05))],
        'AF3_baseline': True,
        'text_fontsize': 12
    }
    create_scatter(**scatter_kwargs)

    # M1239 TMscore
    v1_df = get_v1_ref_df('M1239', 'TMscore')
    v2_df = get_v2_ref_df('M1239', 'TMscore')
    combined_df = get_best_fit('M1239', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'M1239', 'TMscore', horizontal=True, star=True, 
                      outfile_suffix="_vertical_star", save_path="./output/PLOTS_MANUSCRIPT/FigS6_C.png",
                      output_dir='./output/PLOTS_MANUSCRIPT')

    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS6_D.png',
        'score': 'TMscore',
        'xlabel': 'TM-score (V1)',
        'ylabel': 'TM-score (V2)',
        'title': 'Scatter plot of Combined TM-score for \n M1239 V1 vs V2 reference states',
        'text_fontsize': 12,
        'AF3_baseline': True,
        'AF3_fill_between': False,
    }
    create_scatter(**scatter_kwargs)

def FigS7():
    # Creates figure S7 - T1228 and T1239 GDT_TS
    
    # T1228 GDT_TS
    v1_df = get_v1_ref_df('T1228', 'GDT_TS')
    v2_df = get_v2_ref_df('T1228', 'GDT_TS')
    combined_df = get_best_fit('T1228', v1_df, v2_df, 'GDT_TS')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
    
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'T1228', 'GDT_TS', horizontal=True, star=True, 
                      outfile_suffix="_vertical_star", save_path="./output/PLOTS_MANUSCRIPT/FigS7_A.png",
                      output_dir='./output/PLOTS_MANUSCRIPT')
    
    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS7_B.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': 'GDT_TS Score (V1)',
        'ylabel': 'GDT_TS Score (V2)',
        'title': 'Scatter plot of Combined GDT_TS scores for \n T1228 V1 vs V2 reference states',
        'AF3_fill_between': False
    }
    create_scatter(**scatter_kwargs)

    # T1239 GDT_TS
    v1_df = get_v1_ref_df('T1239', 'GDT_TS')
    v2_df = get_v2_ref_df('T1239', 'GDT_TS')
    combined_df = get_best_fit('T1239', v1_df, v2_df, 'GDT_TS')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
    combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100
    
    # Create stacked bar plot
    create_stacked_bar(combined_df, 'T1239', 'GDT_TS', horizontal=True, star=True, 
                      outfile_suffix="_vertical_star", save_path="./output/PLOTS_MANUSCRIPT/FigS7_C.png",
                      output_dir='./output/PLOTS_MANUSCRIPT')

    # Create scatter plot
    scatter_kwargs = {
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './output/PLOTS_MANUSCRIPT/FigS7_D.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': 'GDT_TS Score (V1)',
        'ylabel': 'GDT_TS Score (V2)',
        'title': 'Scatter plot of Combined GDT_TS scores for \n T1239 V1 vs V2 reference states',
        'AF3_fill_between': False
    }
    create_scatter(**scatter_kwargs)

def FigS11():
    # Creates figure S11 - Multi-panel GDT/TM plot
    from process_TM_GDT_two_state_multipanel import assessment as assessment_TM_GDT
    from process_TM_GDT_two_state_multipanel import TARGET_SCORE_DICT as TARGET_SCORE_DICT_TM_GDT
    assessment_TM_GDT(TARGET_SCORE_DICT_TM_GDT, save_path="./output/PLOTS_MANUSCRIPT/FigS11.png")

def make_plots_for_manuscript():
    Figure1_C()
    Figure2_B_C()
    Figure4_C()
    Figure5_C()
    Figure6_B_C()
    Figure7_C_D()
    FigS3()
    FigS5()
    FigS6()
    FigS7()
    FigS11()


if __name__ == '__main__':
    make_plots_for_manuscript()