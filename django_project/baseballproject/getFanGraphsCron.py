#!/usr/bin/python

import time
from baseballOptimizer import grabData

batFolderPath = '/home/django/django_project/baseballproject/fangraphsData/battersPP-'
pitFolderPath = '/home/django/django_project/baseballproject/fangraphsData/pitchersPP-'
urlBat = 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=bat&type=sabersim&team=0&lg=all&players=0'
urlPit = 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=pit&type=sabersim&team=0&lg=all&players=0'

grabData(batFolderPath, urlBat, 'Export Data')
time.sleep(5)
grabData(pitFolderPath, urlPit, 'Export Data')
