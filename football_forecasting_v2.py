from bs4 import BeautifulSoup
import time
import os
import pandas as pd
from datetime import date
import requests
import numpy as np
import random
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb


current_season = int(input('What is the current season?'))

change_in_table = input('Change in table? (Y/N)')


def pltablefetcher():
    """Fetches the premier league table currently and saves it under the Matchweek Folder"""
    if change_in_table.upper() == 'Y':

        if not os.getcwd().endswith('PremierLeagueForecasting'):
            os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

        current_folder = os.getcwd()

        relative_folder = fr'{current_season}_{current_season + 1}_Matchweek'

        full_path = os.path.join(current_folder, relative_folder)

        isExist = os.path.exists(full_path)

        if not isExist:
            os.makedirs(full_path)

        matchweek_files = {}

        for matchweek_file in os.listdir(fr'{current_folder}\{relative_folder}'):
            a = matchweek_file.replace(fr'{current_season}_{current_season+1}_','').replace('.csv','')
            matchweek_files[int(a)] = matchweek_file

        table = pd.read_html(r'https://www.premierleague.com/tables?co=1&se=489&ha=-1')


        regular_table = pd.DataFrame(table[0])
        regular_table = regular_table.drop(columns=['Next', 'Unnamed: 12'])
        regular_table['Match Date'] = regular_table[1::2]['Club'].str.split('-').str[1]
        regular_table['Match Date'] = regular_table[1::2]['Match Date'].str.split(
            ' ').str[2:5]
        a = []
        for x in regular_table['Match Date'][1::2]:
            try:
                a.append(' '.join(x))
            except:
                continue

        regular_table = regular_table[::2]
        regular_table['Match Date'] = a
        regular_table['Match Date'] = pd.to_datetime(regular_table['Match Date'])
        regular_table.columns = ['Position', 'Club', 'Pl', 'W', 'D',
                                'L', 'GF', 'GA', 'GD', 'Pts', 'Form', 'Last Match Date']
        regular_table['Position'] = regular_table['Position'].str[:3].astype(int)
        regular_table['Code'] = regular_table['Club'].str[-3:]
        regular_table['Club'] = regular_table['Club'].str[:-3].str.strip()
        regular_table['Pl'] = regular_table['Pl'].astype(int)
        regular_table['W'] = regular_table['W'].astype(int)
        regular_table['D'] = regular_table['D'].astype(int)
        regular_table['L'] = regular_table['L'].astype(int)
        regular_table['GF'] = regular_table['GF'].astype(int)
        regular_table['GA'] = regular_table['GA'].astype(int)
        regular_table['GD'] = regular_table['GD'].astype(int)
        regular_table['Pts'] = regular_table['Pts'].astype(int)
        regular_table['Form'] = regular_table['Form'].str.replace(
            r'\w{2,100}', '', regex=True)
        regular_table['Form'] = regular_table['Form'].str.replace(
            r"\s+", '', regex=True)
        regular_table['Form'] = regular_table['Form'].str.replace(
            r'[^a-zA-Z]', '', regex=True)
        regular_table['Form'] = regular_table['Form'].apply(
            lambda x: (x.count('W')*3 + x.count('D'))/len(x))
        regular_table['Season'] = current_season
        regular_table.to_csv(fr'{full_path}\{current_season}_{current_season + 1}_{max(matchweek_files)+1}.csv')



def spifetcher():
    url = r'https://projects.fivethirtyeight.com/soccer-predictions/premier-league/'
    
    date_dict = {'Sept': 'Sep', 'March': 'Mar',
                'April': 'Apr', 'June': 'Jun', 'July': 'Jul'}

    if not os.getcwd().endswith('PremierLeagueForecasting'):
        os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

    current_folder = os.getcwd()

    relative_folder = fr'{current_season}_{current_season+1}_SPIdata'

    full_path = os.path.join(current_folder, relative_folder)

    isExist = os.path.exists(full_path)


    if not isExist:
        os.makedirs(full_path)

    match_date = date.today().strftime('%y%b%d')

    dfs = pd.read_html(url)
    a = dfs[0].replace(' ', ':')
    a.columns = a.columns.droplevel()
    a = a[['team', 'spi', 'off.', 'def.']]
    a['team'] = a['team'].str.replace('\d+', '', regex=True)
    a['team'] = a['team'].str.replace('pts', '')
    a['team'] = a['team'].str.replace('pt', '')
    a['team'] = a['team'].str.replace('.', '')
    a['team'] = a['team'].str.strip()
    a['date'] = match_date
    a['date'] = pd.to_datetime(a['date'], format='%y%b%d')
    a = a.rename(columns={'off.': 'off', 'def.': 'def'})

    a.to_csv(fr'{full_path}\{current_season}_{current_season+1}_{match_date}.csv')
