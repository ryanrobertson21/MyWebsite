import re
import copy
import itertools
from collections import Counter

"""
Constraints:
1) 1 Pitcher, 1 Catcher, 1 FirstBaseman, 1 Secondbaseman, 1 Thirdbaseman, 1 Shortstop, 3 Outfielders
2) Total lineup salary cannot exceed $35,000
3) Can not have more than 4 players from the same MLB team in lineup
"""

teamDictFanDuel = {
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


# Removes inconsistencies between players names in contest and fangraphs
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

"""
   Function to find the optimal lineup. Finds the lineup with the highest projected points total that 
   satisfies the constraints. Function is recursive so that if the optimal lineup violates the max players
   from the same team constraint it runs again without using players from whichever team(s) caused it to
   violate that constraint as the basis to eliminate other players from consideration. 
"""
def findMaxPPFanDuel(playerDict, pitchers, catchers, firstBase, secondBase, thirdBase, shortStop, outfielders, teams=set(),
         lineupsViolateConstraint=set(), maxPlayer = 4):

    # Eliminate all but the player with the highest projected points value for each salary, by position
    def positionFilter(positionDict):
        positionDictCopy = copy.deepcopy(positionDict)
        for player in positionDict:
            for player2 in positionDict:
                if positionDict[player][3] == positionDict[player2][3] and positionDict[player][2] < positionDict[player2][2] and \
                   positionDict[player2][-1] not in teams and player in positionDictCopy:
                    del positionDictCopy[player]
        return positionDictCopy

    # Eliminate all players who have a higher salary and a lesser or equal projected points value of another player, by position
    def filterMoreExpensiveLessPP(positionDict):
        positionDictCopy = copy.deepcopy(positionDict)
        for player in positionDict:
            for player2 in positionDict:
                if positionDict[player][3] > positionDict[player2][3] and positionDict[player][2] <= \
                   positionDict[player2][2] and positionDict[player2][-1] not in teams and player in positionDictCopy:
                    del positionDictCopy[player]
        return positionDictCopy

    # If more than three outfielders share the same salary, eliminate all but the three with the highest projected points value
    def ofPositionFilter(positionDict):
        positionDictCopy = copy.deepcopy(positionDict)
        outfielderSalaries = [positionDict[of][3] for of in positionDict]  
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
                    if positionDict[of][2] == lowestPP and positionDict[of][3] == salary and of in positionDictCopy:
                        del positionDictCopy[of]
                        playersWithSameSalary.remove(lowestPP)
                        break
        return positionDictCopy

    # If there are at least three outfielders who have a salary equal to or lower than another outfielder, and a higher projected
    # points value, eliminate that outfielder
    def ofFilterMoreExpensiveLessPP(positionDict):
        outfielderList = []
        for key in positionDict:
            playerEntry = [key]
            [playerEntry.append(info) for info in positionDict[key]]
            outfielderList.append(playerEntry)
            
        outfielderListSalaryOrder = sorted(outfielderList, key=lambda x: (x[4], x[3] * -1))
       
        count = 0
        index = 0
        lowestSalaryOutfielders = []
        while count < 3:
            if outfielderListSalaryOrder[index][-1] not in teams:
                lowestSalaryOutfielders.append(outfielderListSalaryOrder[index])
                count += 1
            index += 1

        count = 1
        while count + 1 < len(outfielderListSalaryOrder):
            minPPOFer = min(lowestSalaryOutfielders, key=lambda x: x[3])

            outfieldersToDelete = []
            for of in outfielderListSalaryOrder[2 + count:]:
                if of[3] < minPPOFer[3] and of[4] >= minPPOFer[4]:
                    outfieldersToDelete.append(of)

            outfielderListSalaryOrder = [x for x in outfielderListSalaryOrder if x not in outfieldersToDelete]

            try:
                if outfielderListSalaryOrder[2 + count][-1] not in teams:
                    lowestSalaryOutfielders.remove(minPPOFer)
                    lowestSalaryOutfielders.append(outfielderListSalaryOrder[2 + count])
                else:
                    pass
            except IndexError:
                break

            count += 1
        outfielders = [item[0] for item in outfielderListSalaryOrder]
        return outfielders

    # Eliminate pairs of players in the same way as before
    def groupFilter(group):
    
        # If one pair has a higher combined salary and a lower or equal combined projected points value than another pair, eliminate that pair    
        toDelete = set()
        for x, y in group:
            for x2, y2 in group:
                if playerDict[x][3] + playerDict[y][3] > playerDict[x2][3] + playerDict[y2][3] and playerDict[x][2] + \
                        playerDict[y][2] <= playerDict[x2][2] + \
                        playerDict[y2][2] and playerDict[x2][-1] not in teams and playerDict[y2][-1] not in teams:
                    toDelete.add((x, y))

        group.difference_update(toDelete)
        
        # If one pair has the same combined salary as another pair but a lower combined projected points value, eliminate that pair
        toDelete = set()
        for a, b in group:
            for a2, b2 in group:
                if playerDict[a][3] + playerDict[b][3] == playerDict[a2][3] + playerDict[b2][3] and playerDict[a][2] + \
                        playerDict[b][2] < playerDict[a2][2] + \
                        playerDict[b2][2] and playerDict[a2][-1] not in teams and playerDict[b2][-1] not in teams:
                    toDelete.add((a, b))

        group.difference_update(toDelete)
        return group

    # Eliminate groups of outfielders in the same way as before
    def oufielderGroupFilter(group):

        # find the total salary and total projected points for each group of outfielders
        newGroup = set()
        for x, y, z in group:
            salaryOF = playerDict[x][3] + playerDict[y][3] + playerDict[z][3]
            projectedPointsOF = playerDict[x][2] + playerDict[y][2] + playerDict[z][2]
            newGroup.add((x, y, z, projectedPointsOF, salaryOF))

        # If a group of outfielders has a higher total salary and a lower or equal total projected points value than another group, eliminate that group
        toDelete = set()
        for x, y, z, pp, sal in newGroup:
            for x2, y2, z2, pp2, sal2 in newGroup:
                if sal > sal2 and pp <= pp2 and playerDict[x2][-1] not in teams and playerDict[y2][-1] not in teams and playerDict[z2][-1] not in teams:
                    toDelete.add((x, y, z))
        group.difference_update(toDelete)

        # If a group of outfielders has the same total salary as another group but a lower total projected points value, eliminate that group
        toDelete = set()
        for x, y, z, pp, sal in newGroup:
            for x2, y2, z2, pp2, sal2, in newGroup:
                if sal == sal2 and pp < pp2 and playerDict[x2][-1] not in teams and playerDict[y2][-1] not in teams and playerDict[z2][-1] not in teams:
                    toDelete.add((x, y, z))
        group.difference_update(toDelete)

        return group
    
    # Filter out players that would never be selected for the optimal lineup
    pitchers2 = filterMoreExpensiveLessPP(positionFilter(pitchers))
    catchers2 = filterMoreExpensiveLessPP(positionFilter(catchers))
    firstBase2 = filterMoreExpensiveLessPP(positionFilter(firstBase))
    secondBase2 = filterMoreExpensiveLessPP(positionFilter(secondBase))
    thirdBase2 = filterMoreExpensiveLessPP(positionFilter(thirdBase))
    shortStop2 = filterMoreExpensiveLessPP(positionFilter(shortStop))
    outfielders2 = ofFilterMoreExpensiveLessPP(ofPositionFilter(outfielders))
    
    # Filter out groups of players that would never be selected for the optimal lineup
    pitchersCatchers = groupFilter(set(itertools.product(pitchers2, catchers2)))
    firstSecond = groupFilter(set(itertools.product(firstBase2, secondBase2)))
    thirdShort = groupFilter(set(itertools.product(thirdBase2, shortStop2)))
    outfielderGroups = oufielderGroupFilter(set(itertools.combinations(outfielders2, 3)))
    
    # Create every possible lineup from the remaining players
    allLineups = list(itertools.product(pitchersCatchers, firstSecond, thirdShort, outfielderGroups))
    
    # Eliminate all lineups which violate the max salary cap constraint
    underCap = set([(pc, fs, ts, of) for pc, fs, ts, of in allLineups if
                    playerDict[pc[0]][3] + playerDict[pc[1]][3] + playerDict[fs[0]][3] + playerDict[fs[1]][3] + \
                    playerDict[ts[0]][3] + playerDict[ts[1]][3] + \
                    playerDict[of[0]][3] + playerDict[of[1]][3] + playerDict[of[2]][3] <= 35000])

    # If any lineups have previously violated the max player from the same team constraint, eliminate them
    underCap.difference_update(lineupsViolateConstraint)

    # Calculate the projected points for all remaining lineups
    underCapPP = {playerDict[pc[0]][2] + playerDict[pc[1]][2] + playerDict[fs[0]][2] + playerDict[fs[1]][2] + playerDict[ts[0]][2] + \
                  playerDict[ts[1]][2] + playerDict[of[0]][2] + playerDict[of[1]][2] + \
                  playerDict[of[2]][2]: (pc, fs, ts, of) for pc, fs, ts, of in underCap}
    
    # Find the lineup with the highest projected points total 
    pp = max(underCapPP)
    
    count = 0
    while True:
        # If this loop has run without being reset then delete the previous optimal lineup for violating the max players from 
        # the same team constraint, and find the lineup with the next highest projected points total, since the team(s)
        # responsible for this lineup violating the max player constraint had already been added to the set not to use to eliminate
        if count > 0:
            lineupToDelete = underCapPP[pp]
            lineupsViolateConstraint.add(lineupToDelete)
            del underCapPP[pp]
            pp = max(underCapPP)    
        
        optimalLineup = underCapPP[pp]
        teamsCounter = []
        
        # Find out the number of players each team has in the optimal lineup
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
                
        # If the optimal lineup violates the max players from the same team constraint, but team(s) had already been added to the set
        # of teams not to eliminate from, revert to the top of this loop
        if maxTeamFreq > maxPlayer and all(x in teams for x in teamPlayersCantElim):
            count += 1
            continue
        
        # If the optimal lineup had more than 4 players from the same team, and that team wasn't already added to the set of teams not 
        # to eliminate from, rerun this function without using any players from that team as a basis to eliminate another player
        elif maxTeamFreq > maxPlayer:
            [teams.add(x) for x in teamPlayersCantElim]
            lineupToDelete = underCapPP[pp]
            lineupsViolateConstraint.add(lineupToDelete)
            return findMaxPPFanDuel(playerDict, pitchers, catchers, firstBase, secondBase, thirdBase, shortStop, outfielders, 
                             teams, lineupsViolateConstraint)
        
        # All constraints have been satisfied, return the optimal lineup and its projected points total
        else:
            optimalLineup = optimalLineup[0] + optimalLineup[1] + optimalLineup[2] + tuple(sorted(optimalLineup[3], key=lambda x: (playerDict[x][3] * -1, x[2] * -1)))
            return optimalLineup, pp



