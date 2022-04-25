from unicodedata import category
from xml.sax import parseString
from bs4 import BeautifulSoup
from numpy import equal
import requests
import re
import os
import csv
import unittest
import matplotlib.pyplot as plt
from statistics import stdev
from statistics import mean
from statistics import median
import numpy as np
from scipy.stats import kde

def get_data():
    url = 'https://copenhagenizeindex.eu/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    city_list = []  
    table = soup.find('div', class_ = 'items')
    specific_cities = table.find_all('a', class_ = 'link')
    for specific_city in specific_cities:
        city_rank = specific_city.find('div', class_ = 'index19').text.strip()
        city_name = specific_city.find('div', class_ = 'name colorize').text.strip()
        city_score = specific_city.find('div', class_ = 'total-score total-score--sm').text.strip()
        city_list.append((city_rank, city_name, city_score))
    print(city_list)
    return(city_list)

def write_csv(data, filename):
    with open(filename, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        header = ['City Rank','City Name','City Score']
        writer.writerow(header)
        for i in range(len(data)):
            text = [data[i][0], data[i][1], data[i][2]]
            writer.writerow(text)

def city_lst(city_list):
    cities = []
    for item in city_list:
        city = item[1]  
        cities.append(city)
    return(cities)

def score_lst(city_list):
    scores_string = ''
    scores = []
    for item in city_list:
        score_perc = str(item[2])       
        scores_string += score_perc
    score_str_list = re.findall('\d+\.\d+', scores_string)
    for score_ in score_str_list:
        score = float(score_)
        scores.append(score)
    return(scores)

def rank_lst(city_list):
    ranks = []
    for item in city_list:
        rank = int(item[0])  
        ranks.append(rank)
    return(ranks)

def stats(scores):
    stats = []
    mean_value = round(mean(scores), 1)
    median_value = round(median(scores), 1)
    std = round(stdev(scores), 1)
    scores_array = np.array(scores)
    print("Mean of scores: ", mean_value)
    print("Median of scores: ", median_value)
    print("Standard Deviation of scores: ", std)
    print("Q1 quantile of scores: ", round(np.quantile(scores_array, .25), 1))
    print("Q2 quantile of scores: ", round(np.quantile(scores_array, .50), 1))
    print("Q3 quantile of scores: ", round(np.quantile(scores_array, .75), 1))
    print("100th quantile of scores: ", round(np.quantile(scores_array, 1), 1)) 
    stats.append(mean_value)
    stats.append(median_value)
    stats.append(std)
    stats.append(round(np.quantile(scores_array, .25), 1))
    stats.append(round(np.quantile(scores_array, .50), 1))
    stats.append(round(np.quantile(scores_array, .75), 1))
    stats.append(round(np.quantile(scores_array, 1), 1))
    print(stats)
    return stats

def city_score_visual(cities, scores):
    plt.figure(1, figsize=(10, 10))
    ax = plt.axes()
    ax.set_facecolor('0')
    plt.barh(cities, scores, color = 'grey')
    plt.gca().invert_yaxis()
    for index, value in enumerate(scores):
        plt.text(value, index, str(value), color = 'w')
    plt.suptitle('The Most Bicycle-Friendly Cities in 2019')
    plt.xlabel('Score')
    plt.ylabel('City')
    plt.savefig('The Most Bicycle-Friendly Cities in 2019')
    plt.show()

def stats_visual(scores_stats):
    Name = ['Mean', 'Median', 'Standard Deviation', 'Q1', 'Q2', 'Q3', 'Q4']
    plt.figure(1, figsize=(10, 10))
    ax = plt.axes()
    ax.set_facecolor('0')
    plt.bar(Name, scores_stats, color = 'grey')
    for value, index in enumerate(scores_stats):
        plt.text(value, index, str(index), color = 'w')
    plt.suptitle('Statistics of the Copenhagenize Index')
    plt.xlabel('Stats')
    plt.ylabel('Scores')
    plt.savefig('Statistics of the Copenhagenize Index')
    plt.show()  

def kernal_estimate_visual(ranks, scores):
    fig = plt.figure(1, figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('yellow')
    nbins=300
    x = np.array(ranks)
    y = np.array(scores)
    k = kde.gaussian_kde([x,y])
    xi, yi = np.mgrid[x.min() : x.max() : nbins * 1j, y.min() : y.max() : nbins*1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto')
    plt.colorbar()
    ax.set_xlabel('Rank')
    ax.set_ylabel('Scores')
    plt.suptitle('Kernel Density Estimate - Rank & Scores')
    plt.xticks(range(1,21))
    plt.show()

def main():
    city_list = get_data()
    write_csv(city_list, 'websiteoutput.csv')
    cities = city_lst(city_list)
    scores = score_lst(city_list)
    ranks = rank_lst(city_list)
    scores_stats = stats(scores)
    city_score_visual(cities, scores)
    stats_visual(scores_stats)
    kernal_estimate_visual(ranks, scores)

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)