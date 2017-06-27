import os
import csv
import math
import time
import errno
import shutil
import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from django.http import Http404


# Downloads fangraphs projected points csv
def grabData(folderPath, url, linkTextString):
    today = str(datetime.date.today())
    folderPath += today
    filePath = folderPath + '/FanGraphs Leaderboard.csv'
    if os.path.isfile(filePath):
        pass
    else:
        try:
            os.makedirs(folderPath)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
		
        display = Display(visible=0, size=(800, 600))
        display.start()
        
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", folderPath)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
	
        binary = FirefoxBinary('/usr/local/firefox/firefox')
	
        browser = webdriver.Firefox(firefox_profile=fp, firefox_binary=binary)
        try:
            browser.get(url)
        except WebDriverException:
            raise Http404('Could not access Fangraphs to download projected points. Try again in a few minutes.')
        except TimeoutException:
            pass
	
        linkElem = browser.find_element_by_link_text(linkTextString)
        linkElem.send_keys(Keys.ENTER)
        
        time.sleep(5)
        browser.quit()
        display.stop()
    return filePath
	
# Reads fangraphs csv data into a list	
def getcsvData(filePath):
    with open(filePath) as spreadSheetFile:
        dataList = list(csv.reader(spreadSheetFile))[1:]
    if len(dataList) == 0:
        fanGraphsDataFolder = '/home/django/django_project/baseballproject/fangraphsData'
        for folder in os.listdir(fanGraphsDataFolder):
            if folder != '.DS_Store':
                shutil.rmtree(fanGraphsDataFolder+'/'+folder)
        raise Http404("Projected points have not yet been posted for todays games. Try again in 15 minutes, or when they are up on 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=bat&type=sabersim'")
    return dataList
    
# Reads contest csv data into a list and then deletes the csv     
def getContestData(absFolderPath):
    for folder in os.listdir(absFolderPath):
        if folder != '.DS_Store':
            newFolderPath = absFolderPath + '/' + folder
            for file in os.listdir(newFolderPath):
                filePath = newFolderPath + '/' + file
                try:
                    with open(filePath) as fanDuelFile:
                        contestLineup = list(csv.reader(fanDuelFile))[1:]
                except:
                    shutil.rmtree(newFolderPath)
                    raise Http404("Something is wrong with the csv file that was uploaded. Are you sure you uploaded the right one?")
                shutil.rmtree(newFolderPath)
                return contestLineup
                
# Calculates how many different ways you can choose g items from n item set (used to figure out how many combinations of outfielders and pitchers are possible)
def combinationsCalculator(n, g):
    combos = int(math.factorial(n)/(math.factorial(g)*math.factorial(n-g)))
    return combos