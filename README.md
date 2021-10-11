# LolStats

A Discord statistics bot for two popular games made by Riot Games: *League of Legends* and *Teamfight Tactics*.

## What does LolStats do?

LolStats is an automated bot for the popular messaging service, Discord. Users can enter commands to do the following: 
* Search for a player's ranking.
* Search for a player's match history (up to 5 most recent games).
* Get live updates for every finished match.

Here are images to demonstrate how the bot works.

![Demo of #helpStats](/images/helpCommand.JPG)

**Command:** #helpStats *username*

**Description:** Returns a discord embed with a list of commands for this bot.

![Demo of #lolStats](/images/lolStats.JPG)

**Command:** #lolstats *username*

**Description:** Returns League of Legends ranked solo/duo stats for the user.

![Demo of #tftStats](/images/tftStats.JPG)

**Command:** #tftstats *username*

**Description:** Returns Teamfight Tactics ranked stats for the user.

![Demo of #lolHistory](/images/lolHistory.JPG)

**Command:** #lolhistory *username*

**Description:** Returns League of Legends ranked solo/duo match history for the user. (Up to 5 games)

![Demo of #tftHistory](/images/tftHistory.JPG)

**Command:** #tfthistory *username*

**Description:** Returns Teamfight Tactics ranked match history for the user. (Up to 5 games)

![Demo of #requestLolUpdate](/images/requestLolUpdate.JPG)

**Command:** #requestLolUpdate *username*

**Description:** Toggles the League of Legends ranked update function for the user. Whenever a League of Legends ranked solo/duo match is finished, that match's statistics will be returned.

![Demo of #requestTftUpdate](/images/requestTftUpdate.JPG)

**Command:** #requestTftUpdate *username*

**Description:** Toggles the Teamfight Tactics ranked update function for the user. Whenever a Teamfight Tactics ranked match is finished, that match's statistics will be returned.

## How can I add this bot?

At the moment, the bot is not publicly available. This is due to the nature of the API that this bot utilizes to gather data. 
Riot Games' API, called "[Riot API](https://developer.riotgames.com/)", requires API keys for developers to gather data from their games. 
The problem with these API keys are that they only last for 24 hours, before requiring you to replace the old key with a new one. 
One can apply for a personal API key that is permanent, but it requires a fully fledged product or is strictly for personal use. 

One way you can test this bot out for yourself is to make your own Discord bot using the files in this repository, with a few additional steps required to get everything setup.
I will create more in=depth instructions at a later date.

For now, here is a basic outline of what should be done to recreate this bot.
1. Create a Discord bot application in the Discord Developer Portal. There are several tutorials on youtube for this. (I may update this README with my own step-by-step instructions.)
2. Clone this repository.
3. Create a .env file to store the token that is provided by your Discord bot application. Include the .env file in a .gitignore file.

![Example of .env](/images/env.JPG) ![Example of .gitignore](/images/gitignore.JPG)

4. Obtain a [Riot API key](https://developer.riotgames.com/).
5. Paste the API key into the LolWatcher and TftWatcher functions in lines 9 and 10 of the boy.py file.

![API Key Functions](/images/apikey.JPG)

6. For the requestLolUpdate and requestTftUpdate commands to work, you must edit the bot.py file in lines 182 and 292 by entering a channel ID. The current version of ranked updater will only be able to send embeds through this channel. Right click on a channel of the server that you would like to test the bot in to find its channel ID.

![Right Click for Channel ID](/images/getChannel.JPG)

7. Run the bot.py file locally or through a hosting service (A Heroku procfile has been included in this repository for you).

## What's next for this bot?
Improvements can be made to this bot in the future. Some features that may be implemented in the future are the following:
- Remove the need to manually change the channel ID in the code.
- Allow easy switching between regions.
- Link the bot to a database to save requestLolUpdate and requestTftUpdate usernames, so that they are available upon restart of the bot.

Please contact me for any suggestions.
