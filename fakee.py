from typing import Final
import os
from dotenv import load_dotenv
load_dotenv()

import pyodbc # To connect to MS SQL (SQL SERVER)
import requests # To make requests
from bs4 import BeautifulSoup
import pandas as pd

SERVER_NAME: Final = os.environ.get('SERVER_NAME')
DATABASE_NAME: Final = os.environ.get('DATABASE_NAME')
USER_NAME = os.environ.get('USER_NAME')
USER_PASSWORD = os.environ.get('USER_PASSWORD')


def setup_mssql_connection():
    conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"
                          f"SERVER={SERVER_NAME};"  
                          f"DATABASE={DATABASE_NAME};"
                          "Trusted_Connection=yes;")
    cursor = conn.cursor()
    cursor.execute(
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='jobs' AND xtype='U')
        CREATE TABLE jobs (
            id INT IDENTITY(1,1) PRIMARY KEY,
            job_title NVARCHAR(255),
            creator NVARCHAR(255),
            address NVARCHAR(255),
            date DATE
        )
        """
    )
    conn.commit()
    return conn, cursor

def scrape_jobs():
    url = "https://realpython.github.io/fake-jobs/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = []
    for job in soup.find_all('div', class_='card-content'):
        job_title = job.find('h2', class_='title').text.strip()
        creator = job.find('h3', class_='company').text.strip()
        address = job.find('p', class_='location').text.strip()
        date = job.find('time')['datetime']
        jobs.append((job_title, creator, address, date))
    return jobs

def insert_jobs(cursor, jobs):
    cursor.executemany('''
        INSERT INTO jobs (job_title, creator, address, date)
        VALUES (?, ?, ?, ?)
    ''', jobs)

def display_jobs_as_dataframe(cursor):
    cursor.execute('''
        SELECT id, job_title, creator, address, date FROM jobs
    ''')
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "Job Title", "Company", "Location", "Date"])
    print(df)

def main():
    conn, cursor = setup_mssql_connection()
    jobs = scrape_jobs()
    insert_jobs(cursor, jobs)
    conn.commit()
    display_jobs_as_dataframe(cursor)
    conn.close()
    print('Records inserted successfully')

if __name__ == "__main__":
    main()