import os
import time
import shutil
from django.shortcuts import render
from django.template import RequestContext
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from baseballproject.models import Document
from baseballproject.forms import DocumentForm
from optimizerFunctions import grabData, getcsvData, getContestData, combinationsCalculator
from optimizeFanDuel import teamDictFanDuel, editPlayerName, findMaxPPFanDuel
from optimizeDraftKings import teamDictDraftKings, findMaxPPDraftKings
from optimizeYahoo import teamDictYahoo, editPlayerNameYahoo, findMaxPPYahoo

    
def list(request):
        
    # Handle csv file upload
    if request.method == 'POST':
        usersCSV = DocumentForm(request.POST, request.FILES)
        contestName = request.POST["contest"]

        if usersCSV.is_valid(): 
            contestCSV = Document(docfile=request.FILES['docfile'])
            contestCSV.save()
            
            # Read in contest data and convert into a list
            contestLineup = getContestData('/home/django/django_project/media/documents')
            
            # Get projected points data from fangraphs and convert into a list
            batFolderPath = '/home/django/django_project/baseballproject/fangraphsData/battersPP-'
            pitFolderPath = '/home/django/django_project/baseballproject/fangraphsData/pitchersPP-'
            urlBat = 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=bat&type=sabersim&team=0&lg=all&players=0'
            urlPit = 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=pit&type=sabersim&team=0&lg=all&players=0'
             
            batFile = grabData(batFolderPath, urlBat, 'Export Data')
            time.sleep(3)
            pitFile = grabData(pitFolderPath, urlPit, 'Export Data')
            
            battersPP = getcsvData(batFile)
            pitchersPP = getcsvData(pitFile)
            
             
    
            # If user selected FANDUEL
            if contestName == 'fanduel':
            
                # Match up the players from fanduel with their projected points from fangraphs
                playerDict = {}
                for row in contestLineup:
                    for ppRow in battersPP:
                        fdName = editPlayerName(row, 3)
                        ppName = editPlayerName(ppRow, 0)
                    
                        if fdName == ppName and row[1] != 'P' and (teamDictFanDuel[row[9]] == ppRow[1] or ppRow[1] == ''):
                            playerList = [row[1], row[3], float(ppRow[-3]), int(row[7]), row[9]]
                            playerDict[ppRow[-1]] = playerList
                        
                for row in contestLineup:
                    for ppRow in pitchersPP:
                        fdName = editPlayerName(row, 3)
                        ppName = editPlayerName(ppRow, 0)
                    
                        if fdName == ppName and row[1] == 'P' and (teamDictFanDuel[row[9]] == ppRow[1] or ppRow[1] == ''):
                            playerList = [row[1], row[3], float(ppRow[-3]), int(row[7]), row[9]]
                            playerDict[ppRow[-1]] = playerList
            
                # Assign the players to dictionaries by position
                pitchers = {}
                catchers = {}
                firstBase = {}
                secondBase = {}
                thirdBase = {}
                shortStop = {}
                outfielders = {}
            

                for ids in playerDict:
            
                    if playerDict[ids][0] == 'P':
                        pitchers[ids] = playerDict[ids]
                    elif playerDict[ids][0] == 'C':
                        catchers[ids] = playerDict[ids]
                    elif playerDict[ids][0] == '1B':
                        firstBase[ids] = playerDict[ids]
                    elif playerDict[ids][0] == '2B':
                        secondBase[ids] = playerDict[ids]
                    elif playerDict[ids][0] == '3B':
                        thirdBase[ids] = playerDict[ids]
                    elif playerDict[ids][0] == 'SS':
                        shortStop[ids] = playerDict[ids]
                    elif playerDict[ids][0] == 'OF':
                        outfielders[ids] = playerDict[ids]
                    
                # Compute the total number of possible lineups
                try:        
                    numLineups = "{:,d}".format(len(pitchers) * len(catchers) * len(firstBase) * len(secondBase) * len(thirdBase) * len(shortStop) * combinationsCalculator(len(outfielders),3))
                    if numLineups == 0:
                        raise Http404('The csv file was read in incorrectly. Please try to submit again, and make sure you are uploading the correct csv file and selecting the correct contest.')
                except ValueError:
                    raise Http404('The csv file was read in incorrectly. Please try to submit again, and make sure you are uploading the correct csv file and selecting the correct contest.')
                    
                # Run the fanduel optimizer program
                theOptimalLineup, pp = findMaxPPFanDuel(playerDict,pitchers,catchers,firstBase,secondBase,thirdBase,shortStop,outfielders)
            
            
            
            # If user selected DRAFTKINGS
            elif contestName == 'draftkings':
                
                # Match up the players from draftkings with their projected points from fangraphs
                playerDict = {}

                for row in contestLineup:
                    for ppRow in battersPP:
                        dkName = editPlayerName(row, 1)
                        ppName = editPlayerName(ppRow, 0)

                        if dkName == ppName and 'P' not in row[0] and (teamDictDraftKings[row[-1]] == ppRow[1] or ppRow[1] == ''):
                            playerList = [row[0], row[1], float(ppRow[-2]), int(row[2]), row[-1]]
                            playerDict[ppRow[-1]] = playerList

                for row in contestLineup:
                    for ppRow in pitchersPP:
                        dkName = editPlayerName(row, 1)
                        ppName = editPlayerName(ppRow, 0)

                        if dkName == ppName and 'P' in row[0] and (teamDictDraftKings[row[-1]] == ppRow[1] or ppRow[1] == ''):
                            playerList = [row[0], row[1], float(ppRow[-2]), int(row[2]), row[-1]]
                            playerDict[ppRow[-1]] = playerList
                
                # Assign the players to dictionaries by position            
                pitchers = {}
                catchers = {}
                firstBase = {}
                secondBase = {}
                thirdBase = {}
                shortStop = {}
                outfielders = {}
                playersCantElim = {}

                for ids in playerDict:

                    if 'P' in playerDict[ids][0] :
                        pitchers[ids] = playerDict[ids]
                    if 'C' in playerDict[ids][0]:
                        catchers[ids] = playerDict[ids]
                    if '1B' in playerDict[ids][0]:
                        firstBase[ids] = playerDict[ids]
                    if '2B' in playerDict[ids][0]:
                        secondBase[ids] = playerDict[ids]
                    if '3B' in  playerDict[ids][0]:
                        thirdBase[ids] = playerDict[ids]
                    if 'SS' in playerDict[ids][0]:
                        shortStop[ids] = playerDict[ids]
                    if 'OF' in playerDict[ids][0]:
                        outfielders[ids] = playerDict[ids]
                    if '/' in playerDict[ids][0]:
                        playersCantElim[ids] = playerDict[ids]
                
                # Compute the total number of possible lineups 
                try:        
                    numLineups = "{:,d}\n".format(combinationsCalculator(len(pitchers), 2) * len(catchers) * len(firstBase) * len(secondBase) * len(thirdBase) * len(shortStop) * combinationsCalculator(len(outfielders), 3))
                    if numLineups == 0:
                        raise Http404('The csv file was read in incorrectly. Please try to submit again, and make sure you are uploading the correct csv file and selecting the correct contest.')
                except ValueError:
                    raise Http404('The csv file was read in incorrectly. Please try to submit again, and make sure you are uploading the correct csv file and selecting the correct contest.')
                    
                # Run the draftkings optimizer program            
                theOptimalLineup, pp = findMaxPPDraftKings(playerDict,pitchers,catchers,firstBase,secondBase,thirdBase,shortStop,outfielders, playersCantElim) 
                           
                           
                            
            # If user selected YAHOO
            else:
                
                # Match up the players from yahoo with their projected points from fangraphs
                playerDict = {}
                
                for row in contestLineup:
                    for ppRow in battersPP:
                        yahooName = editPlayerNameYahoo(row, 1, 3)
                        ppName = editPlayerNameYahoo(ppRow, 0, 1)

                        if yahooName == ppName and row[3] != 'P' and (teamDictYahoo[row[4]] == ppRow[1] or ppRow[1] == ''):
                            playerList = [row[3], row[1] + " " + row[2], float(ppRow[-4]), int(row[8]), row[4]]
                            playerDict[ppRow[-1]] = playerList
                            
                for row in contestLineup:
                    for ppRow in pitchersPP:
                        yahooName = editPlayerNameYahoo(row, 1, 3)
                        ppName = editPlayerNameYahoo(ppRow, 0, 1)

                        if yahooName == ppName and row[3] == 'P' and (teamDictYahoo[row[4]] == ppRow[1] or ppRow[1] == ''):
                            playerList = [row[3], row[1] + " " + row[2], float(ppRow[-4]), int(row[8]), row[4]]
                            playerDict[ppRow[-1]] = playerList
                            
                # Assign the players to dictionaries by position
                pitchers = {}
                catchers = {}
                firstBase = {}
                secondBase = {}
                thirdBase = {}
                shortStop = {}
                outfielders = {}

                for ids in playerDict:

                    if playerDict[ids][0] == 'P':
                        pitchers[ids] = playerDict[ids]
                    elif playerDict[ids][0] == 'C':
                        catchers[ids] = playerDict[ids]
                    elif playerDict[ids][0] == '1B':
                        firstBase[ids] = playerDict[ids]
                    elif playerDict[ids][0] == '2B':
                        secondBase[ids] = playerDict[ids]
                    elif playerDict[ids][0] == '3B':
                        thirdBase[ids] = playerDict[ids]
                    elif playerDict[ids][0] == 'SS':
                        shortStop[ids] = playerDict[ids]
                    elif playerDict[ids][0] == 'OF':
                        outfielders[ids] = playerDict[ids]
                        
                # Compute the total number of possible lineups 
                try:        
                    numLineups = "{:,d}".format(combinationsCalculator(len(pitchers),2) * len(catchers) * len(firstBase) * len(secondBase) * len(thirdBase) * len(shortStop) * combinationsCalculator(len(outfielders),3))
                    if numLineups == 0:
                        raise Http404('The csv file was read in incorrectly. Please try to submit again, and make sure you are uploading the correct csv file and selecting the correct contest.')
                except ValueError:
                    raise Http404('The csv file was read in incorrectly. Please try to submit again, and make sure you are uploading the correct csv file and selecting the correct contest.')
                
                # Run the yahoo optimizer program
                theOptimalLineup, pp = findMaxPPYahoo(playerDict,pitchers,catchers,firstBase,secondBase,thirdBase,shortStop,outfielders)
            
            
            
            # Setup optimal lineup information to be returned
            finalLineup = []
            capUsed = 0
            for player in theOptimalLineup:
                capUsed += playerDict[player][3]
                playerEntry = [playerDict[player][0], playerDict[player][1], str(round(playerDict[player][2], 2)), '${:,d}'.format(playerDict[player][3]), playerDict[player][-1]]
                finalLineup.append(playerEntry)
                
            capUsed = "${:,d}".format(capUsed)
            pp = str(round(pp, 2))
            
            # Redirect to the results page when done
            return render(
        request,
        'results.html',
        {'pp': pp, 'capUsed': capUsed, 'finalLineup': finalLineup, 'numLineups': numLineups, 'contestName': contestName}
    )
    
    else:
        form = DocumentForm() 

    # Render the upload page
    return render(
        request,
        'list.html',
        {'form': form}
    )

