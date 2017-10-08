#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 18:55:27 2017

@author: mincev

Note: 
    For an explanation of how to use finam please see the following link:
    https://stackoverflow.com/questions/15612003/how-to-push-a-new-folder\
    -containing-other-folders-and-files-to-an-existing-git    
"""
import random
import os
from time import sleep
from helper import helper 
from format_helper import format_helper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FINAM_Crawler(object):
    """
    Class used for scraping Finams historical technical data. 
    Finam currently offers 1min denominated data spanning at least two years.
    When run as main, we download TICKER, PER, DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL 
    data spanning from 2014-17 and save a dictionary with values of 
    DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL as a pickle file 
    
    Note: You may have to change the DRIVER_PATHand add it to webdiriver.Chrome()
    """
    global URL, DRIVER_PATH
    URL = "https://www.finam.ru/profile/moex-akcii/gazprom/export/"
    DRIVER_PATH = ""
    
    def __init__(self, market = 17): # 17 -> "Акции США(BATS)/US Equity"
        """
        Input:
            market (17) = 17 -> "Акции США(BATS)/US Equity" (use LOOKUP for index)
                            stands for the US market and subsequently offers a list
                            of 40 companies to choose technicals from (see list below).
        """
        assert type(market) is int
        assert market > 0 and market < 36
        self.market = market
    
    def close_pop_up(self, driver, xpath = '/html/body/div[25]/a', 
                     close_by_xpath = True, print_on = True):
        """
        Closes JS pop-up with xpath
        Input: 
            driver (webdriver) = eg: webdriver.Chrome()
            xpath (str) = xml path to pop-up
            close_by_xpath = if True xpath is used to identify cancel otherwise 
                             use class id
            print_on = if True printing messages is enabelled
        Output:
            (bool) = True if pop-up-closed
        """
        assert type(xpath) is str 
        
        #wait for pop up - and press cancel
        try:
            if print_on: print("Closing pop-up window")
            wait = WebDriverWait(driver, 5)
            if close_by_xpath:
                pop_up_loaded = wait.until(
                                   EC.presence_of_element_located((By.XPATH, xpath))
                                   )
            else:
                pop_up_loaded = wait.until(
                                   EC.presence_of_element_located((By.CLASS, 'cancel'))
                                   )
            pop_up_loaded.click()
        except:
            if print_on: print("No pop-up appeared")
            return False 
        return True 
    
    def wait_for_redirect(self, driver, url = URL, until_url_changes = True):
        """
        Checks that new url is different to previous 'url'
        Input:
            driver (webdriver) = eg: webdriver.Chrome()
            url (str) = previous url
            until_url_changes = if True wait for different url else wait for id
        Output:
            -
        """
        assert type(url) is str
        try:
            wait = WebDriverWait(driver, 3)
            if until_url_changes:
                wait.until_not(
                               lambda browser: browser.current_url == URL
                               )
            else: 
                wait.unitl(
                        driver.find_element_by_id('issuer-profile-header')
                        )
        except:
            print("Error occured whilst waiting for redirect\n")
        return 
    
    def close_pop_up_with_loop(self, driver, start = 21, end = 30, use_assert = True):
        """
        Specialist function:
        Close pop up when xpath is not exactly known. Only continue if pop up is
        succesfully closed
        Input: 
            driver = webdriver
            start (int) = div to start at (div keeps changing and hence we test range)
            end (int) = div to end at 
            use_assert = use 'assert' statement if True (if false the program is not
                                                         stopped if no pop up found)
        """
        assert type(start) and type(end) is int
        assert type(use_assert) is bool
        
        print("Closing pop-up")
        for i in range(start, end):
            close_p_up = self.close_pop_up(driver, '/html/body/div[{0}]/a'.format(str(i)), \
                                           print_on = False)
            if close_p_up is True:
                break
            
        if use_assert:
            assert close_p_up is True
        return
    
    def loop_find_by_xpath(self, driver, xpath, object_to_find, start_range):
        """
        Similarly to the loop close function we experinced problems filling in 
        forms due to adds moving divs. Hence this function tries to find the correct 
        div using a try except loop. 
        Input: 
            driver = webdriver
            xpath (str) = eg: '/html/body/div[{0}]/div/ul/li[{1}]/a'
            object_to_find (int) = number placed in {1} in xpath
            start_range (int) = div{0} to start with
        Output:
            -
        """
        assert type(xpath) is str
        assert type(start_range) and type(object_to_find) is int 
        
        found_object = False
        for i in range(start_range, (start_range + 9)):
            try:
                driver.find_element_by_xpath(xpath.format(str(i), str(object_to_find))).click()
                found_object = True
                break
            except: 
                continue
        
        assert found_object is True
        return
    
    def download_data(self, security = 2, start_date = [2016, 1], \
                      end_date = [2017, 8], frequency = 2, file_path = "/home/mincev//Downloads/"):
        """
        function that downloads technicals spanning start_date - end_date 
        for 'company' found in 'self.market'. THis data is saved as 
        'save_name' csv 
        Input: 
            security (int) = eg: 2 -> 3G co (see lookup list of available 
                              companies for US at the bottom of script)
            frequency (int) = eg 2 -> 1 min interval (see lookup)
            start_date (list int) = [year, month] eg(2017, 1) -> Jan 2017
            end_date (list int) = [year, month]
            file_path (str) = path to downolad folder
        Output
            - download file
        """
        assert type(security) and type(frequency) and type(end_date[0]) \
                and type(start_date[0]) is int 
        assert type(file_path) is str
        assert security > 0 
        assert (end_date[0] - start_date[0]) >= 0
        assert len(start_date) == len(end_date)
        
        #define variabes:
        save_name = str(security) + "_" + str(start_date[0]) + "_" + str(end_date[0])
        start_year = str(39 - (2017 - start_date[0]))
        start_month = str(start_date[1])
        end_year = str(end_date[0] - start_date[0] + 1)
        end_month = str(end_date[1])
        downloaded_file_dir = file_path + save_name + '.csv'
        
        #Fill in form using Selenium: 
        print("\nOpening finam in chromedriver")
        driver = webdriver.Chrome()
        driver.get(URL)
        assert "Финам.ru" in driver.title  
        
        #close pop up if exists 
        self.close_pop_up_with_loop(driver, use_assert = False) 
        
        print("Selecting Market")
        driver.find_element_by_class_name("finam-ui-quote-selector-market").click()
        self.loop_find_by_xpath(driver, '/html/body/div[{0}]/div/ul/li[{1}]/a', \
                                self.market, 11)
        
        print("Selecting Security")
        driver.find_element_by_xpath('//*[@id="issuer-profile-header"]/div[2]/div').click()
        self.loop_find_by_xpath(driver,'/html/body/div[{0}]/div/ul/li[{1}]/a', \
                                security, 11)
        sleep(random.randint(1,3))
        
        #wait for redirect and close pop-up
        self.wait_for_redirect(driver, URL)
        self.wait_for_redirect(driver, until_url_changes=False)
        #BUG TO FIX - unable to always close pop-up hence try many 
        self.close_pop_up_with_loop(driver)            
        self.close_pop_up_with_loop(driver, use_assert = False)
        
        #save new url name
        new_url = driver.current_url
        
        print("Selecting frequency")
        driver.find_element_by_xpath('//*[@id="issuer-profile-export-first-row"]'+
                                     '/td[3]/div').click()
        self.loop_find_by_xpath(driver,'/html/body/div[{0}]/div/ul/li[{1}]/a',
                                frequency, 13)
        #sleep(random.randint(1,3))
        
        print("Selecting save data type")
        driver.find_element_by_xpath('//*[@id="issuer-profile-export-second-row"]' + 
                                     '/td[3]/div/div[1]').click()
        self.loop_find_by_xpath(driver, '/html/body/div[{0}]/div/ul/li[{1}]/a', 2, 14)
        
        print("Inputting Start Date")
        driver.find_element_by_id('issuer-profile-export-from').click()
        #select month
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[1]').click()
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[1]' + 
                                     '/option[{0}]'.format(start_month)).click()
        #select year - 39 is 2017
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[2]').click()
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[2]' + 
                                     '/option[{0}]'.format(start_year)).click()
        #select day - start moves depending on month 1 is sometimes 1 sometimes 2 ....
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/table/tbody' + 
                                     '/tr[1]/td[6]/a').click()
        sleep(random.randint(1,3))
        
        #wait for redirect
        self.wait_for_redirect(driver, new_url)
        
        print("Inputting End Date")
        driver.find_element_by_id('issuer-profile-export-to').click()
        #select month
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[1]').click()
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[1]' + 
                                     '/option[{0}]'.format(end_month)).click()
        #select year - 39 is 2017
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[2]').click()
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[2]' + 
                                     '/option[{0}]'.format(end_year)).click()
        #select day - start moves depending on month 1 is sometimes 1 sometimes 2 ....
        driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/table/tbody' + 
                                     '/tr[3]/td[6]').click()
        sleep(random.randint(1,3))
        
        print("Inputting save name")
        text_box = driver.find_element_by_xpath('//*[@id="issuer-profile-export-file-name"]');
        for _ in range(30):
            text_box.send_keys(Keys.BACKSPACE)
        text_box.send_keys(save_name)
        
        print("Downloading Data....")
        driver.find_element_by_xpath('//*[@id="issuer-profile-export-button"]/button').click()
        
        #check that file was downloaded
        count = 0
        while(os.path.isfile(downloaded_file_dir) is False):
            if count > 12: 
                print('Failed to Download Data\n******************')
                return 
            sleep(5)
            count += 1
        
        driver.close()
        print("Succesfully downloaded data")
        print("----------------------------\n")
        return 
        
if __name__ == "__main__":
    """
    Run to download data from FINAM for all 45 US companies. As downloading only
    supports getting 1y worth of data multiple files are fetched for any given 
    company. We merge these files and store the data in a dictioanry. These 
    dictionaries are stored as pickle files. Note, we choose to create multiple 
    pickle files (one for each company) to facilitate uploading to github.
    """
    #define variables
    crawler = FINAM_Crawler()
    securities_to_download = range(2, 46)
    number_of_securities = len(securities_to_download)
    start_dates  = [[2016, 1], [2015, 1], [2014, 1]]
    end_dates = [[2017, 8], [2016, 2], [2015, 2]]
    file_name_for_saving = '{0}_' + str(start_dates[-1][0]) + "_" + str(end_dates[0][0])
    name_for_saving_key = file_name_for_saving + "_keys"
    number_of_downloads = len(end_dates)
    #file_path = "/home/mincev//Downloads/" 
    file_path = "/media/mincev/UUI/finance_data/"
    file_type = '.csv'
    assert len(start_dates) == len(end_dates) 
    
    #define file save names - start of with end of name and then add start 
    #eg: {0}_2016_2017 -> 2_2016_2017 -> dict[2] = '2_2016_2017
    file_names = []
    for i in range(number_of_downloads):
        file_name = "{0}_" + str(start_dates[i][0]) + "_" + str(end_dates[i][0]) 
        file_names.append(file_name)
        
    files_dict = {}
    for i in securities_to_download:
        file_name = []
        for j in range(number_of_downloads):
            file_name.append(file_names[j].format(str(i)))
        files_dict[i] = file_name
        
    #test case 
    execute_test = input("Do you want to excecute the test crawl for one comp?\n" + \
                         "(y,n): ")
    if execute_test.lower() == 'y':
        crawler.download_data(securities_to_download[0], start_dates[0], end_dates[0])
        crawler.download_data(securities_to_download[0], start_dates[1], end_dates[1])     
    assert os.path.isfile(file_path + '2_2015_2016' + file_type)
    assert os.path.isfile(file_path + '2_2016_2017' + file_type)
    
    #Crawl finam
    execute_crawler = input("Do you want to excecute the crawler?\n" + \
                            "(y,n): ")
    if execute_crawler.lower() == 'y': 
        for i in securities_to_download[1:]:
            try:
                print('Downloading data for {0}'.format(str(i)))
                for j in range(len(start_dates)):
                    crawler.download_data(i, start_dates[j], end_dates[j])
            except:
                continue
        
    #merge downloaded files
    #merges files from FINAM_Crawler and stores these as a pickle dictionary 
    format_helper = format_helper()
    for i in securities_to_download:
        print("Merging files for company: {0}".format(str(i)))
        try:
            data_dic, dic_keys = format_helper.merge_csvs(files_dict[i], 
                                                          file_path = file_path, 
                                                          start_index = 2)
            save_name = file_name_for_saving.format(str(i))
            helper.save_obj(save_name , data_dic)
            save_dic_key_name = name_for_saving_key.format(str(i))
            helper.save_obj(save_dic_key_name, dic_keys)
            test_dict = helper.load_obj(save_name)
            assert len(test_dict) == len(data_dic)
            print("Lengths match for {0}".format(i))
            assert os.path.isfile('obj/' + save_name  + '.pkl') is True
            print("Successfully merged files for company: {0}".format(str(i)))
        except:
            print("Failed to merge files for company: {0}".format(str(i)))
            print("--------------------------------------")
            continue
    
    for i, key in enumerate(data_dic):
        if i % 10000 == 0:
            print(key)
    
# =============================================================================
# """
# LIST OF AVAILABLE FREQUENCIES:
# 1 - тики
# 2 - 1 min.
# 3 - 5 min.
# 4 - 10 min.
# 5 - 15 min.
# 6 - 30 min.
# 7 - 1 hour
# 8 - 1 day
# 9 - 1 week
# 10 - 1 month     
# """
# 
# """
# LIST OF AVAILABLE COMPANIES LOOKUP:
# 1 - не выбрано
# 2 - 3M co
# 3 - AT&T Inc
# 4 - Adobe Systems Inc.
# 5 - Alcoa Inc
# 6 - Alphabet Inc.
# 7 - American Express
# 8 - American Intl Group Inc
# 9 - American Tower Corp. Cl A
# 10 - Apple Inc.
# 11 - Applied Materials Inc.
# 12 - Bank of America
# 13 - Boeing Co
# 14 - CA Inc.
# 15 - Caterpillar Inc
# 16 - Chevron
# 17 - Cisco Systems Inc.
# 18 - Citigroup Inc
# 19 - Coca-Cola co
# 20 - Corning Inc.
# 21 - DuPont
# 22 - EMC Corp.
# 23 - Exxon Mobil
# 24 - First Solar Inc.
# 25 - GE
# 26 - Goldman Sachs Group Inc
# 27 - Hewlett-Packard
# 28 - Home Depot
# 29 - IBM
# 30 - Int.Paper
# 31 - Intel Corp
# 32 - JPMorgan Chase&Co
# 33 - Johnson & Johnson
# 34 - McDonalds
# 35 - Merck & Co
# 36 - Microsoft Corp
# 37 - Pfizer Inc
# 38 - Procter & Gamble
# 39 - Travelers Comp.
# 40 - United Technologies
# 41 - Verizon Communications
# 42 - Wal-Mart Store
# 43 - Walt Disney
# 44 - Wells Fargo
# 45 - Yahoo INC
# 46 - Яндекс
# """
# 
# """
# LIST OF AVAILABLE MARKETS LOOKUP:
# 1 - MosBirda top
# 2 - MosBirja shares
# 3 - MosBirza futures
# 4 - Ruble's exchange rate
# 5 - MosBiří currency market
# 6 - MosBird bond
# 7 - MosBirzh non-listed bonds
# 8 - MosBirja pytha
# 9 - The Moscow-based ETF
# 10 - Receipts
# 11 - Eurobonds
# 12 - St. Petersburg Stock Exchange
# 13 - World Indices
# 14 - Goods
# 15 - World currencies
# 16 - Crypto currency
# 17 - US stocks (BATS)
# 18 - Futures USA
# 19 - Sectors of the US economy
# 20 - Government bonds of the USA
# 21 - ETF
# 22 - World Economic Indices
# 23 - Russian indexes
# 24 - RTS
# 25 - Boorde
# 26 - RTS-GAZ
# 27 - FORTS Archive
# 28 - Raw Materials Archive
# 29 - RTS Standard Archive
# 30 - MICEX Archive
# 31 - RTS Archive
# 32 - SPFB Archive
# 33 - RTS-BOARD Archive
# 34 - Receipts Archive
# 35 - Industries
# """
# =============================================================================

