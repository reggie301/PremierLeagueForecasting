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


## PREMIER LEAGUE TABLE SCRIPT SCRAPES CURRENT TABLE ##

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

if change_in_table.upper() == 'Y':
    regular_table.to_csv(
        fr'{full_path}\{current_season}_{current_season + 1}_{max(matchweek_files)+1}.csv')




# SPI SCRAPER FOR THIS MATCHWEEK
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


# FIXTURE SCRAPER FROM FBREF

# Iterates through premier league seasons
for i in range(current_season, current_season + 1):

    # Makes sure we are in the right folder

    if not os.getcwd().endswith('PremierLeagueForecasting'):
        os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

    current_folder = os.getcwd()

    relative_folder = fr'{i}_{i+1}_Fixture'

    full_path = os.path.join(current_folder, relative_folder)

    isExist = os.path.exists(full_path)

    # Creates fixture folder if it does not exist

    if not isExist:
        os.makedirs(full_path)

    url = fr'https://fbref.com/en/comps/9/{i}-{i+1}/{i}-{i+1}-Premier-League-Stats'

    # Uses user-agent to disguise

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

    # Scrapes fixture data

    r = requests.get(url, headers=HEADERS)  # proxies=proxies
    print(r)
    soup = BeautifulSoup(r.text, 'html.parser')

    List_of_teams = []

    time.sleep(2)

    Team_partial_link = []
    Team_full_link = []

    table_soup = soup.find(
        'table', {'class': 'stats_table sortable min_width force_mobilize'})

    for row in table_soup.find_all('tr'):
        row_text = [e.text.strip() for e in row.find_all('td')]
        try:
            List_of_teams.append(row_text[0])
        except:
            continue

    row_team = table_soup.find_all(
        'td', {'class': 'left', 'data-stat': 'team'})

    for e in row_team:
        a = e.find('a')
        Team_partial_link.append(e.find('a').get('href'))

    for e in Team_partial_link:
        Team_full_link.append('https://fbref.com' + e)

    link_dictionary = dict(zip(Team_full_link, List_of_teams,))

    for url in Team_full_link:
        time.sleep(3)
        # try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        table_soup = soup.find(
            'table', {'class': 'stats_table sortable min_width', 'id': 'matchlogs_for'})
        header_data_fixtures = []
        table_data_fixtures = []
        date_list = []
        new_fixtures_table_data = []

        row = table_soup.find('tr')
        header_data_fixtures = [e.text.strip() for e in row.find_all('th')]

        for row in table_soup.find_all('tr'):
            date_text = [e.text.strip()
                         for e in row.find_all('th', {'class': 'left'})]
            date_list.append(date_text)
            row_text = [e.text.strip() for e in row.find_all('td')]
            table_data_fixtures.append(row_text)

        new_fixture_table_data = []
        for x in list(zip(date_list, table_data_fixtures))[1:]:
            fixture_row = []
            for j in list(x):
                for k in j:
                    fixture_row.append(k)
            new_fixtures_table_data.append(fixture_row)

        fixtures_table = pd.DataFrame(
            new_fixtures_table_data, columns=header_data_fixtures)
        fixtures_table = fixtures_table.replace({'': np.nan})
        fixtures_table = fixtures_table[fixtures_table['Comp']
                                        == 'Premier League']
        fixtures_table = fixtures_table.drop(columns=[
                                             'Time', 'Comp', 'Round', 'Day', 'Attendance', 'Captain', 'Formation', 'Referee', 'Match Report', 'Notes'])
        fixtures_table['Club'] = link_dictionary[url]
        fixtures_table['Date'] = pd.to_datetime(fixtures_table['Date'])

        # Saves fixture table as csv
        fixtures_table.to_csv(
            fr'{full_path}\{i}_{i+1}_{link_dictionary[url]}.csv')



## CREATES MASTER HISTORICAL DATA ##
if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

dir_path = os.getcwd()


# CREATES DICTIONARY OF THREE LETTER ON CLUBS

res = []
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a folder
    if os.path.isdir(os.path.join(dir_path, path)) and 'Matchweek' in path:
        res.append(path)

three_let_dict = {}
for matchweek_folder in res:
    os.chdir(fr'{dir_path}\{matchweek_folder}')
    a = pd.read_csv(random.choice(
        os.listdir(fr'{dir_path}\{matchweek_folder}')))
    for index, row in a.iterrows():
        three_let_dict[row['Club'].strip()] = row['Code']
    os.chdir(dir_path)


three_let_dict['Tottenham'] = three_let_dict.pop('Tottenham Hotspur')
three_let_dict['Brighton'] = three_let_dict.pop('Brighton and Hove Albion')
three_let_dict['Manchester Utd'] = three_let_dict.pop('Manchester United')
three_let_dict['Newcastle Utd'] = three_let_dict.pop('Newcastle United')
three_let_dict['West Ham'] = three_let_dict.pop('West Ham United')
three_let_dict['Wolves'] = three_let_dict.pop('Wolverhampton Wanderers')
three_let_dict["Nott'ham Forest"] = three_let_dict.pop('Nottingham Forest')
three_let_dict["Sheffield Utd"] = three_let_dict.pop('Sheffield United')
three_let_dict["Huddersfield"] = three_let_dict.pop('Huddersfield Town')
three_let_dict["West Brom"] = three_let_dict.pop('West Bromwich Albion')


# FIXTURE LIST

res = []
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a folder
    if os.path.isdir(os.path.join(dir_path, path)) and 'Fixture' in path:
        res.append(path)
print(res)
df = pd.DataFrame()
for fixtures in res:
    os.chdir(fr'{dir_path}\{fixtures}')
    folder = os.getcwd()
    list_of_files = os.listdir()
    for i in list_of_files:
        b = pd.read_csv(fr'{folder}\{i}', index_col=0)
        b['Date'] = pd.to_datetime(b['Date'])
        b['Club'] = b['Club'].map(three_let_dict)
        b['Opponent'] = b['Opponent'].map(three_let_dict)
        df = pd.concat([df, b])
    os.chdir(dir_path)
df = df.reset_index(drop=True)
df = df.sort_values(by=['Date'])
df = df.dropna()


# SPI DATA

res = []
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a folder
    if os.path.isdir(os.path.join(dir_path, path)) and 'SPI' in path:
        res.append(path)
print(res)
df1 = pd.DataFrame()
for SPIdata in res:
    os.chdir(fr'{dir_path}\{SPIdata}')
    folder = os.getcwd()
    list_of_files = os.listdir()
    for i in list_of_files:
        b = pd.read_csv(fr'{folder}\{i}', index_col=0)
        b['date'] = pd.to_datetime(b['date'])
        b['Season'] = int(i[:4])
        b['team'] = b['team'].str.replace('Leicester', 'Leicester City')
        b['team'] = b['team'].str.replace('Newcastle', 'Newcastle Utd')
        b['team'] = b['team'].str.replace('Southamon', 'Southampton')
        b['team'] = b['team'].str.replace('Norwich', 'Norwich City')
        b['team'] = b['team'].str.replace('Man City', 'Manchester City')
        b['team'] = b['team'].str.replace('Man United', 'Manchester Utd')
        b['team'] = b['team'].str.replace('Nottm Forest', "Nott'ham Forest")
        b['team'] = b['team'].map(three_let_dict)
        df1 = pd.concat([df1, b])
    os.chdir(dir_path)
df1 = df1.reset_index(drop=True)
df1 = df1.sort_values(by=['date'])


# PREMIER LEAGUE TABLE
res = []
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a folder
    if os.path.isdir(os.path.join(dir_path, path)) and 'Matchweek' in path:
        res.append(path)

df2 = pd.DataFrame()
for matchweek in res:
    os.chdir(fr'{dir_path}\{matchweek}')
    folder = os.getcwd()
    list_of_files = os.listdir()
    for i in list_of_files:
        a = pd.read_csv(fr'{folder}\{i}', index_col=0)
        a['Season'] = int(matchweek[:4])
        a['Last Match Date'] = pd.to_datetime(a['Last Match Date'])
        a = a.drop(columns=['Club', 'W', 'D', 'L', 'GF', 'GA', 'GD'])
        df2 = pd.concat([df2, a])
    os.chdir(dir_path)

df2 = df2.sort_values(by=['Last Match Date'])


fixture_fixture_merge = pd.merge_asof(left=df, right=df, left_on=['Date'], right_on=[
                                      'Date'], left_by=['Club'], right_by=['Opponent'], direction='nearest')
fixture_fixture_merge = fixture_fixture_merge.drop(
    columns=['Venue_y', 'Result_y', 'Opponent_y', 'Club_y'])
matchweek_fixture_merge_1 = pd.merge_asof(left=fixture_fixture_merge, right=df2, left_on=[
                                          'Date'], right_on=['Last Match Date'], left_by=['Club_x'], right_by=['Code'], direction='nearest')
matchweek_fixture_merge_1 = matchweek_fixture_merge_1.drop(
    columns=['Last Match Date', 'Code'])
matchweek_fixture_merge_2 = pd.merge_asof(left=matchweek_fixture_merge_1, right=df2, left_on=[
                                          'Date'], right_on=['Last Match Date'], left_by=['Opponent_x'], right_by=['Code'], direction='nearest')
matchweek_fixture_merge_2 = matchweek_fixture_merge_2.drop(
    columns=['Season_x', 'Last Match Date', 'Code'])
matchweek_fixture_merge_1 = pd.merge_asof(left=fixture_fixture_merge, right=df2, left_on=[
                                          'Date'], right_on=['Last Match Date'], left_by=['Club_x'], right_by=['Code'], direction='nearest')
matchweek_fixture_merge_1 = matchweek_fixture_merge_1.drop(
    columns=['Last Match Date', 'Code'])
matchweek_fixture_merge_2 = pd.merge_asof(left=matchweek_fixture_merge_1, right=df2, left_on=[
                                          'Date'], right_on=['Last Match Date'], left_by=['Opponent_x'], right_by=['Code'], direction='nearest')
matchweek_fixture_merge_2 = matchweek_fixture_merge_2.drop(
    columns=['Season_x', 'Last Match Date', 'Code'])
rename_columns = {'Venue_x': 'Venue', 'Result_x': 'Result',
                  'Club_x': 'Club', 'Season_x': 'Season', 'Opponent_x': 'Opp'}
spi_everything_merge_1 = pd.merge_asof(left=matchweek_fixture_merge_2, right=df1, left_on=[
                                       'Date'], right_on=['date'], left_by=['Club_x'], right_by=['team'], direction='nearest')
spi_everything_merge_1 = spi_everything_merge_1.drop(
    columns=['team', 'date', 'Season_y'])
spi_everything_merge_2 = pd.merge_asof(left=spi_everything_merge_1, right=df1, left_on=[
                                       'Date'], right_on=['date'], left_by=['Opponent_x'], right_by=['team'], direction='nearest')
spi_everything_merge_2 = spi_everything_merge_2.drop(
    columns=['team', 'date', 'Season_y', 'GF_y', 'GA_y', 'xG_y', 'xGA_y'])
df_final = spi_everything_merge_2.rename(rename_columns, axis='columns')

df_final = df_final.sort_values(by=['Club', 'Season', 'Date'])
df_final['Pl_x'] = df_final.groupby(['Club', 'Season'])['Pl_x'].shift(1)
df_final['Position_x'] = df_final.groupby(['Club', 'Season'])[
    'Position_x'].shift(1)
df_final['Pts_x'] = df_final.groupby(['Club', 'Season'])['Pts_x'].shift(1)
df_final['Form_x'] = df_final.groupby(['Club', 'Season'])['Pts_x'].shift(1)


df_final = df_final.sort_values(by=['Opp', 'Season', 'Date'])
df_final['Pl_y'] = df_final.groupby(['Opp', 'Season'])['Pl_y'].shift(1)
df_final['Position_y'] = df_final.groupby(
    ['Opp', 'Season'])['Position_y'].shift(1)
df_final['Pts_y'] = df_final.groupby(['Opp', 'Season'])['Pts_y'].shift(1)
df_final['Form_y'] = df_final.groupby(['Opp', 'Season'])['Pts_y'].shift(1)

df_final = df_final.sort_values(by=['Club', 'Season', 'Date'])

# df_final = df_final.dropna()

if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

os.chdir(fr'{dir_path}\{current_season}_{current_season + 1}_Clean_Data')

today = date.today()

df_final.to_csv(
    fr'{current_season}_{current_season + 1}_{today.strftime("%b%d")}_historical_data.csv')

## PREPARES PREDICTION TABLE ###

if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

dir_path = os.getcwd()

# FIXTURE LIST

res = []
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a folder
    if os.path.isdir(os.path.join(dir_path, path)) and 'Fixture' in path:
        res.append(path)
print(res)
df = pd.DataFrame()
for fixtures in res:
    os.chdir(fr'{dir_path}\{fixtures}')
    folder = os.getcwd()
    list_of_files = os.listdir()
    for i in list_of_files:
        b = pd.read_csv(fr'{folder}\{i}', index_col=0)
        b['Date'] = pd.to_datetime(b['Date'])
        b['Club'] = b['Club'].map(three_let_dict)
        b['Opponent'] = b['Opponent'].map(three_let_dict)
        b = b[b['Date'] >= np.datetime64('today')].iloc[:1]
        df = pd.concat([df, b])
    os.chdir(dir_path)
df = df.reset_index(drop=True)
df = df.sort_values(by=['Date'])
df = df.reset_index(drop=True)


fixture_fixture_merge = pd.merge_asof(left=df, right=df, left_on=['Date'], right_on=[
                                      'Date'], left_by=['Club'], right_by=['Opponent'], direction='nearest')
fixture_fixture_merge = fixture_fixture_merge.drop(
    columns=['Venue_y', 'Result_y', 'Opponent_y', 'Club_y'])
matchweek_fixture_merge_1 = pd.merge_asof(left=fixture_fixture_merge, right=df2, left_on=[
                                          'Date'], right_on=['Last Match Date'], left_by=['Club_x'], right_by=['Code'], direction='nearest')
matchweek_fixture_merge_1 = matchweek_fixture_merge_1.drop(
    columns=['Last Match Date', 'Code'])
matchweek_fixture_merge_2 = pd.merge_asof(left=matchweek_fixture_merge_1, right=df2, left_on=[
                                          'Date'], right_on=['Last Match Date'], left_by=['Opponent_x'], right_by=['Code'], direction='nearest')
matchweek_fixture_merge_2 = matchweek_fixture_merge_2.drop(
    columns=['Season_x', 'Last Match Date', 'Code'])
spi_everything_merge_1 = pd.merge_asof(left=matchweek_fixture_merge_2, right=df1, left_on=[
                                       'Date'], right_on=['date'], left_by=['Club_x'], right_by=['team'], direction='nearest')
spi_everything_merge_1 = spi_everything_merge_1.drop(
    columns=['team', 'date', 'Season_y'])
spi_everything_merge_2 = pd.merge_asof(left=spi_everything_merge_1, right=df1, left_on=[
                                       'Date'], right_on=['date'], left_by=['Opponent_x'], right_by=['team'], direction='nearest')
spi_everything_merge_2 = spi_everything_merge_2.drop(
    columns=['team', 'date', 'Season_y', 'GF_y', 'GA_y', 'xG_y', 'xGA_y'])

rename_columns = {'Venue_x': 'Venue', 'Result_x': 'Result',
                  'Club_x': 'Club', 'Season_x': 'Season', 'Opponent_x': 'Opp'}

df_final = spi_everything_merge_2.rename(rename_columns, axis='columns')


if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

os.chdir(fr'{dir_path}\{current_season}_{current_season + 1}_Clean_Data')

df_final.to_csv(
    fr'{current_season}_{current_season + 1}_{today.strftime("%b%d")}_matchweek_data.csv')

### REGRESSION PREDICTOR ###

if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

dir_path = os.getcwd()

df_train = pd.read_csv(
    fr'{dir_path}\{current_season}_{current_season + 1}_Clean_Data\{current_season}_{current_season + 1}_{today.strftime("%b%d")}_historical_data.csv', index_col=0)

df_pred = pd.read_csv(
    fr'{dir_path}\{current_season}_{current_season + 1}_Clean_Data\{current_season}_{current_season + 1}_{today.strftime("%b%d")}_matchweek_data.csv', index_col=0)


df = pd.concat([df_train, df_pred])
df = df.sort_values(by=['Club', 'Season', 'Date',])
df = df.reset_index(drop=True)
df['Date'] = pd.to_datetime(df['Date'])

## RESULT ENCODING ##


def encode_result(x):
    if x['Result'] == 'W':
        val = 2
    elif x['Result'] == 'D':
        val = 1
    else:
        val = 0
    return val


df['Result'] = df.apply(encode_result, axis=1)

# POINTS DIFF#
df['Points_Diff'] = (df['Pts_x']/df['Pl_x'] - df['Pts_y']/df['Pl_y'])/3


## SPI Diff##
df['SPI_Diff'] = df['spi_x'] - df['spi_y']
df['SPI_Diff'] = (df['SPI_Diff'] - df.groupby(['Season'])['SPI_Diff'].transform(min))/(df.groupby(
    ['Season'])['SPI_Diff'].transform(max) - df.groupby(['Season'])['SPI_Diff'].transform(min))
df['Off_Diff'] = df['off_x'] - df['off_y']
df['Off_Diff'] = (df['Off_Diff'] - df.groupby(['Season'])['Off_Diff'].transform(min))/(df.groupby(
    ['Season'])['Off_Diff'].transform(max) - df.groupby(['Season'])['Off_Diff'].transform(min))
df['Def_Diff'] = df['def_x'] - df['def_y']
df['Def_Diff'] = (df['Def_Diff'] - df.groupby(['Season'])['Def_Diff'].transform(min))/(df.groupby(
    ['Season'])['Def_Diff'].transform(max) - df.groupby(['Season'])['Def_Diff'].transform(min))

## FORM##
df['Form_Diff'] = (df['Form_x'] - df['Form_y'])/15

# Creating form for goals and goals conceded and expected values for last 5 games
df['Avg_GF_last_5'] = df.groupby(['Club', 'Season'])['GF_x'].shift(1)
df['Avg_GF_last_5'] = df.groupby(['Club', 'Season'])['Avg_GF_last_5'].rolling(
    5).mean().reset_index([0, 1], drop=True)
df['Avg_GA_last_5'] = df.groupby(['Club', 'Season'])['GA_x'].shift(1)
df['Avg_GA_last_5'] = df.groupby(['Club', 'Season'])['Avg_GA_last_5'].rolling(
    5).mean().reset_index([0, 1], drop=True)
df['Avg_xG_last_5'] = df.groupby(['Club', 'Season'])['xG_x'].shift(1)
df['Avg_xG_last_5'] = df.groupby(['Club', 'Season'])['Avg_xG_last_5'].rolling(
    5).mean().reset_index([0, 1], drop=True)
df['Avg_xGA_last_5'] = df.groupby(['Club', 'Season'])['xGA_x'].shift(1)
df['Avg_xGA_last_5'] = df.groupby(['Club', 'Season'])['Avg_xGA_last_5'].rolling(
    5).mean().reset_index([0, 1], drop=True)
df['Avg_Poss_last_5'] = df.groupby(['Club', 'Season'])['Poss_x'].shift(1)
df['Avg_Poss_last_5'] = df.groupby(['Club', 'Season'])[
    'Avg_Poss_last_5'].rolling(5).mean().reset_index([0, 1], drop=True)

# Standardisation
df['Avg_GF_last_5'] = (df['Avg_GF_last_5'] - df.groupby(['Season'])['Avg_GF_last_5'].transform(min))/(
    df.groupby(['Season'])['Avg_GF_last_5'].transform(max) - df.groupby(['Season'])['Avg_GF_last_5'].transform(min))
df['Avg_GA_last_5'] = (df['Avg_GA_last_5'] - df.groupby(['Season'])['Avg_GA_last_5'].transform(min))/(
    df.groupby(['Season'])['Avg_GA_last_5'].transform(max) - df.groupby(['Season'])['Avg_GA_last_5'].transform(min))
df['Avg_xG_last_5'] = (df['Avg_xG_last_5'] - df.groupby(['Season'])['Avg_xG_last_5'].transform(min))/(
    df.groupby(['Season'])['Avg_xG_last_5'].transform(max) - df.groupby(['Season'])['Avg_xG_last_5'].transform(min))
df['Avg_xGA_last_5'] = (df['Avg_xGA_last_5'] - df.groupby(['Season'])['Avg_xGA_last_5'].transform(min))/(
    df.groupby(['Season'])['Avg_xGA_last_5'].transform(max) - df.groupby(['Season'])['Avg_xGA_last_5'].transform(min))
df['Avg_Poss_last_5'] = (df['Avg_Poss_last_5'] - df.groupby(['Season'])['Avg_Poss_last_5'].transform(min))/(
    df.groupby(['Season'])['Avg_Poss_last_5'].transform(max) - df.groupby(['Season'])['Avg_Poss_last_5'].transform(min))

## SEASON STATS##
df['Avg_GF_season'] = df.groupby(['Club', 'Season'])['GF_x'].shift(1)
df['Avg_GF_season'] = df.groupby(['Season'])['Avg_GF_season'].expanding(
    1).mean().reset_index([0], drop=True)
df['Avg_GA_season'] = df.groupby(['Club', 'Season'])['GA_x'].shift(1)
df['Avg_GA_season'] = df.groupby(['Season'])['Avg_GA_season'].expanding(
    1).mean().reset_index([0], drop=True)
df['Avg_xG_season'] = df.groupby(['Club', 'Season'])['xG_x'].shift(1)
df['Avg_xG_season'] = df.groupby(['Season'])['Avg_xG_season'].expanding(
    1).mean().reset_index([0], drop=True)
df['Avg_xGA_season'] = df.groupby(['Club', 'Season'])['xGA_x'].shift(1)
df['Avg_xGA_season'] = df.groupby(['Season'])['Avg_xGA_season'].expanding(
    1).mean().reset_index([0], drop=True)
df['Avg_Poss_season'] = df.groupby(['Club', 'Season'])['Poss_x'].shift(1)
df['Avg_Poss_season'] = df.groupby(['Season'])['Avg_Poss_season'].expanding(
    1).mean().reset_index([0], drop=True)

# Standardisation
df['Avg_GF_season'] = (df['Avg_GF_season'] - df.groupby(['Season'])['Avg_GF_season'].transform(min))/(
    df.groupby(['Season'])['Avg_GF_season'].transform(max) - df.groupby(['Season'])['Avg_GF_season'].transform(min))
df['Avg_GA_season'] = (df['Avg_GA_season'] - df.groupby(['Season'])['Avg_GA_season'].transform(min))/(
    df.groupby(['Season'])['Avg_GA_season'].transform(max) - df.groupby(['Season'])['Avg_GA_season'].transform(min))
df['Avg_xG_season'] = (df['Avg_xG_season'] - df.groupby(['Season'])['Avg_xG_season'].transform(min))/(
    df.groupby(['Season'])['Avg_xG_season'].transform(max) - df.groupby(['Season'])['Avg_xG_season'].transform(min))
df['Avg_xGA_season'] = (df['Avg_xGA_season'] - df.groupby(['Season'])['Avg_xGA_season'].transform(min))/(
    df.groupby(['Season'])['Avg_xGA_season'].transform(max) - df.groupby(['Season'])['Avg_xGA_season'].transform(min))
df['Avg_Poss_season'] = (df['Avg_Poss_season'] - df.groupby(['Season'])['Avg_Poss_season'].transform(min))/(
    df.groupby(['Season'])['Avg_Poss_season'].transform(max) - df.groupby(['Season'])['Avg_Poss_season'].transform(min))

## AGAINST OPPONENT##
df['Avg_GF_Opp'] = df.groupby(['Club', 'Opp'])['GF_x'].shift(1)
df['Avg_GF_Opp'] = df.groupby(['Club', 'Opp'])['Avg_GF_Opp'].rolling(
    2).mean().reset_index([0, 1], drop=True)
df['Avg_GA_Opp'] = df.groupby(['Club', 'Opp'])['GA_x'].shift(1)
df['Avg_GA_Opp'] = df.groupby(['Club', 'Opp'])['Avg_GA_Opp'].rolling(
    2).mean().reset_index([0, 1], drop=True)
df['Avg_xG_Opp'] = df.groupby(['Club', 'Opp'])['xG_x'].shift(1)
df['Avg_xG_Opp'] = df.groupby(['Club', 'Opp'])['Avg_xG_Opp'].rolling(
    2).mean().reset_index([0, 1], drop=True)
df['Avg_xGA_Opp'] = df.groupby(['Club', 'Opp'])['xGA_x'].shift(1)
df['Avg_xGA_Opp'] = df.groupby(['Club', 'Opp'])['Avg_xGA_Opp'].rolling(
    2).mean().reset_index([0, 1], drop=True)
df['Avg_Poss_Opp'] = df.groupby(['Club', 'Opp'])['Poss_x'].shift(1)
df['Avg_Poss_Opp'] = df.groupby(['Club', 'Opp'])['Avg_Poss_Opp'].rolling(
    2).mean().reset_index([0, 1], drop=True)

# Standardisation
df['Avg_GF_Opp'] = (df['Avg_GF_Opp'] - df.groupby(['Opp'])['Avg_GF_Opp'].transform(min))/(
    df.groupby(['Opp'])['Avg_GF_Opp'].transform(max) - df.groupby(['Opp'])['Avg_GF_Opp'].transform(min))
df['Avg_GA_Opp'] = (df['Avg_GA_Opp'] - df.groupby(['Opp'])['Avg_GA_Opp'].transform(min))/(
    df.groupby(['Opp'])['Avg_GA_Opp'].transform(max) - df.groupby(['Opp'])['Avg_GA_Opp'].transform(min))
df['Avg_xG_Opp'] = (df['Avg_xG_Opp'] - df.groupby(['Opp'])['Avg_xG_Opp'].transform(min))/(
    df.groupby(['Opp'])['Avg_xG_Opp'].transform(max) - df.groupby(['Opp'])['Avg_xG_Opp'].transform(min))
df['Avg_xGA_Opp'] = (df['Avg_xGA_Opp'] - df.groupby(['Opp'])['Avg_xGA_Opp'].transform(min))/(
    df.groupby(['Opp'])['Avg_xGA_Opp'].transform(max) - df.groupby(['Opp'])['Avg_xGA_Opp'].transform(min))
df['Avg_Poss_Opp'] = (df['Avg_Poss_Opp'] - df.groupby(['Opp'])['Avg_Poss_Opp'].transform(min))/(
    df.groupby(['Opp'])['Avg_Poss_Opp'].transform(max) - df.groupby(['Opp'])['Avg_Poss_Opp'].transform(min))


df_test = df[df['Date'] < np.datetime64('today')]
df_pred = df[df['Date'] >= np.datetime64('today')]
df_pred['GF_x'] = 0
df_pred['GA_x'] = 0
df_poo = df_pred


unwanted_columns = ['Date', 'Opp', 'Result', 'GF_x', 'xG_x', 'xGA_x',
                    'Poss_x', 'Club', 'Poss_y', 'Position_x', 'Pl_x', 'Pts_x', 'Form_x',
                    'Position_y', 'Pl_y', 'Pts_y', 'Form_y', 'spi_x', 'off_x', 'def_x',
                    'Season', 'spi_y', 'off_y', 'def_y']
df_test_1 = df_test.drop(columns=unwanted_columns)
df_pred_1 = df_pred.drop(columns=unwanted_columns)
df_test_1 = df_test_1.dropna()
df_pred_1 = df_pred_1.dropna()

df_test_1 = pd.get_dummies(df_test_1, columns=['Venue'])
df_pred_1 = pd.get_dummies(df_pred_1, columns=['Venue'])

boo = df_test_1.drop(columns='GA_x')

X_train_1 = df_test_1[boo.columns]
y_train_1 = df_test_1['GA_x']

X_test_1 = df_pred_1[boo.columns]

rfr = RandomForestRegressor(n_estimators=250, max_depth=3, random_state=0)
rfr.fit(X_train_1, y_train_1)
y_pred_1 = rfr.predict(X_test_1)


unwanted_columns = ['Date', 'Opp', 'Result', 'GA_x', 'xG_x', 'xGA_x',
                    'Poss_x', 'Club', 'Poss_y', 'Position_x', 'Pl_x', 'Pts_x', 'Form_x',
                    'Position_y', 'Pl_y', 'Pts_y', 'Form_y', 'spi_x', 'off_x', 'def_x',
                    'Season', 'spi_y', 'off_y', 'def_y']
df_test = df_test.drop(columns=unwanted_columns)
df_pred = df_pred.drop(columns=unwanted_columns)
df_test = df_test.dropna()
df_pred = df_pred.dropna()

df_test.columns
df_test = pd.get_dummies(df_test, columns=['Venue'])
df_pred = pd.get_dummies(df_pred, columns=['Venue'])

boo = df_test.drop(columns='GF_x')

X_train = df_test[boo.columns]
y_train = df_test['GF_x']

X_test = df_pred[boo.columns]

rfr = RandomForestRegressor(n_estimators=90, max_depth=3, random_state=0)
rfr.fit(X_train, y_train)
y_pred = rfr.predict(X_test)

df_poo = df_poo[['Season', 'Club', 'Opp', 'Venue', 'Date']]
a = pd.DataFrame(y_pred, columns=['GF'], index=X_test.index)
b = pd.DataFrame(y_pred_1, columns=['GA'], index=X_test_1.index)
c = pd.merge(df_poo, a, left_index=True, right_index=True)
d1 = pd.merge(c, b, left_index=True, right_index=True)
d2 = pd.merge(d1, d1, left_on=['Club', 'Date'], right_on=['Opp', 'Date'])
d2 = d2.drop(columns=['Season_y', 'Club_y', 'Opp_y', 'Venue_y'])

d2['GF'] = (d2['GF_x'] + d2['GA_y']) / 2
d2['GA'] = (d2['GF_y'] + d2['GA_x']) / 2
d2 = d2.drop(columns=['GF_x', 'GA_x', 'GF_y', 'GA_y'])

d3 = d2.drop(columns=['Venue_x', 'GA'])


for score in range(6):
    d3['Score' + str(score)] = (d3['GF'] ** score *
                                np.exp(- d3['GF']))/np.math.factorial(score)

d4 = pd.merge(d3, d3, left_on='Club_x', right_on='Opp_x')

score_list = []

win_list = []
draw_list = []
loss_list = []

for i in range(6):
    for j in range(6):
        d4[fr'{i} - {j}'] = d4[fr'Score{i}_x'] * d4[fr'Score{j}_y']
        score_list.append(fr'{i} - {j}')

        if i > j:
            win_list.append(list(d4[fr'Score{i}_x'] * d4[fr'Score{j}_y']))
        elif i == j:
            draw_list.append(list(d4[fr'Score{i}_x'] * d4[fr'Score{j}_y']))
        else:
            loss_list.append(list(d4[fr'Score{i}_x'] * d4[fr'Score{j}_y']))


d4[score_list].idxmax(axis=1)

d2['Most likely score'] = list(d4[score_list].idxmax(axis=1))

win_list = [sum(i) for i in list(zip(*win_list))]
draw_list = [sum(i) for i in list(zip(*draw_list))]
loss_list = [sum(i) for i in list(zip(*loss_list))]

d2['win_prob'] = win_list
d2['draw_prob'] = draw_list
d2['loss_prob'] = loss_list

d2['sum'] = d2['win_prob'] + d2['draw_prob'] + d2['loss_prob']

d2['win_prob'] = d2['win_prob']/d2['sum'] 
d2['draw_prob'] = d2['draw_prob']/d2['sum'] 
d2['loss_prob'] = d2['loss_prob']/d2['sum'] 

d2 = d2.drop(columns = ['sum'])

if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

current_folder = os.getcwd()

relative_folder = fr'{current_season}_{current_season + 1}_Match_Predictions'

full_path = os.path.join(current_folder, relative_folder)

d2.to_csv(
    fr'{full_path}\{current_season}_{current_season + 1}_{today.strftime("%b%d")}_predictions.csv')

d2 = d2[d2['Venue_x'] == 'Home']
d2 = d2.drop(columns = ['Season_x','GF','GA','Venue_x'])
d2['Date'] = d2['Date'].dt.strftime('%B %d')
d2 = d2.rename(columns={"Club_x": "Home", "Opp_x": "Away","win_prob": "1", "draw_prob":"X","loss_prob":"2"})
final = d2.style.background_gradient(axis=None).format({'1': '{:,.2%}'.format,'X': '{:,.2%}'.format,'2': '{:,.2%}'.format,})
final.to_html('this_matchweek_predictions.html',index=False)

### bet365###

url = 'https://www.aceodds.com/football/premiership.html'

df = pd.read_html(url)

betting_odds = pd.DataFrame()
df = df[0].replace(' ', '/')

df = df[df[1].str.contains("/")]
df[2] = df[2].str.replace('Draw', '')
betting_odds['Club'] = df[1].str.rsplit(" ", 1, expand=True)[0]
betting_odds['Opp'] = df[3].str.rsplit(" ", 1, expand=True)[0]
betting_odds['bet365_win'] = df[1].str.rsplit(" ", 1, expand=True)[1]
betting_odds['bet365_draw'] = df[2]
betting_odds['bet365_loss'] = df[3].str.rsplit(" ", 1, expand=True)[1]
betting_odds[['Club', 'Opp']] = betting_odds[[
    'Club', 'Opp']].replace('Man Utd', 'Manchester Utd')
betting_odds[['Club', 'Opp']] = betting_odds[[
    'Club', 'Opp']].replace('Man City', 'Manchester City')
betting_odds[['Club', 'Opp']] = betting_odds[[
    'Club', 'Opp']].replace('Newcastle', 'Newcastle Utd')
betting_odds[['Club', 'Opp']] = betting_odds[['Club', 'Opp']
                                             ].replace('Nottm Forest', "Nott'ham Forest")
betting_odds[['Club', 'Opp']] = betting_odds[[
    'Club', 'Opp']].replace('Wolverhampton', "Wolves")
betting_odds[['Club', 'Opp']] = betting_odds[[
    'Club', 'Opp']].replace('Leicester', "Leicester City")
betting_odds[['Club', 'Opp']] = betting_odds[[
    'Club', 'Opp']].replace('Leeds', "Leeds United")
betting_odds['Club'] = betting_odds['Club'].map(three_let_dict)
betting_odds['Opp'] = betting_odds['Opp'].map(three_let_dict)

betting_odds['bet365_win'] = betting_odds['bet365_win'].str.rsplit("/", 1, expand=True)[1].astype(int) / (betting_odds['bet365_win'].str.rsplit(
    "/", 1, expand=True)[0].astype(int) + betting_odds['bet365_win'].str.rsplit("/", 1, expand=True)[1].astype(int))
betting_odds['bet365_draw'] = betting_odds['bet365_draw'].str.rsplit("/", 1, expand=True)[1].astype(int) / (betting_odds['bet365_draw'].str.rsplit(
    "/", 1, expand=True)[0].astype(int) + betting_odds['bet365_draw'].str.rsplit("/", 1, expand=True)[1].astype(int))
betting_odds['bet365_loss'] = betting_odds['bet365_loss'].str.rsplit("/", 1, expand=True)[1].astype(int) / (betting_odds['bet365_loss'].str.rsplit(
    "/", 1, expand=True)[0].astype(int) + betting_odds['bet365_loss'].str.rsplit("/", 1, expand=True)[1].astype(int))



if not os.getcwd().endswith('PremierLeagueForecasting'):
    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

current_folder = os.getcwd()

relative_folder = fr'{current_season}_{current_season + 1}_Match_Predictions'

full_path = os.path.join(current_folder, relative_folder)

prediction_table = pd.read_csv(
    fr'{full_path}\{current_season}_{current_season + 1}_{today.strftime("%b%d")}_predictions.csv',index_col=0)

prediction_table = prediction_table[[
    'Club_x', 'Opp_x', 'win_prob', 'draw_prob', 'loss_prob']]

final_table = pd.merge(prediction_table, betting_odds, left_on=[
                       'Club_x', 'Opp_x'], right_on=['Club', 'Opp'])

final_table = final_table.drop(columns=['Club', 'Opp'])
final_table['Buy_Home_Win'] = final_table['win_prob'] - \
    final_table['bet365_win']
final_table['Buy_Home_Win'] = final_table['Buy_Home_Win'].apply(
    lambda x: 'Yes' if x > 0.1 else 'No')
final_table['Buy_Draw'] = final_table['draw_prob'] - final_table['bet365_draw']
final_table['Buy_Draw'] = final_table['Buy_Draw'].apply(
    lambda x: 'Yes' if x > 0.1 else 'No')
final_table['Buy_Home_Loss'] = final_table['loss_prob'] - \
    final_table['bet365_loss']
final_table['Buy_Home_Loss'] = final_table['Buy_Home_Loss'].apply(
    lambda x: 'Yes' if x > 0.1 else 'No')
final_table = final_table.set_index(['Club_x', 'Opp_x'])
final_table.to_csv(
    fr'{full_path}\{current_season}_{current_season + 1}_{today.strftime("%b%d")}_bet365.csv')

for i in ['Buy_Home_Win', 'Buy_Draw', 'Buy_Home_Loss']:
    print(fr"{i} {final_table.index[final_table[i] == 'Yes'].tolist()}")
