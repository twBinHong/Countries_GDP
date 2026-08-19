'''
The required information needs to be made 
accessible as a CSV file Countries_by_GDP.csv 
as well as a table Countries_by_GDP in a database 
file World_Economies.db with attributes Country 
and GDP_USD_billion.

Your boss wants you to demonstrate the success of 
this code by running a query on the database 
table to display only the entries with more than
 a 100 billion USD economy. Also, you should log 
 in a file with the entire process of execution 
 named etl_project_log.txt.
'''

# Code for ETL operations on Country-GDP data

# Importing the required libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd 
import numpy as np 
import sqlite3
from datetime import datetime

#  initialize all the known entities
url ='https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
db_name = 'World_Economies.db'
table_name = 'Countries_by_GDP'
csv_path = './Countries_by_GDP.csv'
table_attribs = ["Country", "GDP_USD_millions"]
log_text = './etl_project_log.txt'

def extract(url, table_attribs):
    ''' This function extracts the required
	information from the website and saves it to a dataframe. The
	function returns the dataframe for further processing. '''
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    df = pd.DataFrame(columns= table_attribs)
    #target_table = "wikitable sortable static-row-numbers plainrowheaders srn-white-background jquery-tablesorter"
    #rows = soup.find_all('table', class_=target_table).find_all('tbody')
    tables = soup.find_all('tbody')
    rows = tables[2].find_all('tr')
    for row in rows:
        col = row.find_all('td')
        if col:
            # col.has_attr('href') and col[2].contents != "—":
            if col[0].find('a') and '—' not in col[2]:
                data_dict = {'Country':col[0].a.contents,'GDP_USD_millions':col[2].contents}
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df,df1], ignore_index=True)
    return df

def transform(df):
    ''' This function converts the GDP information from Currency
	format to float value, transforms the information of GDP from
	USD (Millions) to USD (Billions) rounding to 2 decimal places.
	The function returns the transformed dataframe.'''
    #df["GDP_USD_millions"] = df["GDP_USD_millions"].astype('float64')
    #df[["GDP_USD_millions"]] = df[["GDP_USD_millions"]] /1000
    #df["GDP_USD_millions"] = np.round( df["GDP_USD_millions"], 2)
    gdp_ls = df["GDP_USD_millions"].tolist()
    gdp_ls = [float("".join(x.split(','))) for x in gdp_ls]
    df["GDP_USD_millions"] = gdp_ls
    df[["GDP_USD_millions"]] = df[["GDP_USD_millions"]] /1000
    df["GDP_USD_millions"] = np.round( df["GDP_USD_millions"], 2)
    df = df.rename(columns={"GDP_USD_millions":"GDP_USD_billions"})
    return df

def load_to_csv(df, csv_path):
    ''' This function saves the final dataframe as a `CSV` file 
	in the provided path. Function returns nothing.'''
    df.to_csv(csv_path)


def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final dataframe as a database table
	with the provided name. Function returns nothing.'''
    df.to_sql(table_name,sql_connection,if_exists = 'replace', index = False)


def run_query(query_statement, sql_connection):
    ''' This function runs the stated query on the database table and
	prints the output on the terminal. Function returns nothing. '''
    print(query_statement)
    query_output = pd.read_sql(query_statement,sql_connection)
    print(query_output)

def log_progress(message):
    ''' This function logs the mentioned message at a given stage of the code execution to a log file. Function returns nothing'''
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now() # get current timestamp 
    
    timestamp = now.strftime(timestamp_format) # convert the timestamp to a string format
    with open(log_text, 'a') as file:
        file.write(timestamp + ' : ' + message + '\n')
    

''' Here, you define the required entities and call the relevant 
functions in the correct order to complete the project. Note that this
portion is not inside any function.'''

log_progress("ETL Job Started"+ " from Wikipedia") 

# log_progress('Preliminaries complete. Initiating ETL process')
log_progress("Extract phase Started") 
extracted_data = extract(url, table_attribs)
print("extracted_data is below:")
print(extracted_data)

log_progress("Extract phase Ended") 
# log_progress('Data extraction complete. Initiating Transformation process')

log_progress("Transform phase Started") 
transformed_data= transform(extracted_data)
print(transformed_data)
log_progress("Transform phase Ended") 
# log_progress('Data transformation complete. Initiating loading process')


log_progress("Load phase Started") 
# log_progress('Data saved to CSV file')
log_progress("Load phase Started" + "load_to_csv") 
load_to_csv(transformed_data, csv_path)
log_progress("done" + "load_to_csv") 

log_progress("Load phase Started" + "load_to_db")
# log_progress('SQL Connection initiated.')
conn = sqlite3.connect(db_name)
load_to_db(transformed_data, conn, table_name)
log_progress("Load phase Ended") 

log_progress('+Data loaded to Database as table. Running the query')

query_statement= f"SELECT * from {table_name} WHERE GDP_USD_billions >= 100"
run_query(query_statement, conn)
log_progress('+Process Complete.')
conn.close()


'''
Important Note:

Maintaining consistency of the lab structure, 
the webpage being accessed is routed through 
an archive database. Often, in case the archive server is busy,
 the users may encounter delayed execution and/or an error such as:
 requests.exceptions.ConnectionError: 
 HTTPSConnectionPool(host='web.archive.org', port=443): Max retries exceeded with url. 
 In such a situation, try executing the code again. In case the problem persists, 
 you can change the URL to the live version, such as: 
 https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29
'''