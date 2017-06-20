from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from baseballproject.models import Document
from baseballproject.forms import DocumentForm
from baseballOptimizer import teamNames, editPlayerName, combinationsCalculator, getFanDuel, findMaxPP, grabData, getcsvData
import time
     

def list(request):
    # Handle csv file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
            
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
            
            # Read in fanduel data and convert into a list
            contestLineup = getFanDuel('/home/django/django_project/media/documents') 

            # Match up the players from fanduel with their projected points from fangraphs
            playerDict = {}
            for row in contestLineup:
                for ppRow in battersPP:
                    fdName = editPlayerName(row, 3)
                    ppName = editPlayerName(ppRow, 0)
                    
                    if fdName == ppName and row[1] != 'P' and (teamNames[row[9]] == ppRow[1] or ppRow[1] == ''):
                        playerList = [row[1], row[3], float(ppRow[-3]), int(row[7]), row[9]]
                        playerDict[row[0]] = playerList
                        
            for row in contestLineup:
                for ppRow in pitchersPP:
                    fdName = editPlayerName(row, 3)
                    ppName = editPlayerName(ppRow, 0)
                    
                    if fdName == ppName and row[1] == 'P' and (teamNames[row[9]] == ppRow[1] or ppRow[1] == ''):
                        playerList = [row[1], row[3], float(ppRow[-3]), int(row[7]), row[9]]
                        playerDict[row[0]] = playerList
            
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
            numLineups = "{:,d}".format(len(pitchers) * len(catchers) * len(firstBase) * len(secondBase) * len(thirdBase) * len(shortStop) * combinationsCalculator(len(outfielders)))
            
            # Run the optimizer program
            optimalLineup, pp = findMaxPP(playerDict,pitchers,catchers,firstBase,secondBase,thirdBase,shortStop,outfielders)
            
            # Setup optimal lineup information to be returned
            finalLineup = []
            capUsed = 0
            for group in optimalLineup:
                for player in group:
                    capUsed += playerDict[player][3]
                if len(group) == 3:
                    outfield = sorted(group, key=lambda x: (playerDict[x][3] * -1, x[2] * -1))
                    for of in outfield:
                        playerEntry = [playerDict[of][0], playerDict[of][1], str(round(playerDict[of][2], 2)), '${:,d}'.format(playerDict[of][3]), playerDict[of][-1]]
                        finalLineup.append(playerEntry) 
                else:
                    for player in group:
                        playerEntry = [playerDict[player][0], playerDict[player][1], str(round(playerDict[player][2], 2)), '${:,d}'.format(playerDict[player][3]), playerDict[player][-1]]
                        finalLineup.append(playerEntry)
            capUsed = "${:,d}".format(capUsed)
            pp = str(round(pp, 2))
            
            # Redirect to the results page when done
            return render(
        request,
        'results.html',
        {'pp': pp, 'capUsed': capUsed, 'finalLineup': finalLineup, 'numLineups': numLineups}
    )
    
    else:
        form = DocumentForm() 

    # Render the upload page
    return render(
        request,
        'list.html',
        {'form': form}
    )

