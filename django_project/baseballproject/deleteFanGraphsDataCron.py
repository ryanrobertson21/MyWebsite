#!/usr/bin/python

import datetime, shutil


batFolderPath = '/home/django/django_project/baseballproject/fangraphsData/battersPP-'
pitFolderPath = '/home/django/django_project/baseballproject/fangraphsData/pitchersPP-'

today = str(datetime.date.today())

batFolderPath += today
pitFolderPath += today

shutil.rmtree(batFolderPath)
shutil.rmtree(pitFolderPath)


