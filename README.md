# Qtr
Qtr, the quote management bot!

# What is Qtr?
Qtr is a quote management bot that will assist with your quoting needs. This bot provides a way to keep track of statistics, such as the current quote count, the highest ranked quote and all of the people who have been quoted in the server.

When formatting the message, Qtr will recognise quotes that are formatted in a ```"[Quote]" - [Name]``` form.

To configure Qtr to your specific quotes channel, please run the ```.qtrSetup``` command in the channel of your choice, which will create the necessary connections and pins to allow the bot to work away! (This requires administrator permissions)

If there are any problems with Qtr, let me know! Please file an issue and I will try to solve it right away!

# Features
Qtr has a few features to improve management and viewing of your quotes channel. Some of these features are work-in-progress and will be updated in the future.


### Quote Counting
The main feature of Qtr is the counting function. This links your quotes channel to the database and records each time a quote is made by a particular user.This counter will link to a pinned message in your channel, showing you all the statistics you need to keep track of your counting and motivate your server to quote, quote, quote!

### Quote Leaderboard
This feature is W.I.P and is not yet developed. This feature will aim to list the top quotes by users, using other user's reaction as a ranking system. This will promote viewing of the quotes channel and kind reactions!

# FAQ

##### Qtr won't respond to me!
Make sure that the bot has sufficient permissions, in both the server and the channel that you are trying to execute the command in. Also make sure that you have sufficient permissions if you are attempting to run a permission required command (e.g. .qtrSetup / .qtrReset)

##### I want to reset my quotes channel!
If you wish to reset your quotes channel and all of the information for your server, relating to Qtr, please execute the `.qtrReset`. This command will remove all information from the Qtr Database including: Guild ID, Channel IDs, Message IDs and Quoted Names. Please take care when executing this command, as it cannot be reversed and will remove all of the information of your server's quote channel. (This command required administrator permissions)

##### What happens to my data when the bot leaves?
Dont worry, when the bot leaves your server, it will run a command to remove all data relating to your server from the database. This means that the bot will have a fresh start for your server, if you wish to add it again. However, please note that all quote counts and names will also be deleted. This action is irreversible.
