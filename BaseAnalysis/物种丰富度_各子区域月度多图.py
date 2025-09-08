import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib

# Set the font to support English and other characters properly
matplotlib.rcParams['font.sans-serif'] = ['Arial']  # Using Arial font
matplotlib.rcParams['axes.unicode_minus'] = False  # Properly display the minus sign

# Update to your local file path
input_file_path = r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv'

# Read CSV file
data = pd.read_csv(input_file_path)

# Filter out records where 'Count' is 0 and create a new DataFrame using .copy()
filtered_data = data[data['Count'] > 0].copy()

# Convert 'Date' to datetime format
filtered_data['Date'] = pd.to_datetime('2023-' + filtered_data['Date'], format='%Y-%d-%b')

# Group by 'Region' and month, and calculate species richness for each group
species_richness_by_region_month = filtered_data.groupby(['Region', filtered_data['Date'].dt.to_period('M')])['Species'].nunique().reset_index()
species_richness_by_region_month.columns = ['Region', 'Date', 'Species_Richness']

# Generate a standard range of months (January to November of 2023)
all_months = pd.period_range('2023-01', '2023-11', freq='M')

# Function to sort 'Region' name based on numbers and letters while preserving case
def region_sort_key(region):
    number = ''
    letter = ''
    for char in region:
        if char.isdigit():
            number += char
        else:
            letter += char
    return (int(number) if number else 0, letter)

# Sort data by 'Region' and 'Date'
species_richness_by_region_month['Sort_Region'] = species_richness_by_region_month['Region'].apply(region_sort_key)
species_richness_by_region_month = species_richness_by_region_month.sort_values(by=['Sort_Region', 'Date'])

# Remove the temporary sort column
species_richness_by_region_month = species_richness_by_region_month.drop(columns=['Sort_Region'])

# Get unique regions
regions = species_richness_by_region_month['Region'].unique()

# Set plot style
sns.set(style="whitegrid")

# Set the y-axis range for all subplots
y_min = 0
y_max = 12

# Calculate the number of rows needed for a 7-column layout
n_cols = 7
n_rows = -(-len(regions) // n_cols)  # Ceiling division to determine number of rows

# Create a figure for all the subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(24, 3 * n_rows))  # No shared axes

# Flatten the axes for easier iteration (handles both single and multi-row cases)
axes = axes.flatten()

# Loop through each region to plot
for i, region in enumerate(regions):
    # Extract data for the current region
    region_data = species_richness_by_region_month[species_richness_by_region_month['Region'] == region]
    region_data = region_data.set_index('Date')  # Set 'Date' as the index
    region_data = region_data.reindex(all_months).reset_index()  # Reindex to include all months but keep NaN for missing months

    # Rename columns to ensure consistency
    region_data.rename(columns={'index': 'Date'}, inplace=True)

    # Plot the data for the current region
    axes[i].plot(region_data['Date'].dt.strftime('%b'), region_data['Species_Richness'],
                 marker='o', color='tab:blue', alpha=0.7, linestyle='-', linewidth=1)

    # Set the y-axis range for all subplots
    axes[i].set_ylim(y_min, y_max)

    # Set fixed x-axis range and labels
    axes[i].set_xticks(range(len(all_months)))
    axes[i].set_xticklabels([month.strftime('%b') for month in all_months])

    # Set plot title and labels for each region
    axes[i].set_title(f'Region {region}', fontsize=12)
    axes[i].set_xlabel('Month', fontsize=10)
    axes[i].set_ylabel('Species Richness', fontsize=10)
    axes[i].tick_params(axis='x', rotation=45, labelsize=8)
    axes[i].tick_params(axis='y', labelsize=8)
    axes[i].grid(True)

# Turn off unused axes
for j in range(len(regions), len(axes)):
    fig.delaxes(axes[j])

# Adjust layout to make space for titles and labels
plt.tight_layout()

# Output the image
output_dir = os.path.dirname(input_file_path)
output_image_path = os.path.join(output_dir, 'Species_Richness_Trend_Subplots_7_Columns.png')

# Save the figure
plt.savefig(output_image_path, dpi=300)
plt.show()

print(f"The plot has been saved at {output_image_path}")
