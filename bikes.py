from asyncore import write
from itertools import count
from turtle import color
import unittest
import sqlite3
import json
import os
import requests
import matplotlib.pyplot as plt
import numpy as np



def readfile():
    pass

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createBikesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Bikes (bike_id INTEGER PRIMARY KEY, name TEXT, latitude NUMBER, longitude NUMBER, city TEXT, country TEXT, company TEXT)")
    conn.commit()

def createCitiesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Cities (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    conn.commit()

def createCountriesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Countries (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    conn.commit()

def createCompaniesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Companies (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    conn.commit()

def createNamesTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Names (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    conn.commit()

def readAPI():
    url = 'http://api.citybik.es/v2/networks'
    resp = requests.get(url)
    if resp.ok:
        results = resp.json()
        return results
    else:
        print('Request not set correctly')
        return None

def addBikes(cur, conn, bikes_dict):
    # get last id inserted into the table
    cur.execute("SELECT * FROM Bikes")
    res = cur.fetchall()
    # if no entries in the table, target gets set to 0
    if len(res) == 0:
        i = 0
    # otherwise, get the id of the last row, add 25 to get target
    else:
        i = res[-1][0] + 1
    target = i + 25

    bike_list = bikes_dict['networks']
    # start from last id and only insert 25 more entries into the table at once
    for row in range(25):
        if i < target and i < len(bike_list):
            id = i

            name = bike_list[i]['name']
            cur.execute("SELECT id FROM Names WHERE name = ?", (name,))
            name_id = cur.fetchone()[0]

            city = bike_list[i]['location']['city']
            cur.execute("SELECT id FROM Cities WHERE name = ?", (city,))
            city_id = cur.fetchone()[0]

            country = bike_list[i]['location']['country']
            cur.execute("SELECT id FROM Countries WHERE name = ?", (country,))
            country_id = cur.fetchone()[0]

            lat = bike_list[i]['location']['latitude']

            lon = bike_list[i]['location']['longitude']

            if bike_list[i]['company'] == None:
                company = ''
                company_id = None
            else:
                company = bike_list[i]['company'][0]
                cur.execute("SELECT id FROM Companies WHERE name = ?", (company,))
                company_id = cur.fetchone()[0]

            cur.execute("INSERT OR IGNORE INTO Bikes (bike_id, name, city, country, latitude, longitude, company) VALUES (?, ?, ?, ?, ?, ?, ?)", (id, name_id, city_id, country_id, lat, lon, company_id))
            i += 1
    conn.commit()

def addCities(cur, conn, bikes_dict):
    cur.execute("SELECT * FROM Cities")
    res = cur.fetchall()
    if len(res) == 0:
        for row in bikes_dict['networks']:
            city = row['location']['city']
            cur.execute("INSERT OR IGNORE INTO Cities (name) VALUES (?)", (city,))
        conn.commit()
    

def addCountries(cur, conn, bikes_dict):
    cur.execute("SELECT * FROM Countries")
    res = cur.fetchall()
    if len(res) == 0:
        for row in bikes_dict['networks']:
            country = row['location']['country']
            cur.execute("INSERT OR IGNORE INTO Countries (name) VALUES (?)", (country,))
        conn.commit()

def addCompanies(cur, conn, bikes_dict):
    cur.execute("SELECT * FROM Companies")
    res = cur.fetchall()
    if len(res) == 0:
        for row in bikes_dict['networks']:
            if row['company'] == None:
                company = ''
            else:
                company = row['company'][0]

            cur.execute("INSERT OR IGNORE INTO Companies (name) VALUES (?)", (company,))
        conn.commit()

def addNames(cur, conn, bikes_dict):
    cur.execute("SELECT * FROM Cities")
    res = cur.fetchall()
    if len(res) == 0:
        for row in bikes_dict['networks']:
            name = row['name']
            cur.execute("INSERT OR IGNORE INTO Names (name) VALUES (?)", (name,))
        conn.commit()

def getCounts(cur, conn):
    cur.execute("SELECT Cities.name, Countries.name, COUNT(*) FROM Bikes JOIN Cities ON Bikes.city = Cities.id JOIN Countries ON Bikes.country = Countries.id GROUP BY city")
    res = cur.fetchall()
    return res

def getMaxCount(count_list):
    max = 0
    max_city = []

    for row in count_list:
        if row[2] > max:
            max_city.clear()
            max_city.append((row[0], row[1]))
            max = row[2]
        elif row[2] == max:
            max_city.append((row[0], row[1]))
    return (max, max_city)

def writeData(counts):
    f = open("bike_data.csv", "w")

    f.write("CITY,COUNTRY,NUMBER OF BIKES\n")
    for row in counts:
        f.write(str(row[0]) + "," + str(row[1]) + "," + str(row[2]) + "\n")

    f.close()

def bikesByCompany(cur, conn):
    cur.execute("SELECT Companies.name, COUNT(*) FROM Bikes JOIN Companies ON Bikes.company = Companies.id GROUP BY company")
    res = cur.fetchall()
    res.sort(key = lambda x: x[1], reverse=True) 
    companies = []
    counts = []
    for row in res[:10]:
        # if row[1] < 9:
        #     continue
        # else:
        #     companies.append(row[0])
        #     counts.append(row[1])
        companies.append(row[0])
        counts.append(row[1])

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('yellow')
    ax.stem(companies, counts, linefmt='yellow')
    ax.patch.set_facecolor('blue')
    ax.set_xlabel('Company Names')
    ax.set_ylabel('Bikes per Company')
    ax.set_title('TOP 10 EBIKE COMPANIES IN THE WORLD')
    plt.xticks(rotation = 70) 
    plt.tight_layout()
    plt.show()

def main():
    # create database
    cur, conn = setUpDatabase('bikes.db')
    # set up tables
    createBikesTable(cur, conn)
    createCitiesTable(cur, conn)
    createCountriesTable(cur, conn)
    createCompaniesTable(cur, conn)
    createNamesTable(cur, conn)
    
    # read in the API
    bikes_dict = readAPI()
    # add the data to the tables as long as reading API goes okay
    if bikes_dict != None:
        addCities(cur, conn, bikes_dict)
        addCountries(cur, conn, bikes_dict)
        addCompanies(cur, conn, bikes_dict)
        addNames(cur, conn, bikes_dict)
        addBikes(cur, conn, bikes_dict)
    counts = getCounts(cur, conn)
    max_cities = getMaxCount(counts)
    writeData(counts)
    bikesByCompany(cur, conn)
    
if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)