import csv, itertools, copy, time, datetime, os, re, math, shutil
from collections import Counter
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from django.http import Http404
import errno

teamNames = {
'LAA' : 'Angels',
'HOU' : 'Astros',
'OAK' : 'Athletics',
'TOR' : 'Blue Jays',
'ATL' : 'Braves',
'MIL' : 'Brewers',
'STL' : 'Cardinals',
'CHC' : 'Cubs',
'ARI' : 'Diamondbacks',
'LOS' : 'Dodgers',
'SFG' : 'Giants',
'CLE' : 'Indians',
'SEA' : 'Mariners',
'MIA' : 'Marlins',
'NYM' : 'Mets',
'WAS' : 'Nationals',
'BAL' : 'Orioles',
'SDP' : 'Padres',
'PHI' : 'Phillies',
'PIT' : 'Pirates',
'TEX' : 'Rangers',
'TAM' : 'Rays',
'BOS' : 'Red Sox',
'CIN' : 'Reds',
'COL' : 'Rockies',
'KAN' : 'Royals',
'DET' : 'Tigers',
'MIN' : 'Twins',
'CWS' : 'White Sox',
'NYY' : 'Yankees'
}

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
    return dataList
    
# Reads fanduels csv data into a list and then deletes the csv     
def getFanDuel(absFolderPath):
    for folder in os.listdir(absFolderPath):
        if folder != '.DS_Store':
            newFolder = folder
            newFolderPath = absFolderPath + '/' + newFolder
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

# Matches up players from fanduels with players from fangraphs
def editPlayerName(elementName, rowIndex):
    fullName = elementName[rowIndex].lower().replace(".", "").replace(" jr", "").split(' ', 1)
    firstName = fullName[0]
    if len(firstName) > 2:
        firstName = firstName[:3]
    lastName = fullName[1]
    name = firstName + " " + lastName
    removeInitial = re.compile(r' \w ').search(name)
    if removeInitial:
        name = name.replace(removeInitial.group(), ' ')
    return name

# Calculates how many different ways you can choose 3 items from n item set (used to figure out how many combinations of outfielders are possible)
def combinationsCalculator(n):
    groupings = 3
    combos = int(math.factorial(n)/(math.factorial(groupings)*math.factorial(n-groupings)))
    return combos

"""Function to find the optimal lineup. Finds the lineup with the highest projected points total that satisfies the three constraints of...

 1. One player at each of the following positions pitcher, catcher, first base, second base, third base, shortstop, and three outfielders
 2. Total lineup salary less than or equal to $35,000
 3. Can not have more than four players from the same MLB team in a chosen lineup
 
 Function is recursive so that if the optimal lineup violates the max players from the same team constraint it runs again without using
 players from whatever team(s) caused it to violate that constraint as the basis to eliminate other players from consideration. 
"""
def findMaxPP(playerDict, pitchers, catchers, firstBase, secondBase, thirdBase, shortStop, outfielders, teams=set(), lineupsViolateConstraint=set(), maxPlayer = 4):

    # Eliminate all but the player with the highest projected points value for each salary, by position
    def positionFilter(positionDict):
        positionDictCopy = copy.deepcopy(positionDict)
        for player in positionDict:
            for player2 in positionDict:
                if positionDict[player][3] == positionDict[player2][3] and positionDict[player][2] < \
                        positionDict[player2][2] and positionDict[player2][-1] not in teams:
                    if player in positionDictCopy:
                        del positionDictCopy[player]
        return positionDictCopy

    # Eliminate all players who have a higher salary and a lesser or equal projected points value of another player, by position
    def filterMoreExpensiveLessPP(positionDict):
        positionDictCopy = copy.deepcopy(positionDict)
        for player in positionDict:
            for player2 in positionDict:
                if positionDict[player][3] > positionDict[player2][3] and positionDict[player][2] <= \
                        positionDict[player2][2] and positionDict[player2][-1] not in teams:
                    if player in positionDictCopy:
                        del positionDictCopy[player]
        return positionDictCopy

    # If more than three outfielders share the same salary, eliminate all but the three with the highest projected points value
    def ofPositionFilter(positionDict):
        positionDictCopy = copy.deepcopy(positionDict)
        outfielderSalaries = []
        for of in positionDict: 
            outfielderSalaries.append(positionDict[of][3])
            
        ofSalaryCounts = Counter(outfielderSalaries)

        outfielderSalariesToFilter = {k: v for k, v in ofSalaryCounts.items() if v > 3}
      
        for salary in outfielderSalariesToFilter:
            onTeams = 0
            playersWithSameSalary = []
            for of in positionDict:
                if positionDict[of][3] == salary:
                    playersWithSameSalary.append(positionDict[of][2])
                    if positionDict[of][-1] in teams:
                        onTeams += 1
			
            for num in range(outfielderSalariesToFilter[salary] - 3 - onTeams):
                lowestPP = min(playersWithSameSalary)
                for of in positionDict:
                    if positionDict[of][2] == lowestPP and positionDict[of][3] == salary:
                        if of in positionDictCopy:
                            del positionDictCopy[of]
                            playersWithSameSalary.remove(lowestPP)
        return positionDictCopy

    # If there are at least three outfielders below another outfielder who each have a higher projected points value and a lower or equal salary, eliminate that outfielder
    def ofFilterMoreExpensiveLessPP(positionDict):
        outfielderList = []
        for key in positionDict:
            playerEntry = [key]
            for info in positionDict[key]:
                playerEntry.append(info)
            outfielderList.append(playerEntry)
            
        outfielderListSalaryOrder = sorted(outfielderList, key=lambda x: (x[4], x[3] * -1))
       
        count = 0
        i = 0
        lowestSalaryOutfielders = []
        while count < 3:
            if outfielderListSalaryOrder[i][-1] not in teams:
                lowestSalaryOutfielders.append(outfielderListSalaryOrder[i])
                i += 1
                count += 1
            else:
                i += 1

        count2 = 1
        while count2 + 1 < len(outfielderListSalaryOrder):

            minPPOFer = min(lowestSalaryOutfielders, key=lambda x: x[3])

            outfieldersToDelete = []
            for of in outfielderListSalaryOrder[2 + count2:]:
                if of[3] < minPPOFer[3] and of[4] >= minPPOFer[4]:
                    outfieldersToDelete.append(of)

            outfielderListSalaryOrder = [x for x in outfielderListSalaryOrder if x not in outfieldersToDelete]

            try:
                if outfielderListSalaryOrder[2 + count2][-1] not in teams:
                    lowestSalaryOutfielders.remove(minPPOFer)
                    lowestSalaryOutfielders.append(outfielderListSalaryOrder[2 + count2])
                else:
                    pass
            except IndexError:
                break

            count2 += 1
        outfielders = [item[0] for item in outfielderListSalaryOrder]
        return outfielders

    # Pair players from one position up with players from another position and eliminate them in the same way as before
    def groupFilter(group):
        # If one pair has a higher combined salary and a lower or equal combined projected points value than another pair, eliminate that pair    
        toDelete = set()
        for x, y in group:
            for x2, y2 in group:
                if playerDict[x][3] + playerDict[y][3] > playerDict[x2][3] + playerDict[y2][3] and playerDict[x][2] + \
                        playerDict[y][2] <= playerDict[x2][2] + \
                        playerDict[y2][2] and playerDict[x2][-1] not in teams and playerDict[y2][-1] not in teams:
                    pair = (x, y)
                    toDelete.add(pair)

        group = group.difference(toDelete)
        # If one pair has the same combined salary as another pair but a lower combined projected points value, eliminate that pair
        toDelete = set()
        for a, b in group:
            for a2, b2 in group:
                if playerDict[a][3] + playerDict[b][3] == playerDict[a2][3] + playerDict[b2][3] and playerDict[a][2] + \
                        playerDict[b][2] < playerDict[a2][2] + \
                        playerDict[b2][2] and playerDict[a2][-1] not in teams and playerDict[b2][-1] not in teams:
                    pair = (a, b)
                    toDelete.add(pair)

        group = group.difference(toDelete)
        return group

    # Combine outfielders in groups of three and eliminate them in the same way as before
    def oufielderGroupFilter(group):
        # If a group of outfielders has a higher combined salary and a lower or equal combined projected points value than another group, eliminate that group
        toDelete = set()
        for x, y, z in group:
            for x2, y2, z2 in group:
                if playerDict[x][3] + playerDict[y][3] + playerDict[z][3] > playerDict[x2][3] + playerDict[y2][3] + playerDict[z2][3] and \
                    playerDict[x][2] + playerDict[y][2] + playerDict[z][2] <= playerDict[x2][2] + playerDict[y2][2] + playerDict[z2][2] and \
                    playerDict[x2][-1] not in teams and playerDict[y2][-1] not in teams and playerDict[z2][-1] not in teams:
                    
                    team = (x, y, z)
                    toDelete.add(team)
        group = group.difference(toDelete)
        # If a group of outfielders has the same combined salary as another group but a lower combined projected points value, eliminate that group
        toDelete = set()
        for x, y, z in group:
            for x2, y2, z2 in group:
                if playerDict[x][3] + playerDict[y][3] + playerDict[z][3] == playerDict[x2][3] + playerDict[y2][3] + playerDict[z2][3] and \
                    playerDict[x][2] + playerDict[y][2] + playerDict[z][2] < playerDict[x2][2] + playerDict[y2][2] + playerDict[z2][2] and \
                    playerDict[x2][-1] not in teams and playerDict[y2][-1] not in teams and playerDict[z2][-1] not in teams:

                    team = (x, y, z)
                    toDelete.add(team)
        outfielderGroups = group.difference(toDelete)
        return outfielderGroups
    
    
    pitchers2 = filterMoreExpensiveLessPP(positionFilter(pitchers))
    catchers2 = filterMoreExpensiveLessPP(positionFilter(catchers))
    firstBase2 = filterMoreExpensiveLessPP(positionFilter(firstBase))
    secondBase2 = filterMoreExpensiveLessPP(positionFilter(secondBase))
    thirdBase2 = filterMoreExpensiveLessPP(positionFilter(thirdBase))
    shortStop2 = filterMoreExpensiveLessPP(positionFilter(shortStop))
    outfielders2 = ofFilterMoreExpensiveLessPP(ofPositionFilter(outfielders))
    
    pitchersCatchers = set(itertools.product(pitchers2, catchers2))
    firstSecond = set(itertools.product(firstBase2, secondBase2))
    thirdShort = set(itertools.product(thirdBase2, shortStop2))
    outfielderGroups = set(itertools.combinations(outfielders2, 3))
    outfielderGroups = oufielderGroupFilter(outfielderGroups)
    allLineups = list(itertools.product(pitchersCatchers, firstSecond, thirdShort, outfielderGroups))
    
    # Eliminate all lineups which violate the max salary cap constraint
    underCap = set()
  
    for pc, fs, ts, of in allLineups:
        salary = 0
        salary += playerDict[pc[0]][3] + playerDict[pc[1]][3] + playerDict[fs[0]][3] + playerDict[fs[1]][3] + \
                  playerDict[ts[0]][3] + playerDict[ts[1]][3] + \
                  playerDict[of[0]][3] + playerDict[of[1]][3] + playerDict[of[2]][3]

        squad = (pc, fs, ts, of)
        if salary <= 35000:
            underCap.add(squad)
    underCap = underCap.difference(lineupsViolateConstraint)
    
    # Calculate the projected points for all remaining lineups
    underCapPP = {}
    for pc, fs, ts, of in underCap:
        projectedPoints = 0
        projectedPoints += playerDict[pc[0]][2] + playerDict[pc[1]][2] + playerDict[fs[0]][2] + playerDict[fs[1]][2] + \
                            playerDict[ts[0]][2] + \
                            playerDict[ts[1]][2] + playerDict[of[0]][2] + playerDict[of[1]][2] + playerDict[of[2]][2]

        team = (pc, fs, ts, of)
        underCapPP[projectedPoints] = team
    
    # Find the lineup with the highest projected points total 
    pp = max(underCapPP)
    
    count = 0
    while True:
        # If this loop has run without being reset then delete the previous optimal lineup for violating the max players from the same team constraint, and find the lineup with the next highest projected points total, since the team(s) responsible for this lineup violating the max player constraint had already been added to the set not to use to eliminate
        if count > 0:
            lineupToDelete = underCapPP[pp]
            lineupsViolateConstraint.add(lineupToDelete)
            del underCapPP[pp]
            pp = max(underCapPP)
        teamsCounter = []
        optimalLineup = underCapPP[pp]
        # Find the team(s) with the highest number of players in the optimal lineup
        for group in optimalLineup:
            for player in group:
                teamsCounter.append(playerDict[player][-1])
                
        teamsCounter = Counter(teamsCounter)
        maxTeamFreq = max(teamsCounter.values())
        # If the optimal lineup violates the max players from the same team constraint, add team(s) to a list to reference
        teamPlayersCantElim = []
        for teamName in teamsCounter:
            if teamsCounter[teamName] == maxTeamFreq:
                if teamName not in teamPlayersCantElim: teamPlayersCantElim.append(teamName)
        # If the optimal lineup violates the max players from the same team constraint, but team(s) had already been added to the set of teams not to eliminate from, revert to the top of this loop
        if maxTeamFreq > maxPlayer and all(x in teams for x in teamPlayersCantElim):
            count += 1
            continue
        # If the optimal lineup had more than 4 players from the same team, and that team wasn't already added to the set of teams not to eliminate from, rerun this function without using any players from that team as a basis to eliminate another player
        elif max(teamsCounter.values()) > maxPlayer:
            [teams.add(x) for x in teamPlayersCantElim]
            lineupToDelete = underCapPP[pp]
            lineupsViolateConstraint.add(lineupToDelete)
            return findMaxPP(playerDict, pitchers, catchers, firstBase, secondBase, thirdBase, shortStop, outfielders, teams, lineupsViolateConstraint)
        # All constraints have been satisfied, return the optimal lineup
        else:
            return underCapPP[pp], pp



