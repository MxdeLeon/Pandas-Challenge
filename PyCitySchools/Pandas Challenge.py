#!/usr/bin/env python
# coding: utf-8

# # District Summary

import os
import pandas as pd

school_data_file = os.path.join('.', 'Resources', 'schools_complete.csv')
student_data_file = os.path.join('.', 'Resources', 'students_complete.csv')

school_data = pd.read_csv(school_data_file)
student_data = pd.read_csv(student_data_file)

school_df_merged = pd.merge(student_data, school_data, how='left', on='school_name')
print(school_df_merged)

# count the number of unique schools
school_count = school_df_merged['school_name'].nunique()

# count the total number of students
student_count = school_df_merged['student_name'].count()

# calculate the total district budget
total_budget = school_df_merged['budget'].unique().sum()

# calculate the average student math score
avg_math_score = school_df_merged['math_score'].mean()

# calculate the average student reading score
avg_reading_score = school_df_merged['reading_score'].mean()

# calculate the percentage of students with passing (>= 70%) math scores
pct_passing_math = ((school_df_merged[school_df_merged['math_score'] >= 70].count()[
    'student_name']) / student_count) * 100

# calculate the percentage of students with passing (>= 70%) reading scores
pct_passing_reading = ((school_df_merged[school_df_merged['reading_score'] >= 70].count()[
    'student_name']) / student_count) * 100

# calculate the percentage of students passing overall
num_pass_both = \
    school_df_merged[(school_df_merged["reading_score"] >= 70) & (school_df_merged['math_score'] >= 70)].count()[
        'student_name']
pct_pass_both = (num_pass_both / student_count) * 100

# create new dataframe summarizing district data
dist_summary = pd.DataFrame({'Total Schools': [school_count],
                             'Total Students': [student_count],
                             'Total Budget': [total_budget],
                             'Average Math Score': [avg_math_score],
                             'Average Reading Score': [avg_reading_score],
                             '% Passing Math': [pct_passing_math],
                             '% Passing Reading': [pct_passing_reading],
                             '% Overall Passing': [pct_pass_both]})

dist_summary['Total Budget'] = dist_summary['Total Budget'].map("${:,.2f}".format)
dist_summary['Total Students'] = dist_summary['Total Students'].map("{:,}".format)

print(dist_summary)

# # School Summary

# Get school names

school_names = school_data['school_name'].unique()

# Extract and save school types
school_types = school_data.set_index(['school_name'])['type']
school_summary = school_types
school_summary = school_summary.reset_index()

# Calculate student population per school
per_school_counts = school_data.set_index(['school_name'])['size']
school_summary = pd.merge(school_summary, per_school_counts, on='school_name')

# Calculate budget by school
per_school_budget = school_data.set_index(['school_name'])['budget']
school_summary = pd.merge(school_summary, per_school_budget, on='school_name')

# Calculate per student budget
per_school_capita = per_school_budget / per_school_counts
school_summary['per_student_budget'] = list(per_school_capita)

groups = school_df_merged.groupby(['school_name'])
temp = groups[['math_score', 'reading_score']].mean()

school_summary.join(temp, on='school_name')

# Calculate the number of students passing math in each school
count_pass_math = []

for school in school_names:
    count_pass_math.append(school_df_merged[(school_df_merged['school_name'] == school) & \
                                            (school_df_merged['math_score'] >= 70)].count()['student_name'])

# Calculate the percentage of students passing math per school
school_summary['%_passing_math'] = (count_pass_math / school_summary['size']) * 100

# Calculate the number of students passing reading in each school
count_pass_reading = []

for school in school_names:
    count_pass_reading.append(school_df_merged[(school_df_merged['school_name'] == school) & \
                                               (school_df_merged['reading_score'] >= 70)].count()['student_name'])

# Calculate the percentage of students passing reading per school
school_summary['%_passing_reading'] = (count_pass_reading / school_summary['size']) * 100

# Calculate the number of students passing both in each school
count_pass_both = []

for school in school_names:
    count_pass_both.append(school_df_merged[(school_df_merged['school_name'] == school) & \
                                            (school_df_merged['reading_score'] >= 70) & \
                                            (school_df_merged['math_score'] >= 70)].count()['student_name'])

# Calculate the percentage of students passing overall per school
school_summary['%_passing_overall'] = (count_pass_both / school_summary['size']) * 100
print(school_summary)

# # Schools sorted by Performance

# Create new dataframe showing top performing schools sorted by % passing overall
top_schools = pd.DataFrame(school_summary.sort_values('%_passing_overall', ascending=False))
print(top_schools)

# Create new dataframe showing bottom performing schools sorted by % passing overall
bottom_schools = pd.DataFrame(school_summary.sort_values('%_passing_overall', ascending=True))
print(bottom_schools)

# # Scores by Grade


groups = school_df_merged.groupby(by='grade')
score_by_grade = groups[['math_score', 'reading_score']].mean()
score_by_grade = score_by_grade.reset_index()
score_by_grade = score_by_grade.rename(columns={'math_score': 'avg_math_score', 'reading_score': 'avg_reading_score'})
print(score_by_grade)

# # Scores by School Spending

spending_bins = [0, 585, 630, 645, 680]
labels = ["<$585", "$585-630", "$630-645", "$645-680"]

test = pd.cut(school_summary['per_student_budget'], spending_bins, labels=labels)
school_summary.insert(loc=5,
                      column='spending_bracket',
                      value=list(test))

columns = list(school_summary.columns)

grouped = school_summary.groupby('spending_bracket')
spending_summary = grouped[columns[6:]].mean(numeric_only=True)
spending_summary = spending_summary.reset_index()
print(spending_summary)

# # Scores by School Size

size_bins = [0, 1000, 2000, 5000]
labels = ["Small (<1000)", "Medium (1000-2000)", "Large (2000-5000)"]

size_groups = pd.cut(school_summary['size'], size_bins, labels=labels)
size_groups = list(size_groups)
school_sum_v1 = school_summary
school_sum_v1.insert(loc=3,
                     column='size_bracket',
                     value=size_groups)

columns = school_sum_v1.columns
list(columns)
groups = school_sum_v1.groupby('size_bracket')

size_summary = groups[columns[7:]].mean()
print(size_summary)

# # Scores by School Type

school_sum_v2 = school_summary
groups = school_sum_v2.groupby('type')
columns = school_sum_v2.columns

type_summary = groups[columns[7:]].mean()
print(type_summary)
