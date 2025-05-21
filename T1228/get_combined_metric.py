import glob
import pandas as pd
import matplotlib.pyplot as plt
from get_global_gdt import combine_gdt_scores

# Turn off interactive mode to suppress output
plt.ioff()

# Load the input dataframes with the correct paths
V1A_df = pd.read_csv('./V1A/best_global_gdt_combined_sorted_descending.csv')
V1B_df = pd.read_csv('./V1B/best_global_gdt_combined_sorted_descending.csv')
V1A_by_v1 = pd.read_csv('./V1A/best_global_gdt_by_group_v1.csv')
V1A_by_v2 = pd.read_csv('./V1A/best_global_gdt_by_group_v2.csv')
V1B_by_v1 = pd.read_csv('./V1B/best_global_gdt_by_group_v1.csv')
V1B_by_v2 = pd.read_csv('./V1B/best_global_gdt_by_group_v2.csv')

# Get the combined results using the imported function
combined_df = combine_gdt_scores(
    V1A_df=V1A_df,
    V1B_df=V1B_df,
    V1A_by_v1=V1A_by_v1,
    V1A_by_v2=V1A_by_v2,
    V1B_by_v1=V1B_by_v1,
    V1B_by_v2=V1B_by_v2,
    metric='Global_GDT'
)

# Save the combined metric to a CSV file
combined_df.to_csv('combined_metric.csv', index=False)

# Create a stacked bar chart
plt.figure(figsize=(10, 6))
plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df['V1A_final_fit'], label='<GDT_TS> (V1A)')
plt.bar(combined_df['Group'].str.replace('TS', ''), combined_df['V1B_final_fit'], bottom=combined_df['V1A_final_fit'], label='<GDT_TS> (V1B)')
plt.xlabel('Group', fontsize=18)
plt.ylabel('Score', fontsize=18)
plt.title('Aggregate Global GDT_TS scores for T1228 V1A and V1B', fontsize=18)
plt.legend(loc='upper right', fontsize=16)
plt.xticks(rotation=90, fontsize=8)
plt.yticks(fontsize=18)

# Save the plot as an image file
plt.savefig('../PLOTS/T1228_combined_metric_plot.png')