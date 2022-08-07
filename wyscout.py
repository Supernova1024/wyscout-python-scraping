from re import search
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import string
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.alert import Alert

from bs4 import BeautifulSoup

import sys
import os
import argparse

import openpyxl
from xlrd import open_workbook

###
#Libraries to be downloaded
#-selenium
#-bs4
#-pandas
#-lxml
#-openpyxl
###

# Load Chrome Browser
show_browser = True

options = Options()
# options.add_argument('--headless')

scraped_data = []

def bot_driver(url, user_name, user_password):
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    driver.maximize_window()
    
    time.sleep(2)

    # Log in
    # login = driver.find_element_by_xpath("//ul[@id='avia-menu']/li[5]/a")
    # login.click()
    time.sleep(10)

    idd = driver.find_element_by_xpath("//input[@id='login_username']")
    idd.send_keys(user_name)
    passW = driver.find_element_by_xpath("//input[@id='login_password']")
    passW.send_keys(user_password)
    time.sleep(2)

    submit = driver.find_element_by_xpath("//button[@id='login_button']")
    submit.click()
    time.sleep(10)

    try:
        force_login = driver.find_element_by_xpath("//button[@class='btn2_zFM sc-jDwBTQ cUKaFo -block3u2Qh -primary1dLZk']")
        force_login.click()
        print('force loging')
    except :
        print('force login error')

    return driver

def select_country(driver, country_name):
    # Specific Country
    # country = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@commandsource='list@area_list@30']")))
    # country = driver.find_element_by_xpath("//div[@commandsource='list@area_list@30']")
    
    # All the countries
    list_country = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='detail_0_home_navy']/div[1]/div/div")))
    time.sleep(3)
    for entry in list_country:
        if country_name == entry.text:
            print('country click here')
            entry.click()
            return driver, 1
    
    return driver, 0

def select_league(driver, league_name):
    # Specific League
    # league = driver.find_element_by_xpath("//div[@commandsource='list@competition_list@0']")
    
    # All the leagues
    list_league = driver.find_elements_by_xpath("//div[@id='detail_0_area_navy_0']/div[1]/div/div")
    for entry in list_league:
        if league_name == entry.text:
            entry.click()
            return driver, 1
    
    return driver, 0

def select_team(driver, team_names):
    # Specific Team
    # team = driver.find_element_by_xpath("//div[@commandsource='list@team_list@0']")

    flag_team = 0
    list_team = driver.find_elements_by_xpath("//div[@id='detail_0_competition_navy_0']/div[1]/div/div")
    for entry in list_team:
        if entry.text in team_names:
            flag_team = 1
            print('selected team = ', entry.text)
            entry.click()
            time.sleep(2)

            # Stats
            stats = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Stats')))
            stats.click()
            time.sleep(3)

            # Extract the data
            table_stats = WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='detail_0_team_stats']/div/div/div/main/div[3]/div[2]/div")))
            
            # Scroll down
            print('scroll down')
            last_height = driver.execute_script("return arguments[0].scrollHeight;", table_stats)
            print('last_height = ', last_height)
            time.sleep(3)

            while True:
                driver.execute_script("arguments[0].scrollBy(0,arguments[0].scrollHeight)", table_stats)
                time.sleep(5)

                new_height = driver.execute_script("return arguments[0].scrollHeight;", table_stats)
                print('new_height = ', new_height)

                if new_height == last_height:
                    break
                    
                last_height = new_height

            print('scroll end')
            content_stats = driver.page_source
            soup_stats = BeautifulSoup(content_stats, "html.parser")

            table_stats = soup_stats.find('table', attrs={'class': 'teamstats__Index-module__table___1K93L teamstats__Index-module__with-opp___16Rp5'})
            # print(table_stats)
            tbody_stats = table_stats.find('tbody')
            tr_stats = tbody_stats.find_all('tr')
            
            for index in range(2, len(tr_stats)):
                td_list = tr_stats[index].find_all('td')
                stats = {}
                # Team Name, Goals & League, Date
                td_tgld = td_list[0].find_all('div')
                team_goal = td_tgld[0].split(':')
                
                home = team_goal[0].split(' ')
                home_goal = home.split(' ')[-1]
                home_team = ''
                for home_index in range(len(home) - 1):
                    home_team += home[home_index]
                
                away = team_goal[1].split(' ')
                away_goal = away.split(' ')[0]
                away_team = ''
                for away_index in range(1, len(away)):
                    away_team += away[away_index]
                
                print('home - {0}, {1}'.format(home_team, home_goal))
                print('away - {0}, {1}'.format(away_team, away_goal))

            # Return to team selection
            back_team = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@id='detail_0_team_back']")))
            back_team.click()
            time.sleep(5)
    
    if flag_team == 1:
        return driver, 1
    else:
        return driver, 0

if __name__ == "__main__":
    # User input

    # Login - wyscout_url = 'https://wyscout.com/'
    wyscout_url = 'https://platform.wyscout.com/app/?/'
    wyscout_user_name = ''
    wyscout_user_password = ''
    wyscout_driver = bot_driver(wyscout_url, wyscout_user_name, wyscout_user_password)
    time.sleep(10)

    # Select a Country
    country = 'England' # .upper()
    wyscout_driver, succeed = select_country(wyscout_driver, country)
    if succeed == 0:
        print('NO country!')
    time.sleep(7)

    # Select a league
    league = 'Premier League' # .upper()
    wyscout_driver, succeed = select_league(wyscout_driver, league)
    if succeed == 0:
        print('NO League!')
    time.sleep(7)

    # Select team
    team_options = ['Arsenal']
    wyscout_driver, succeed = select_team(wyscout_driver, team_options)
    time.sleep(7)
    if succeed == 0:
        print('NO Team!')
    time.sleep(7)

    # Go to Main Page

    print('!!!Wyscout END!!!')
    # wyscout_driver.quit()