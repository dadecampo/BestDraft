#This tutorial was built by me, Farzain! You can ask me questions or troll me on Twitter (@farzatv)

#First we need to import requests. Installing this is a bit tricky. I included a step by step process on how to get requests in readme.txt which is included in the file along with this program.
import requests
import time
import json

call=0

matches = {
        "matchList":[],
        "totalGames":0
    }

def foundLenght(file):
    with open(file,"r+") as fd:
        c=0
        data=json.load(fd)
        for game in data['matchList']:
            c+=1
        return c


def countApiCall():
    global matches
    print(matches)
    addToFileMatchList("matchList.json",matches)
    matches = {
        "matchList":[],
        "totalGames":0
    }
        
        
def foundWinRate(region,accountID,APIKey,data):
    winCount=0
    loseCount=0
    tot=0
    for index, row in data.iterrows():
        
        matchInfo = requestMatchInformation(region, row['matchID'], APIKey)
        countApiCall()
        for x in range(0,10):
            if(matchInfo['participantIdentities'][x]['player']['accountId']==accountID):
                playerId=x+1
                winnerBlue=matchInfo['teams'][0]['win']
                if((winnerBlue=="Win" and playerId<=5 )or( winnerBlue=="Fail" and playerId>5)):
                    print ("Win\n")
                    winCount+=1
                else:
                    print ("Lose\n")
                    loseCount+=1
                break
        tot+=1
    
    print("Winrate: "+str(float(winCount/tot)*100)[:4])
    return (float(winCount/tot)*100)

def foundChampVSChampWinrate(champion, rivalChampion, file):
    win=0
    tot=0
    with open(file,"r+") as fd:
        data=json.load(fd)
        for game in range(0,data['totalGames']):
            if (champion in data['matchList'][game]['teamWinner'] and rivalChampion in data['matchList'][game]['teamLoser']):
                win+=1
                tot+=1
            if (rivalChampion in data['matchList'][game]['teamWinner'] and champion in data['matchList'][game]['teamLoser']):
                tot+=1
    print(tot)
    if(tot==0):
        return ("Nessuna partita vs tra "+champion+" e "+rivalChampion)
    return str(float(win/tot)*100)[:4]
                

def foundChampionWinRate(region,champion,accountID,APIKey,data):
    
    winCount=0
    loseCount=0
    tot=0
    for index, row in data.iterrows():
        if(champion==row['champion']):
            matchInfo = requestMatchInformation(region, row['matchID'], APIKey)
            countApiCall()
            for x in range(0,10):
                if(matchInfo['participantIdentities'][x]['player']['accountId']==accountID):
                    playerId=x+1
                    winnerBlue=matchInfo['teams'][0]['win']
                    if((winnerBlue=="Win" and playerId<=5 )or( winnerBlue=="Fail" and playerId>5)):
                        print ("Win\n")
                        winCount+=1
                    else:
                        print ("Lose\n")
                        loseCount+=1
                    break
            tot+=1
    if (tot==0):
        print("Nessuna partita trovata con questo champ!!\n")
        return 0
    print("Winrate: "+str(float(winCount/tot)*100)[:4])
    return (float(winCount/tot)*100)


#AGGIUNGE ALLA GAMELIST UNA LISTA DI MATCHES (MATCH GIà PRESENTI NON VENGONO AGGIUNTI)
def addGameList(file,gameList):
    with open(file,"r+") as fd:
        data = json.load(fd)
        for game in gameList['matches']:
            flag=0
            for x in range(0,data['endIndex']):
                if(game['gameId'] == data['matches'][x]['gameId']):
                    flag=1
            if(flag==0):
                data['matches'].append(game)
                data['totalGames']+=1
        fd.seek(0)
        json.dump(data,fd, indent=2)


#CREA STRUTTURA TEAMSTRUCT
def createTeamsStruct(dataChampDIR,matchInfo):
    champion=[None,None,None,None,None,None,None,None,None,None]
    championName=[None,None,None,None,None,None,None,None,None,None]
    for x in range(0,10):
        try:
            champion[x] = matchInfo['participants'][x]['championId']
        except:
            champion[x] = "BadGateway"
    #APRO FILE CON TUTTE INFORMAZIONI SUI CHAMP
    with open(dataChampDIR,"r+") as f:
            data = json.load(f)
            for x in range(0,10):
                for y in data['data'].keys():
                    if(int(data['data'][y]['key'])==champion[x]):
                        championName[x]=data['data'][y]['id']
    
    if (matchInfo['teams'][0]['win']=="Win"):
        matches ={
                         "gameId": matchInfo['gameId']
                         ,
                         "teamWinner":[championName[0],
                                        championName[1],
                                        championName[2],
                                        championName[3],
                                        championName[4]]
                         ,
                          "teamLoser":[championName[5],
                                        championName[6],
                                        championName[7],
                                        championName[8],
                                        championName[9]]
                            
                }
                
    else:
        matches ={
                         "gameId": matchInfo['gameId']
                         ,
                         "teamWinner":[championName[5],
                                        championName[6],
                                        championName[7],
                                        championName[8],
                                        championName[9]]
                         ,
                          "teamLoser":[championName[0],
                                        championName[1],
                                        championName[2],
                                        championName[3],
                                        championName[4]]
                            
                }
    return matches
        
    
def addToFileMatchList(file,matchesJSON):
    c=0
    print(type(matchesJSON))
    with open(file,"r+") as fd:
        data = json.load(fd)
        for game in range(0,matchesJSON['totalGames']):
            flag=0
            
            for x in range(0,data['totalGames']):
                try:
                    outDataMatch = int(matchesJSON['matchList'][game]['gameId'])
                    inDataMatch = int(data['matchList'][x]['gameId'])
                except:
                    print("/n ---errore in addToFileMatchList()--- /n")
                    flag=1
                    break
                #print(str(game['gameId'])+" "+str(data['matchList'][x]['gameId']))
                if(outDataMatch == inDataMatch):
                    flag=1
                    break
            if(flag==0):
                data['matchList'].append(matchesJSON['matchList'][game])
                c+=1
        data['totalGames']+=c
        print("\n#######  trasferimento finito  #######\n")
        fd.seek(0)
        json.dump(data,fd, indent=2)
    

#estraggo informazioni sull'evocatore 'summonerName'
def requestSummonerData(region, summonerName, APIKey):
    #Here is how I make my URL.  There are many ways to create these.  
    URL = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #requests.get is a function given to us my our import "requests". It basically goes to the URL we made and gives us back a JSON.
    response = requests.get(URL)
    if("{'status': {'message': 'Rate limit exceeded', 'status_code': 429}}" == str(response.json())):
        countApiCall()
        time.sleep(110)
        response = requests.get(URL)
    #Here I return the JSON we just got.
    return response.json()

#estraggo informazioni sull'elo di appartenenza di summonerName(ID)
def requestRankedData(region, ID, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + ID + "?api_key=" + APIKey
    response = requests.get(URL)
    if("{'status': {'message': 'Rate limit exceeded', 'status_code': 429}}" == str(response.json())):
        countApiCall()
        time.sleep(110)
        response = requests.get(URL)
    return response.json()


#return a list of match played by the player accountID in the queueID selected (max 100 entries)
def requestMatchList(region, accountID, APIKey):
    URL = "https://"+region+".api.riotgames.com/lol/match/v4/matchlists/by-account/"+accountID+"?api_key="+APIKey
    response = requests.get(URL)
    if("{'status': {'message': 'Rate limit exceeded', 'status_code': 429}}" == str(response.json())):
        countApiCall()
        time.sleep(110)
        response = requests.get(URL)
    print (URL+"\n")
    return response.json()


#estraggo informazioni sui match trovati
def requestMatchInformation(region, matchID, APIKey):
    URL = "https://"+region+".api.riotgames.com/lol/match/v4/matches/"+str(matchID)+"?api_key="+APIKey
    response = requests.get(URL)
    if("{'status': {'message': 'Rate limit exceeded', 'status_code': 429}}" == str(response.json())):
        countApiCall()
        time.sleep(110)
        response = requests.get(URL)
    
    return response.json()
    

def main():
    global matches
    
    matches = {
        "matchList":[],
        "totalGames":0
    }
    
    #ISTANZIAMO LE VARIABILI
    APIKey = 'RGAPI-bf797ac4-53de-44f4-af58-5fddf3d2a5d3'
    x=0


    
    print("Inserisci il tuo server di gioco e successivamente il tuo nickname:\n")

    #I first ask the user for three things, their region, summoner name, and API Key.
    #These are the only three things I need from them in order to get create my URL and grab their ID.

    region = (str)(input('Type in one of the regions above: '))
    summonerName = (str)(input('Type your Summoner Name here and DO NOT INCLUDE ANY SPACES: '))
    #APIKey = (str)(input('Copy and paste your API Key here: '))

    #I send these three pieces off to my requestData function which will create the URL and give me back a JSON that has the ID for that specific summoner.
    #Once again, what requestData returns is a JSON.
    responseJSON  = requestSummonerData(region, summonerName, APIKey)
    #countApiCall()
    
    #INIZIALIZZAZIONE JSON MATCHES
    print(foundLenght("matchList.json"))

    
    print (matches)
    ID = str(responseJSON['id'])
    responseJSON2 = requestRankedData(region, ID, APIKey)
    #countApiCall()
    print (foundChampVSChampWinrate("Ornn","Taric","matchList.json"))
        
    
    
        
    if (responseJSON2[0]['queueType']=="RANKED_SOLO_5x5"):
        tier = responseJSON2[0]['tier']
        rank = responseJSON2[0]['rank']
        lp   = responseJSON2[0]['leaguePoints']
    else:
        tier = responseJSON2[1]['tier']
        rank = responseJSON2[1]['rank']
        lp   = responseJSON2[1]['leaguePoints']
    print ("\nSoloQ ELO: "+tier+" "+str(rank)+": "+str(lp)+" LP\n")



    accountID = str(responseJSON['accountId'])
    responseJSON3 = requestMatchList(region, accountID, APIKey)
    #countApiCall()
    #addGameList("data.json",responseJSON3)
    #data=pd.DataFrame();
    y=0
    
    if(str(responseJSON3) != "{'status': {'message': 'Data not found', 'status_code': 404}}" and 
        str(responseJSON3) != "{'status': {'message': 'Forbidden', 'status_code': 403}}" and
        str(responseJSON3) != "{'status': {'message': 'Gateway timeout', 'status_code': 504}}" and
        str(responseJSON3) != "{'status': {'message': 'Service unavailable', 'status_code': 503}}"): 
        for x in range(0,responseJSON3['endIndex']):
            
            #ricerco nuovo gameid
            matchID = (responseJSON3['matches'][x]['gameId'])
            extMatchInfo = requestMatchInformation(region, matchID, APIKey)
            #countApiCall()
            if(str(extMatchInfo) != "{'status': {'message': 'Data not found', 'status_code': 404}}" and 
                str(extMatchInfo) != "{'status': {'message': 'Forbidden', 'status_code': 403}}" and
                str(extMatchInfo) != "{'status': {'message': 'Gateway timeout', 'status_code': 504}}" and
                str(extMatchInfo) != "{'status': {'message': 'Service unavailable', 'status_code': 503}}"):
                for y in range(0,10):
                    playerID=extMatchInfo['participantIdentities'][y]['player']['accountId']
                    matchListPlayer = requestMatchList(region, playerID, APIKey)
                    #countApiCall()
                    #print(str(matchListPlayer) == "{'status': {'message': 'Data not found', 'status_code': 404}}")
                    if(str(matchListPlayer) != "{'status': {'message': 'Data not found', 'status_code': 404}}" and 
                        str(matchListPlayer) != "{'status': {'message': 'Forbidden', 'status_code': 403}}" and
                        str(matchListPlayer) != "{'status': {'message': 'Gateway timeout', 'status_code': 504}}" and
                        str(matchListPlayer) != "{'status': {'message': 'Service unavailable', 'status_code': 503}}"):
                        try:
                            for z in range(0,matchListPlayer['endIndex']):
                                if(matchListPlayer['matches'][z]['queue']!=450 and
                                   matchListPlayer['matches'][z]['queue']!=830):
                                    #y=y+1
                                    ID=requestMatchInformation(region, matchListPlayer['matches'][z]['gameId'], APIKey)
                                    #countApiCall()
                                    print (type(ID))
                                    if(str(ID) != "{'status': {'message': 'Data not found', 'status_code': 404}}" and 
                                       str(ID) != "{'status': {'message': 'Forbidden', 'status_code': 403}}" and
                                       str(ID) != "{'status': {'message': 'Gateway timeout', 'status_code': 504}}" and
                                       str(ID) != "{'status': {'message': 'Service unavailable', 'status_code': 503}}"):
                                        
                                        matches['matchList'].append(createTeamsStruct("champion.json",ID))
                                        matches['totalGames']+=1
                                        #in questo game accountId ha usato 'champion' come proprio campione
                                        #champion = int(matchListPlayer['matches'][x]['champion'])
                                        #creo e aggiungo il nuovo risultato a data
                                        #nuovoGame=pd.Series(data={'matchID':str(matchID),'champion':champion},name=y)
                                        #data=data.append(nuovoGame,ignore_index=False)
                                    else:
                                        print("\n---- errore analisi MatchInformation ----\n")
                        except:
                            print(matchListPlayer)
                
        
        
        
        
    #print(data[["matchID","champion"]])
    """
    #CALCOLO WINRATE
    foundWinRate(region, accountID, APIKey, data)
    countApiCall()
    foundChampionWinRate(region, 114, accountID, APIKey, data)
    countApiCall()
    """
    
#This starts my program!
if __name__ == "__main__":
    main()

