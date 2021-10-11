import discord, math
from discord.client import Client
from discord.embeds import Embed
from discord.ext import commands, tasks
from riotwatcher import LolWatcher, TftWatcher
import os
from dotenv import load_dotenv

lol_watcher = LolWatcher('Paste API Key Here') #For production, this should be hidden in an env file.
tft_watcher = TftWatcher('Paste API Key Here') #For production, this should be hidden in an env file.

load_dotenv()

# Store token in env file. PUT ENV FILE IN .gitignore.
token = os.getenv("TOKEN")

# Select region for users. Code can be altered to ask for user input for a region.
# Note that region must also be changed within the rankedLolUpdate and rankedTftUpdate functions/commands.
# Future versions of the bot may include the ability to change regions.
my_region = 'na1'

bot = commands.Bot(command_prefix = '#') 
# Change prefix to whatever is preferred

# Background task variables to check for new ranked matches
summonerListLol = []
summonerEmptyLol = True
summonerListTft = []
summonerEmptyTft = True

#Bot start
@bot.event
async def on_ready():
    rankedLolUpdate.start()
    rankedTftUpdate.start()


@bot.command()
async def helpStats(ctx):
    embed = discord.Embed(
        title = "Help!",
        description = 'List of commands for LolStats\nIMPORTANT: ALL COMMANDS ARE CaSe SeNsItIvE!'
    )
    embed.set_footer(text = 'Created by minkim#8625')
    embed.add_field(name="#helpStats", value="Prints out this text box for list of commands.")
    embed.add_field(name="#lolstats (username)", value="Display solo rank data for League of Legends")
    embed.add_field(name="#tftstats (username)", value="Display rank data for Teamfight Tactics")
    embed.add_field(name="#lolhistory (username)", value="Display recent match history for League of Legends")
    embed.add_field(name="#tfthistory (username)", value="Display recent match history for Teamfight Tactics")
    embed.add_field(name="#requestLolUpdate (username) ", value="Request for user's League of Legends ranked data to be automatically updated")
    embed.add_field(name="#requestTftUpdate (username) ", value="Request for user's Teamfight Tactics ranked data to be automatically updated")
    await ctx.send(embed=embed)

# Ranked Auto-Updater for League of Legends
@tasks.loop(minutes = 1)
async def rankedLolUpdate():
    print(summonerListLol)
    if summonerEmptyLol:
        print('No requested summoners')
        return
    for summonerLol in summonerListLol:
        summonerDataLol = lol_watcher.summoner.by_name(my_region, summonerLol['name'])
        checkRecentLol = lol_watcher.match_v5.matchlist_by_puuid('AMERICAS', summonerDataLol['puuid'], None, 1)
        matchDataLol = lol_watcher.match_v5.by_id('AMERICAS', checkRecentLol[0])
        print(summonerLol)
        if matchDataLol['info']['queueId'] != 420:
            print("Latest match is not ranked")
            if summonerListLol.index(summonerLol) == (len(summonerListLol) - 1):
                return
            continue
        if summonerLol["gameExist"] == False:
            summonerLol["gameExist"] = True
            summonerLol["latestGame"] = checkRecentLol[0]
            print("Latest game is ranked and is kept in memory")
        else:
            if summonerLol["latestGame"] == checkRecentLol[0]:
                print("No new matches")
                if summonerListLol.index(summonerLol) == (len(summonerListLol) - 1):
                    return
                continue
            else:
                print("Found new ranked match to replace old match")
                summonerLol["latestGame"] = checkRecentLol[0]
        
        # Check users position and which side team
        participantList = matchDataLol['info']['participants']
        participantCount = 0
        totalKills = 0
        totalAssists = 0
        totalDeaths = 0
        totalDamage = 0
        position = None
        for participants in participantList:
            if participants['puuid'] == summonerDataLol['puuid']:
                position = participantCount
            participantCount += 1
        # Collect team data based on which side the user was in
        if position < 5: 
            for i in range(0, 5):
                totalDamage += participantList[i]['totalDamageDealtToChampions']
                totalKills += participantList[i]['kills']
                totalAssists += participantList[i]['assists']
                totalDeaths += participantList[i]['deaths']
        else:
            for i in range(5, 10):
                totalDamage += participantList[i]['totalDamageDealtToChampions']
                totalKills += participantList[i]['kills']
                totalAssists += participantList[i]['assists']
                totalDeaths += participantList[i]['deaths']
        # Collect data
        myData = matchDataLol['info']['participants'][position]
        champion = myData['championName']
        kills = myData['kills']
        deaths = myData['deaths']
        assists = myData['assists']
        damage = myData['totalDamageDealtToChampions']
        doubleKill = myData['doubleKills']
        tripleKill = myData['tripleKills']
        quadraKill = myData['quadraKills']
        pentaKill = myData['pentaKills']
        visionScore = myData['visionScore']
        if deaths != 0:
            kda = round(((kills + assists)/deaths), 2)
        else:
            kda = 'Perfect Score'
        myPosition = myData['teamPosition'].title()
        if myPosition == 'Utility':
            myPosition = 'Support'
        myTeam = myData['teamId']
        timePlayed = myData['timePlayed']
        minutes = int(timePlayed/60)
        seconds = (timePlayed - int(timePlayed/60) * 60)
        if seconds < 10:
            seconds = f"0{seconds}"
        # Assign side to user and check result of match
        if myTeam == 100:
            teamColor = 'Blue'
            result = matchDataLol['info']['teams'][0]['win']
        else:
            teamColor = 'Red'
            result = matchDataLol['info']['teams'][1]['win']
        if result == True:
            result = 'Victory'
        else:
            result = 'Defeat'
        #Gather new ranked stats
        lol_stats = lol_watcher.league.by_summoner(my_region, summonerDataLol['id'])
        queue = 0
        for queues in lol_stats:
            if queues['queueType'] == 'RANKED_SOLO_5x5':
                break
            queue += 1
        if lol_stats[queue]:
            ranked_data = lol_stats[queue]
            tier = ranked_data['tier'].title()
            rank = ranked_data['rank']
            lp = ranked_data['leaguePoints']
        #Display information in an embed
        embed = discord.Embed(
            title = f"{summonerLol['name']}'s League of Legends Ranked Result: {result}",
            description = f'Game Time: {minutes}:{seconds}'
        )
        embed.set_footer(text = 'Created by minkim#8625')
        if result == 'Victory':
            embed.color= discord.Colour.blue()
        else:
            embed.color = discord.Colour.red()
        embed.add_field(name="Team Side", value=f"{teamColor} Side", inline=True)
        embed.add_field(name="Position", value=f"{myPosition}", inline=True)
        embed.add_field(name = chr(173), value = chr(173))
        embed.add_field(name="Champion", value=f"{champion}", inline=True)
        embed.add_field(name="K/D/A", value=f"{kills}/{deaths}/{assists} ({kda})", inline=True)
        embed.add_field(name="Kill Participation", value=f"{round((kills + assists)/totalKills * 100)}%", inline=True)
        embed.add_field(name="Total Damage Dealt to Champions", value=f"{damage}", inline=True)
        embed.add_field(name="Damage Percentage", value=f"{round(damage/totalDamage * 100)}%", inline=True)
        embed.add_field(name="Vision Score", value=f"{visionScore}", inline=True)
        embed.add_field(name="Multi Kills", value=f"Double Kills: {doubleKill}\nTriple Kills: {tripleKill}\nQuadra Kills: {quadraKill}\nPenta Kills: {pentaKill}", inline=True)
        if lol_stats[queue]:
            embed.add_field(name = chr(173), value = chr(173))
            embed.add_field(name = chr(173), value = chr(173))
            embed.add_field(name="Rank", value=f"{tier} {rank}", inline=True)
            embed.add_field(name="LP", value=f"{lp}", inline=True)
        channel = bot.get_channel() #Input channel ID as parameter of function.
        await channel.send(embed=embed)

# Append usernames to auto-update rank history for League of Legends
@bot.command()
async def requestLolUpdate(ctx, *, arg):
    try: 
        if summonerListLol:
            for summonersInLol in summonerListLol:
                if summonersInLol['name'] == arg:
                    summonerListLol.remove(summonersInLol)
                    await ctx.send(f'League of Legends ranked auto-update has been turned off for {arg}!')
                    return
        global summonerEmptyLol
        summonerEmptyLol = False
        me = lol_watcher.summoner.by_name(my_region, arg) # If the username is not valid, error is returned via except
        dict = {
            "name": arg,
            "gameExist": False,
            "latestGame": "" 
        }
        summonerListLol.append(dict)
        await ctx.send(f'Added {arg} to League of Legends Ranked Updater!')
    except:
        await ctx.send('Error: User not found')

# Ranked Auto-Updater for Teamfight Tactics
@tasks.loop(minutes=1)
async def rankedTftUpdate():
    if summonerEmptyTft:
        print('No requested summoners')
        return
    for summonerTft in summonerListTft:
        summonerDataTft = tft_watcher.summoner.by_name(my_region, summonerTft['name'])
        checkRecentTft = tft_watcher.match.by_puuid('AMERICAS', summonerDataTft['puuid'], 1)
        matchDataTft = tft_watcher.match.by_id('AMERICAS', checkRecentTft[0])
        print(summonerTft)
        if matchDataTft['info']['queue_id'] != 1100:
            print("Latest match is not ranked")
            if summonerListTft.index(summonerTft) == (len(summonerListLol) - 1):
                return
            continue
        if summonerTft["gameExist"] == False:
            summonerTft["gameExist"] = True
            summonerTft["latestGame"] = checkRecentTft[0]
            print("Latest game is ranked and is kept in memory")
        else:
            if summonerTft["latestGame"] == checkRecentTft[0]:
                print("No new matches")
                if summonerListTft.index(summonerTft) == (len(summonerListTft) - 1):
                    return
                continue
            else:
                print("Found new ranked match to replace old match")
                summonerTft["latestGame"] = checkRecentTft[0]

        #Collect individual user's data
        participantList = matchDataTft['info']['participants']
        for participants in participantList:
            if participants['puuid'] == summonerDataTft['puuid']:
                level = participants['level']
                placement = participants['placement']
                timeEliminated = participants['time_eliminated']
                damageDealt = participants['total_damage_to_players']
        gametime = matchDataTft['info']['game_length']
        minutes = int(gametime/60)
        seconds = int(gametime%60)
        eliminatedMin = int(timeEliminated/60)
        eliminatedSec = int(timeEliminated%60)
        if eliminatedSec < 10:
            eliminatedSec = f"0{eliminatedSec}"
        if seconds < 10:
            seconds = f"0{seconds}"
            
        if placement == 1:
            placement = "1st"
        elif placement == 2:
            placement = "2nd"
        elif placement == 3:
            placement = "3rd"
        else:
            placement = f"{placement}th"
        #Collect rank stats
        tft_stats = tft_watcher.league.by_summoner(my_region, summonerDataTft['id'])
        if tft_stats:
            ranked_data = tft_stats[0]
            name = ranked_data['summonerName']
            tier = ranked_data['tier'].title()
            rank = ranked_data['rank']
            lp = ranked_data['leaguePoints']
        #Display information in an embed
        embed = discord.Embed(
            title = f"{summonerTft['name']}'s Ranked TFT Match: {placement}",
            description = f'Game Time: {minutes}:{seconds}'
        )
        embed.set_footer(text = 'Created by minkim#8625')
        if placement == '1st':
            embed.color= discord.Colour.from_rgb(255, 215, 0)
        elif placement == '2nd':
            embed.color= discord.Colour.from_rgb(192, 192, 192)
        elif placement == '3rd':
            embed.color= discord.Colour.from_rgb(205, 127, 50)
        else:
            embed.color = discord.Colour.from_rgb(0, 0, 0)
        embed.add_field(name="Time Eliminated", value=f"{eliminatedMin}:{eliminatedSec}", inline=True)
        embed.add_field(name="Level", value=f"{level}", inline=True)
        embed.add_field(name="Total Damage Dealt", value=f"{damageDealt}", inline=True)
        if tft_stats:
            embed.add_field(name="Rank", value=f"{tier} {rank}", inline=True)
            embed.add_field(name="LP", value=f"{lp}", inline=True)
        channel = bot.get_channel() #Input channel ID as parameter of function.
        await channel.send(embed=embed)

# Append usernames to auto-update rank history for Teamfight Tactics
@bot.command()
async def requestTftUpdate(ctx, *, arg):
    try: 
        if summonerListTft:
            for summonersInTft in summonerListTft:
                if summonersInTft['name'] == arg:
                    summonerListTft.remove(summonersInTft)
                    await ctx.send(f'TFT auto-update has been turned off for {arg}!')
                    return
        global summonerEmptyTft
        summonerEmptyTft = False
        me = lol_watcher.summoner.by_name(my_region, arg) # If the username is not valid, error is returned via except
        dict = {
            "name": arg,
            "gameExist": False,
            "latestGame": "" 
        }
        summonerListTft.append(dict)
        print(1)
        await ctx.send(f'Added {arg} to Teamfight Tactics Ranked Updater!')
    except:
        await ctx.send('Error: User not found')

# Gives back lol stats for summoner
@bot.command()
async def lolstats(ctx, *, arg):
    try:
        me = lol_watcher.summoner.by_name(my_region, arg)
        lol_stats = lol_watcher.league.by_summoner(my_region, me['id'])
        queue = 0
        for queues in lol_stats:
            if queues['queueType'] == 'RANKED_SOLO_5x5':
                break
            queue += 1
        ranked_data = lol_stats[queue]
        tier = ranked_data['tier'].title()
        rank = ranked_data['rank']
        lp = ranked_data['leaguePoints']
        wins = ranked_data['wins']
        losses = ranked_data['losses']
        winRate = int(wins/(wins + losses)  * 100)
        
        embed = discord.Embed(
            title = f'Ranked Stats for {arg}',
            description = f'Game: League of Legends'
        )
        #Change embed color based on Rank
        if tier == 'Challenger':
            embed.color= discord.Colour.from_rgb(230, 230, 230)
        elif tier == 'Grandmaster':
            embed.color= discord.Colour.from_rgb(204, 0, 0)
        elif tier == 'Master':
            embed.color= discord.Colour.from_rgb(209, 26, 255)
        elif tier == 'Diamond':
            embed.color= discord.Colour.from_rgb(77, 219, 255)
        elif tier == 'Platinum':
            embed.color= discord.Colour.from_rgb(0, 230, 172)
        elif tier == 'Gold':
            embed.color= discord.Colour.from_rgb(255, 215, 0)
        elif tier == 'Silver':
            embed.color= discord.Colour.from_rgb(192, 192, 192)
        elif tier == 'Bronze':
            embed.color= discord.Colour.from_rgb(205, 127, 50)
        else:
            embed.color = discord.Colour.from_rgb(92, 92, 61)
        embed.set_footer(text = 'Created by minkim#8625')
        embed.add_field(name="Rank", value=f"{tier} {rank}", inline=True)
        embed.add_field(name="LP", value=f"{lp}", inline=True)
        embed.add_field(name = chr(173), value = chr(173))
        embed.add_field(name="Wins", value=f"{wins}", inline=True)
        embed.add_field(name="Losses", value=f"{losses}", inline=True)
        embed.add_field(name="Win Rate", value=f"{winRate}%", inline=True)
        embed.add_field(name = chr(173), value = chr(173))
        await ctx.send(embed=embed)
    except:
        await ctx.send('Error: Summoner not found OR not enough matches.')

# Gives back tft stats for summoner
@bot.command()
async def tftstats(ctx, *, arg):
    try:
        me = tft_watcher.summoner.by_name(my_region, arg)
        tft_stats = tft_watcher.league.by_summoner(my_region, me['id'])
        ranked_data = tft_stats[0]
        name = ranked_data['summonerName']
        tier = ranked_data['tier'].title()
        rank = ranked_data['rank']
        lp = ranked_data['leaguePoints']
        wins = ranked_data['wins']
        losses = ranked_data['losses']
        winRate = int(wins/(wins + losses)  * 100)
        embed = discord.Embed(
            title = f'Ranked Stats for {arg}',
            description = f'Game: Teamfight Tactics'
        )
        #Change embed color based on rank
        if tier == 'Challenger':
            embed.color= discord.Colour.from_rgb(230, 230, 230)
        elif tier == 'Grandmaster':
            embed.color= discord.Colour.from_rgb(204, 0, 0)
        elif tier == 'Master':
            embed.color= discord.Colour.from_rgb(209, 26, 255)
        elif tier == 'Diamond':
            embed.color= discord.Colour.from_rgb(77, 219, 255)
        elif tier == 'Platinum':
            embed.color= discord.Colour.from_rgb(0, 230, 172)
        elif tier == 'Gold':
            embed.color= discord.Colour.from_rgb(255, 215, 0)
        elif tier == 'Silver':
            embed.color= discord.Colour.from_rgb(192, 192, 192)
        elif tier == 'Bronze':
            embed.color= discord.Colour.from_rgb(205, 127, 50)
        else:
            embed.color = discord.Colour.from_rgb(92, 92, 61)
        embed.set_footer(text = 'Created by minkim#8625')
        embed.add_field(name="Rank", value=f"{tier} {rank}", inline=True)
        embed.add_field(name="LP", value=f"{lp}", inline=True)
        embed.add_field(name = chr(173), value = chr(173))
        embed.add_field(name="Wins", value=f"{wins}", inline=True)
        embed.add_field(name="Losses", value=f"{losses}", inline=True)
        embed.add_field(name="Win Rate", value=f"{winRate}%", inline=True)
        embed.add_field(name = chr(173), value = chr(173))
        await ctx.send(embed=embed)
    except:
        await ctx.send('Error: Summoner not found OR not enough matches')

# Search for recent League of Legends matches of summoner.
@bot.command()
async def lolhistory(ctx, *, arg):
    try:
        me = lol_watcher.summoner.by_name(my_region, arg)
        history = lol_watcher.match_v5.matchlist_by_puuid('AMERICAS', me['puuid'], None, 20)
        matchCount = 0
        await ctx.send('Finding up to 5 most recent ranked solo/duo matches for user: ' + arg)
        for match in history:
            # Finds match data for each of the selected 20 matches
            matchData = lol_watcher.match_v5.by_id('AMERICAS', match)
            if matchData['info']['queueId'] != 420: # Checks if match is not a ranked solo/duo game
                continue # if not ranked solo/duo, skip iteration
            matchCount += 1
            # Check users position and which side team
            participantList = matchData['info']['participants']
            participantCount = 0
            totalKills = 0
            totalAssists = 0
            totalDeaths = 0
            totalDamage = 0
            position = None
            for participants in participantList:
                if participants['puuid'] == me['puuid']:
                    position = participantCount
                participantCount += 1
            # Collect team data based on which side the user was in
            if position < 5: 
                for i in range(0, 5):
                    totalDamage += participantList[i]['totalDamageDealtToChampions']
                    totalKills += participantList[i]['kills']
                    totalAssists += participantList[i]['assists']
                    totalDeaths += participantList[i]['deaths']
            else:
                for i in range(5, 10):
                    totalDamage += participantList[i]['totalDamageDealtToChampions']
                    totalKills += participantList[i]['kills']
                    totalAssists += participantList[i]['assists']
                    totalDeaths += participantList[i]['deaths']
            # Collect data
            myData = matchData['info']['participants'][position]
            champion = myData['championName']
            kills = myData['kills']
            deaths = myData['deaths']
            assists = myData['assists']
            damage = myData['totalDamageDealtToChampions']
            doubleKill = myData['doubleKills']
            tripleKill = myData['tripleKills']
            quadraKill = myData['quadraKills']
            pentaKill = myData['pentaKills']
            visionScore = myData['visionScore']
            if deaths != 0:
                kda = round(((kills + assists)/deaths), 2)
            else:
                kda = 'Perfect Score'
            myPosition = myData['teamPosition'].title()
            if myPosition == 'Utility':
                myPosition = 'Support'
            myTeam = myData['teamId']
            timePlayed = myData['timePlayed']
            minutes = int(timePlayed/60)
            seconds = (int(timePlayed%60))
            if seconds < 10:
                seconds = f"0{seconds}"
            # Assign side to user and check result of match
            if myTeam == 100:
                teamColor = 'Blue'
                result = matchData['info']['teams'][0]['win']
            else:
                teamColor = 'Red'
                result = matchData['info']['teams'][1]['win']
            if result == True:
                result = 'Victory'
            else:
                result = 'Defeat'
            #Display information in an embed
            embed = discord.Embed(
                title = f"Match {matchCount}: {result}",
                description = f'Game Time: {minutes}:{seconds}'
            )
            embed.set_footer(text = 'Created by minkim#8625')
            if result == 'Victory':
                embed.color= discord.Colour.blue()
            else:
                embed.color = discord.Colour.red()
            embed.add_field(name="Team Side", value=f"{teamColor} Side", inline=True)
            embed.add_field(name="Position", value=f"{myPosition}", inline=True)
            embed.add_field(name = chr(173), value = chr(173))
            embed.add_field(name="Champion", value=f"{champion}", inline=True)
            embed.add_field(name="K/D/A", value=f"{kills}/{deaths}/{assists} ({kda})", inline=True)
            embed.add_field(name="Kill Participation", value=f"{round((kills + assists)/totalKills * 100)}%", inline=True)
            embed.add_field(name="Total Damage Dealt to Champions", value=f"{damage}", inline=True)
            embed.add_field(name="Damage Percentage", value=f"{round(damage/totalDamage * 100)}%", inline=True)
            embed.add_field(name="Vision Score", value=f"{visionScore}", inline=True)
            embed.add_field(name="Multi Kills", value=f"Double Kills: {doubleKill}\nTriple Kills: {tripleKill}\nQuadra Kills: {quadraKill}\nPenta Kills: {pentaKill}", inline=True)
            await ctx.send(embed=embed)
            
            if matchCount == 5:
                break
        await ctx.send(f'Found {matchCount} ranked matches from recent games.')
    except:
        await ctx.send('Error: user not found.')

# Search for recent Teamfight Tactics matches of summoner.
@bot.command()
async def tfthistory(ctx, *, arg):
    try:
        me = tft_watcher.summoner.by_name(my_region, arg)
        history = tft_watcher.match.by_puuid('AMERICAS', me['puuid'], 20)
        matchCount = 0
        await ctx.send('Finding up to 5 most recent ranked TFT matches for user: ' + arg)
        for match in history:
            # Finds match data for each of the selected 20 matches
            matchData = tft_watcher.match.by_id('AMERICAS', match)
            if matchData['info']['queue_id'] != 1100: # Checks if match is not a ranked game
                continue # if not ranked, skip iteration
            matchCount += 1
            #Collect individual user's data
            participantList = matchData['info']['participants']
            for participants in participantList:
                if participants['puuid'] == me['puuid']:
                    level = participants['level']
                    placement = participants['placement']
                    timeEliminated = participants['time_eliminated']
                    damageDealt = participants['total_damage_to_players']
            gametime = matchData['info']['game_length']
            minutes = int(gametime/60)
            seconds = int(gametime%60)
            eliminatedMin = int(timeEliminated/60)
            eliminatedSec = int(timeEliminated%60)
            if seconds < 10:
                seconds = f"0{seconds}"
            if eliminatedSec < 10:
                eliminatedSec = f"0{eliminatedSec}"
            if placement == 1:
                placement = "1st"
            elif placement == 2:
                placement = "2nd"
            elif placement == 3:
                placement = "3rd"
            else:
                placement = f"{placement}th"
            #Display information in an embed
            embed = discord.Embed(
                title = f"{arg}'s Ranked TFT Match: {placement}",
                description = f'Game Time: {minutes}:{seconds}'
            )
            embed.set_footer(text = 'Created by minkim#8625')
            if placement == '1st':
                embed.color= discord.Colour.from_rgb(255, 215, 0)
            elif placement == '2nd':
                embed.color= discord.Colour.from_rgb(192, 192, 192)
            elif placement == '3rd':
                embed.color= discord.Colour.from_rgb(205, 127, 50)
            else:
                embed.color = discord.Colour.from_rgb(0, 0, 0)
            embed.add_field(name="Time Eliminated", value=f"{eliminatedMin}:{eliminatedSec}", inline=True)
            embed.add_field(name="Level", value=f"{level}", inline=True)
            embed.add_field(name="Total Damage Dealt", value=f"{damageDealt}", inline=True)
            await ctx.send(embed=embed)
            
            if matchCount == 5:
                break
        if matchCount == 0:
            await ctx.send('No ranked matches found from recent games')
        else:
            await ctx.send(f'Found {matchCount} ranked matches from recent games')
    except:
        await ctx.send('Error: User not found.')

bot.run(token)