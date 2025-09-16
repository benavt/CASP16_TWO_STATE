
from process_single_state_score import get_v1_ref_df as get_v1_ref_df_single
from process_single_state_score import get_best_fit as get_best_fit_single
from process_single_state_score import create_stacked_bar as create_stacked_bar_single


from process_two_state_score import get_v1_ref_df as get_v1_ref_df_two
from process_two_state_score import get_v2_ref_df as get_v2_ref_df_two
from process_two_state_score import get_best_fit as get_best_fit_two
from process_two_state_score import create_stacked_bar as create_stacked_bar_two
from process_two_state_score import create_scatter as create_scatter_two
from process_two_state_score import frange as frange

def Figure1_C():
    # Creates figure 1C
    # horizontal 
    v1_df = get_v1_ref_df_single('T1214', 'Composite_Score_4')
    combined_df = get_best_fit_single('T1214', v1_df, 'Composite_Score_4')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_single(combined_df, 'T1214', 'Composite_Score_4', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_no_star", save_path = "./PLOTS_MANUSCRIPT/Figure1_C.png")
    create_stacked_bar_single(combined_df, 'T1214', 'Composite_Score_4', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_no_star", save_path = "./PLOTS_MANUSCRIPT/FigS1.png")

def Figure2_B_C():
    # Creates figure 2B and C
    # horizontal
    v1_df = get_v1_ref_df_two('M1228', 'TMscore')
    v2_df = get_v2_ref_df_two('M1228', 'TMscore')
    combined_df = get_best_fit_two('M1228', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1228', 'TMscore', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/Figure2_B.png")
    create_stacked_bar_two(combined_df, 'M1228', 'TMscore', horizontal=True, \
        star=False, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS3_A1.png")

    kwargs = {}
    kwargs['text_fontsize'] = 16

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df["Best_v1_ref"],
        'y': combined_df["Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': './PLOTS_MANUSCRIPT/Figure2_C.png',
        'score': 'TMscore',
        'xlabel': 'TM-score (V1)',
        'ylabel': 'TM-score (V2)',
        'title': 'Scatter plot of Combined TM-score for \n M1228 V1 vs V2 reference states',
        'main_xlim': (0.6, 0.8),
        'ylim': (0.65, 0.85),
        'xticks': [round(x, 2) for x in list(frange(0.6, 0.8+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.65, 0.85+0.001, 0.05))],
        'AF3_baseline': True
    })
    create_scatter_two(**kwargs)
    kwargs['save_path'] = "./PLOTS_MANUSCRIPT/FigS3_A2.png"
    create_scatter_two(**kwargs)

def Figure4_C():
    # Creates figure 4C
    # horizontal
    v1_df = get_v1_ref_df_two('T1228', 'GDT_TS')
    v2_df = get_v2_ref_df_two('T1228', 'GDT_TS')
    # Convert GDT_TS scores to percentage
    
    combined_df = get_best_fit_two('T1228', v1_df, v2_df, 'GDT_TS')
    
    if max(combined_df['Best_v1_ref']) <= 1:
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    if max(combined_df['Best_v2_ref']) <= 1:
        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'T1228', 'GDT_TS', horizontal=True, \
        star=True, outfile_suffix = "_vertical_star", save_path = "./PLOTS_MANUSCRIPT/Figure4_C.png")
    create_stacked_bar_two(combined_df, 'T1228', 'GDT_TS', horizontal=False, \
        star=True, outfile_suffix = "_vertical_star", save_path = "./PLOTS_MANUSCRIPT/FigS4A1.png")
    kwargs = {}
    kwargs['text_fontsize'] = 12

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS4A2.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': f'GDT_TS Score (V1)',
        'ylabel': f'GDT_TS Score (V2)',
        'title': f'Scatter plot of Combined GDT_TS scores for \n T1228 V1 vs V2 reference states',
    })
    create_scatter_two(**kwargs)

def Figure5_C():
    # Creates figure 5C
    v1_df = get_v1_ref_df_two('M1239', 'TMscore')
    v2_df = get_v2_ref_df_two('M1239', 'TMscore')
    combined_df = get_best_fit_two('M1239', v1_df, v2_df, 'TMscore')

    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
   
    kwargs = {}
    kwargs['text_fontsize'] = 12

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/Figure5_C1.png',
        'score': 'TMscore',
        'AF3_baseline': True,
        'xlabel': f'TM-score (V1)',
        'ylabel': f'TM-score (V2)',
        'title': f'Scatter plot of Combined TM-score for \n M1239 V1 vs V2 reference states',
    })
    create_scatter_two(**kwargs)

    # Creates figure 5C T1239 GDT_TS
    v1_df = get_v1_ref_df_two('T1239', 'GDT_TS')
    v2_df = get_v2_ref_df_two('T1239', 'GDT_TS')
    combined_df = get_best_fit_two('T1239', v1_df, v2_df, 'GDT_TS')

    if max(combined_df['Best_v1_ref']) <= 1:
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    if max(combined_df['Best_v2_ref']) <= 1:
        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
        
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
   
    kwargs = {}
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/Figure5_C2.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': f'GDT_TS Score (V1)',
        'ylabel': f'GDT_TS Score (V2)',
        'title': f'Scatter plot of Combined GDT_TS scores for \n T1239 V1 vs V2 reference states',
    })
    create_scatter_two(**kwargs)

def Figure6_B_C():
    # Creates figure 6B and C
    # horizontal
    v1_df = get_v1_ref_df_two('T1249', 'AvgDockQ')
    v2_df = get_v2_ref_df_two('T1249', 'AvgDockQ')
    combined_df = get_best_fit_two('T1249', v1_df, v2_df, 'AvgDockQ')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'T1249', 'AvgDockQ', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/Figure6_B.png")
    create_stacked_bar_two(combined_df, 'T1249', 'AvgDockQ', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS8A1.png")

    kwargs = {}
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/Figure6_C.png',
        'score': 'DockQ',
        'AF3_baseline': True,
        'xlabel': f'DockQ Score (V1)',
        'ylabel': f'DockQ Score (V2)',
        'title': f'Scatter plot of Combined DockQ scores for \n T1249 V1 vs V2 reference states',
    })
    create_scatter_two(**kwargs)
    kwargs['save_path'] = "./PLOTS_MANUSCRIPT/FigS8A2.png"
    create_scatter_two(**kwargs)

def Figure7_C_D():
    # Creates figure 7C and D
    # R1203 Composite_Score_4
    v1_df = get_v1_ref_df_two('R1203', 'Composite_Score_4')
    v2_df = get_v2_ref_df_two('R1203', 'Composite_Score_4')
    combined_df = get_best_fit_two('R1203', v1_df, v2_df, 'Composite_Score_4')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'R1203', 'Composite_Score_4', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/Figure7_C.png")
    create_stacked_bar_two(combined_df, 'R1203', 'Composite_Score_4', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS9A1.png")

    kwargs = {}
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/Figure7_D.png',
        'score': 'Composite_Score_4',
        'AF3_baseline': True,
        'xlabel': f'Composite Score (V1)',
        'ylabel': f'Composite Score (V2)',
        'title': f'Scatter plot of Combined Composite Score scores for \n R1203 V1 vs V2 reference states',
    })
    
    create_scatter_two(**kwargs)
    kwargs['save_path'] = "./PLOTS_MANUSCRIPT/FigS9A2.png"
    create_scatter_two(**kwargs)

def FigS3():
    # Creates figure S3
    # M1228 GDT_TS and GlobDockQ
    v1_df = get_v1_ref_df_two('M1228', 'GDT_TS')
    v2_df = get_v2_ref_df_two('M1228', 'GDT_TS')
    
    combined_df = get_best_fit_two('M1228', v1_df, v2_df, 'GDT_TS')
    # Convert GDT_TS scores to percentage
    if max(combined_df['Best_v1_ref']) <= 1:
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
    if max(combined_df['Best_v2_ref']) <= 1:
        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1228', 'GDT_TS', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS3_B.png")
    kwargs = {}
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS3_C.png',
        'score': 'GDT_TS'
    })
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'xlabel': f'GDT_TS Score (V1)',
        'ylabel': f'GDT_TS Score (V2)',
        'title': f'Scatter plot of Combined GDT_TS scores for \n M1228 V1 vs V2 reference states',
        'main_xlim': (10, 40),
        'ylim': (10, 40),
        'xticks': [round(x, 2) for x in list(frange(10, 40+0.001, 5))],
        'yticks': [round(y, 2) for y in list(frange(10, 40+0.001, 5))],
        'AF3_baseline': True
    })
    create_scatter_two(**kwargs)
    v1_df = get_v1_ref_df_two('M1228', 'GlobDockQ')
    v2_df = get_v2_ref_df_two('M1228', 'GlobDockQ')
    combined_df = get_best_fit_two('M1228', v1_df, v2_df, 'GlobDockQ')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1228', 'GlobDockQ', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS3_D.png")
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS3_E.png',
        'score': 'GlobDockQ',
        'xlabel': f'GlobDockQ Score (V1)',
        'ylabel': f'GlobDockQ Score (V2)',
        'title': f'Scatter plot of Combined GlobDockQ scores for \n M1228 V1 vs V2 reference states',
        'main_xlim': (0.20, 0.40),
        'ylim': (0.20, 0.40),
        'xticks': [round(x, 2) for x in list(frange(0.20, 0.40+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.20, 0.40+0.001, 0.05))],
        'AF3_baseline': True
    })
    create_scatter_two(**kwargs)

def FigS5():
    # creates figure S5
    # M1239 GDT_TS and GlobDockQ
    v1_df = get_v1_ref_df_two('M1239', 'GDT_TS')
    v2_df = get_v2_ref_df_two('M1239', 'GDT_TS')
    combined_df = get_best_fit_two('M1239', v1_df, v2_df, 'GDT_TS')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1239', 'GDT_TS', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS5_B.png")
    kwargs = {}
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS5_C.png',
        'score': 'GDT_TS',
        'xlabel': f'GDT_TS Score (V1)',
        'ylabel': f'GDT_TS Score (V2)',
        'title': f'Scatter plot of Combined GDT_TS scores for \n M1239 V1 vs V2 reference states',
        'main_xlim': (10, 40),
        'ylim': (10, 40),
        'xticks': [round(x, 2) for x in list(frange(10, 40+0.001, 5))],
        'yticks': [round(y, 2) for y in list(frange(10, 40+0.001, 5))],
        'xlim': (14, 32),
        'ylim': (14, 30),
        'xticks': [round(x, 2) for x in list(frange(14, 32+0.001, 2))],
        'yticks': [round(y, 2) for y in list(frange(14, 30+0.001, 2))],
    })
    create_scatter_two(**kwargs)
    v1_df = get_v1_ref_df_two('M1239', 'GlobDockQ')
    v2_df = get_v2_ref_df_two('M1239', 'GlobDockQ')
    combined_df = get_best_fit_two('M1239', v1_df, v2_df, 'GlobDockQ')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1239', 'GlobDockQ', horizontal=False, \
        star=True, outfile_suffix = "_horizontal_star", save_path = "./PLOTS_MANUSCRIPT/FigS5_D.png")
    kwargs = {}
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS5_E.png',
        'score': 'GlobDockQ',
        'xlabel': f'GlobDockQ Score (V1)',
        'ylabel': f'GlobDockQ Score (V2)',
        'title': f'Scatter plot of Combined GlobDockQ scores for \n M1239 V1 vs V2 reference states',
        'main_xlim': (0.20, 0.40),
        'xlim': (0.15, 0.40),
        'ylim': (0.15, 0.40),
        'xticks': [round(x, 2) for x in list(frange(0.15, 0.40+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.15, 0.40+0.001, 0.05))],
    })
    create_scatter_two(**kwargs)

def FigS6():
    # Create Figure S6
    # M1228 TMscore
    # M1239 TMscore
    v1_df = get_v1_ref_df_two('M1228', 'TMscore')
    v2_df = get_v2_ref_df_two('M1228', 'TMscore')
    combined_df = get_best_fit_two('M1228', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1228', 'TMscore', horizontal=True, \
        star=True, outfile_suffix = "_vertical_star", save_path = "./PLOTS_MANUSCRIPT/FigS6_A.png")


    kwargs = {}
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS6_B.png',
        'score': 'TMscore',
        'xlabel': f'TM-score (V1)',
        'ylabel': f'TM-score (V2)',
        'title': f'Scatter plot of Combined TM-score for \n M1228 V1 vs V2 reference states',
        'main_xlim': (0.6, 0.8),
        'ylim': (0.65, 0.85),
        'xticks': [round(x, 2) for x in list(frange(0.6, 0.8+0.001, 0.05))],
        'yticks': [round(y, 2) for y in list(frange(0.65, 0.85+0.001, 0.05))],
        'AF3_baseline': True
    })
    create_scatter_two(**kwargs)


    v1_df = get_v1_ref_df_two('M1239', 'TMscore')
    v2_df = get_v2_ref_df_two('M1239', 'TMscore')
    combined_df = get_best_fit_two('M1239', v1_df, v2_df, 'TMscore')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'M1239', 'TMscore', horizontal=True, \
        star=True, outfile_suffix = "_vertical_star", save_path = "./PLOTS_MANUSCRIPT/FigS6_C.png")

    kwargs = {}
    kwargs['text_fontsize'] = 12
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS6_D.png',
        'score': 'TMscore',
        'xlabel': f'TM-score (V1)',
        'ylabel': f'TM-score (V2)',
        'title': f'Scatter plot of Combined TM-score for \n M1239 V1 vs V2 reference states',
    })
    create_scatter_two(**kwargs)

def FigS7():
    # creates figure S7
    # T1228 GDT_TS
    # T1239 GDT_TS
    v1_df = get_v1_ref_df_two('T1228', 'GDT_TS')
    v2_df = get_v2_ref_df_two('T1228', 'GDT_TS')
    combined_df = get_best_fit_two('T1228', v1_df, v2_df, 'GDT_TS')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'T1228', 'GDT_TS', horizontal=True, \
        star=True, outfile_suffix = "_vertical_star", save_path = "./PLOTS_MANUSCRIPT/FigS7_A.png")
    kwargs = {}
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS7_B.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': f'GDT_TS Score (V1)',
        'ylabel': f'GDT_TS Score (V2)',
        'title': f'Scatter plot of Combined GDT_TS scores for \n T1228 V1 vs V2 reference states',
    })
    create_scatter_two(**kwargs)

    v1_df = get_v1_ref_df_two('T1239', 'GDT_TS')
    v2_df = get_v2_ref_df_two('T1239', 'GDT_TS')
    combined_df = get_best_fit_two('T1239', v1_df, v2_df, 'GDT_TS')
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    create_stacked_bar_two(combined_df, 'T1239', 'GDT_TS', horizontal=True, \
        star=True, outfile_suffix = "_vertical_star", save_path = "./PLOTS_MANUSCRIPT/FigS7_C.png")

    kwargs = {}
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./PLOTS_MANUSCRIPT/FigS7_D.png',
        'score': 'GDT_TS',
        'AF3_baseline': True,
        'xlabel': f'GDT_TS Score (V1)',
        'ylabel': f'GDT_TS Score (V2)',
        'title': f'Scatter plot of Combined GDT_TS scores for \n T1239 V1 vs V2 reference states',
    })
    create_scatter_two( **kwargs)

def FigS11():
    from process_TM_GDT_two_state_multipanel import assessment as assessment_TM_GDT
    from process_TM_GDT_two_state_multipanel import TARGET_SCORE_DICT as TARGET_SCORE_DICT_TM_GDT
    assessment_TM_GDT(TARGET_SCORE_DICT_TM_GDT, save_path = "./PLOTS_MANUSCRIPT/FigS11.png")

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