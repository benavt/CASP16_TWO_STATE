import glob
import pandas as pd
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
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
plt.xlabel(f'Best Global_GDT V1A ref', fontsize=18)
plt.ylabel(f'Best Global_GDT V1B ref', fontsize=18)
plt.title(f'Scatter plot of best Global_GDT scores for 1239 V1A vs V1B', fontsize=18)
plt.legend(fontsize=16)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
# Save the plot as an image file
plt.savefig(f'../PLOTS/T1239_combined_scatter_plot.png')
# plt.show()
plt.cla()

combined_df['Combined_Score'] = combined_df['V1A_final_fit'] + combined_df['V1B_final_fit']
 
import matplotlib.pyplot as plt

# Sort the combined_df by 'Combined_Score' in descending order
combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
# Save the combined metric to a CSV file
combined_df.to_csv('T1239_combined_metric.csv', index=False)
# Create a stacked bar chart
plt.figure(figsize=(10, 6))
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
plt.savefig('../PLOTS/T1239_combined_metric_plot.png')
