#!/usr/bin/python

import shutil
import datetime


batFolderPath = '/home/django/django_project/baseballproject/fangraphsData/battersPP-'
pitFolderPath = '/home/django/django_project/baseballproject/fangraphsData/pitchersPP-'
contestPath = '/home/django/django_project/media/documents'

today = str(datetime.date.today())

batFolderPath += today
pitFolderPath += today

shutil.rmtree(batFolderPath)
shutil.rmtree(pitFolderPath)

for folder in os.listdir(contestPath):
    if folder != '.DS_Store':
        oldFolderPath = contestPath + '/' + folder
        shutil.rmtree(oldFolderPath)


