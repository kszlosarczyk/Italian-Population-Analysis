#!/usr/bin/env python
# coding: utf-8

# # Data Load

# In[5]:


import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from matplotlib.ticker import FuncFormatter

files = glob.glob(r'data\*.csv')
dfs = []

for file in files:
    df = pd.read_csv(file)
    df['Year'] = os.path.splitext(os.path.basename(file))[0]
    dfs.append(df)

all_years_df = pd.concat(dfs, ignore_index = True)



# # Dataset overview

# In[6]:


print(f'Data types {all_years_df.info()}\n')

print(f'Missing values {all_years_df.isna().sum()}\n')

print(f'Number of rows {len(all_years_df)}')

all_years_df[['REF_AREA','Territorio']].nunique()


# # Data clean

# In[7]:


all_years_df['Year'] = all_years_df['Year'].astype(int)

all_years_df.rename(columns={'OBS_VALUE':'Total', 'Territorio':'Region'}, inplace = True)

latest_year_df = all_years_df[all_years_df['Year'] == 2023].reset_index()


# ## Features

# In[ ]:


population_df = all_years_df.groupby('Year').agg(
        F = ('F', 'sum'),
        M = ('M', 'sum'),
        Total = ('Total', 'sum')
        ).reset_index()

population_df['Year'] = pd.to_datetime(population_df['Year'], format='%Y').dt.year
population_df['Growth %'] = population_df['Total'].pct_change().fillna(0) * 100
population_df['F%'] = population_df['F'] / population_df['Total'] * 100
population_df['M%'] = population_df['M'] / population_df['Total'] * 100
population_df['Sex ratio'] = population_df['M'] / population_df['F'] * 100

population_df


# # Yearly population distribution

# By region

# In[9]:


plt.figure(figsize=(12,6))

plt.hist(all_years_df['Total'], bins=30)

plt.show()


# ## Population distribution by sex

# In[80]:


plt.figure(figsize=(10,6))

labels = population_df['Year']
x = np.arange(len(labels))
width = 0.35

plt.bar(x - width/2, population_df['F'], width, label='Women', color='violet')
plt.bar(x + width/2, population_df['M'], width, label='Men', color='lightblue')

# tutaj ustawiamy etykiety lat
plt.xticks(x, population_df['Year'])

plt.title('Total number of Women and Men per Year')
plt.xlabel('Year')
plt.ylabel('Count')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.5)

formatter = FuncFormatter(lambda x, pos: f'{x/1_000_000:.1f}M')
plt.gca().yaxis.set_major_formatter(formatter)
plt.ylim(28_500_000, 31_500_000)

plt.show()

x = np.arange(len(population_df['Year']))
width = 0.35

plt.figure(figsize=(10,6))

plt.bar(x - width/2, population_df['F%'], width, label='Women', color = 'violet')
plt.bar(x + width/2, population_df['M%'], width, label='Men', color = 'lightblue')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.title('% of population')
plt.ylabel('% of population')
plt.xlabel('Year')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.ylim(48, 52)

plt.show()


# Większy udział kobiet w populacji

# ## Sex ratio

# In[79]:


population_df[['Year','Sex ratio']].round(2)


# ## Population change overall

# In[61]:


plt.figure()

plt.plot(population_df.groupby('Year')['Total'].sum(), marker='o')
formatter = FuncFormatter(lambda x, pos: f'{x/1_000_000:.1f}M')
plt.gca().yaxis.set_major_formatter(formatter)

plt.show()


# Populacja cały czas maleje

# In[62]:


display(population_df[['Year','Growth %']])


# In[64]:


display(population_df[population_df['Growth %'] == population_df['Growth %'].min()][['Year','Growth %']])


# Największy spadek populacji odnotowano w 2021

# In[71]:


diff = population_df[['Year','Total']].max() - population_df[['Year','Total']].min()
diff.index = ['Timeline', 'Total change']
diff


# # Latest

# ### Ilość kobiet i mężczyzn procentowo 2023

# In[81]:


stats2 = latest_year_df[['Region', 'F', 'M', 'Total']]
stats2['F%'] = stats2['F'] / stats2['Total'] * 100
stats2['M%'] = stats2['M'] / stats2['Total'] * 100
stats2 = stats2.drop(columns=['F','M','Total']).sort_values('F%', ascending=False )
stats2


# ### Region z największą populacją i najmniejszą w 2023

# In[85]:


current_df = latest_year_df[(latest_year_df['Total'] == latest_year_df['Total'].max()) | (latest_year_df['Total'] == latest_year_df['Total'].min())][['Region', 'Total']]


historical_df = all_years_df[(all_years_df['Total'] == all_years_df['Total'].max()) | (all_years_df['Total'] == all_years_df['Total'].min())][['Year','Region', 'Total']]
historical_df.index = ['max_total','min_total']

display(current_df)
display(historical_df)


# ### Region z największą populacją i najmniejszą

# ### Top 5 największych regionów

# In[86]:


top_regions = latest_year_df[['Region','Total']]
top_regions['Region share %'] = top_regions['Total'] / top_regions['Total'].sum() * 100
top_5_regions = top_regions.nlargest(5, 'Total')
top_5_regions


# In[ ]:


plt.figure(figsize=(12,4))

plt.bar(
    top_5_regions['Region'], 
    top_5_regions['Region share %'])

plt.show()


# ## Trend regionów

# In[22]:


trend = all_years_df.groupby(['Year','Region'])['Total'].sum().reset_index()
trend


# In[23]:


plt.figure(figsize=(8,6))

for region in top_5_regions['Region']:

    data = trend[trend['Region'] == region]

    plt.plot(
        data['Year'],
        data['Total']
    )
plt.title("Trend by region")

