import os, re, time
import discord
import sqlite3
from config import token, db_file
from discord.ext import commands
from discord.utils import get

# -------------------------------------------------------------------------------------------
# Define Global Variables
bot = commands.Bot(command_prefix='.qtr', case_insensitive=True)
bot.remove_command('help')

iCounter = 0
# -------------------------------------------------------------------------------------------
# Initialise Bot
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="user's quotes! | .qtrHelp"))
    print("-- Qtr Ready! --\n\n")
    
# -------------------------------------------------------------------------------------------
# Help Command
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.purple()
    )

    embed.set_author(name='Help')
    embed.add_field(name='Bot Prefix: .qtr', value='Used before all commands. Commands are not case sensitive.', inline=False)
    embed.add_field(name='.qtrPing', value='Returns Pong! and bot latency.', inline=False)
    embed.add_field(name='.qtrSetup', value="Begins setup for Qtr in respective channel. [ADMIN]", inline=False)
    embed.add_field(name='.qtrReset', value='Begins the reset for Qtr, removing all server information. [ADMIN]', inline=False)
    embed.add_field(name='Documentation:', value="https://github.com/Delriss/Qtr (W.I.P)", inline=False)

    await ctx.author.send(embed=embed)
    
# -------------------------------------------------------------------------------------------
# Ping for latency
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

# -------------------------------------------------------------------------------------------
# On Join - Setup
@bot.event
async def on_guild_join(guild):
    await guild.text_channels[0].send("***Welcome to Qtr!*** \n\n> This bot will manage all of your quoting needs, but first a setup is required. Please enter the `.qtrSetup` command in your chosen quotes channel to continue the setup.\nFor more information use '.qtrHelp'.")

# -------------------------------------------------------------------------------------------
# Setup Command
@bot.group(case_insensitive=True)
@commands.has_guild_permissions(administrator=True)
async def setup(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("This will setup all requirements for Qtr.\nQuotes made here will be recorded into the system.\nPlease note that previously created quotes will not be included.\n\nWARNING: This action is irreversible, to continue please execute `.qtrSetup Agree`.")
    
@setup.command()    
async def agree(ctx):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id
    
    #Check Database + Save Database
    is_inDatabase = False
    
    try:
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #SELECT STATEMENT
        sql_Select = """SELECT Channel_ID FROM tblGuilds WHERE Channel_ID = ?"""
        
        sqlCursor.execute(sql_Select, (channel_id,))
        
        records = sqlCursor.fetchall()
        iCounter = 0
        for row in records:
            if channel_id == row[iCounter]:
                iCounter += 1
                print("Setup has already been performed.")
                is_inDatabase = True
        sqlCursor.close()
        sqliteConnection.close()
        
        
    except sqlite3.Error as e: #Catch Error in Inputting
        print("Failed to find information into SQL table - Setup. Error:", e)      
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("Database Connection Closed")
    
    if is_inDatabase == True:
        await ctx.send("Setup has already been completed.")
    else:
        #Save to Database Section
        await ctx.send("This setup will create the necessary pins and messages in your quote channel. Please note that previous quotes will not be counted, as it is currently not supported.\n")
        await ctx.send("Please wait for the setup to complete...")
        
        time.sleep(2)
        
        #Setup Counter Embed
        embed=discord.Embed(title="Quote Counter", description="A current count of the top quoted users!", color=0x8080c0)
        embed.set_author(name="Qtr")
        embed.set_footer(text="QTR - Quote Counter")
        countermessage = await ctx.send(embed=embed)
        await countermessage.pin(reason = "Qtr Quote Counter")
        ##print(countermessage.id)
        ##print(countermessage.channel.id)
        ##print(countermessage.guild.id)
        
            
        time.sleep(2)
            
        #Setup Leaderboard Embed
        embed=discord.Embed(title="Quote Leaderboard", description="A leaderboard for the most liked quotes!", color=0x0000ff)
        embed.set_author(name="Qtr - Leaderboard")
        embed.set_footer(text="QTR - Quote Leaderboard")
        leaderboardmessage = await ctx.send(embed=embed)
        await leaderboardmessage.pin(reason = "Qtr Quote Leaderboard")
        ##print(leaderboardmessage.id) # Here for debugging
        ##print(leaderboardmessage.channel.id)
        ##print(leaderboardmessage.guild.id)
        
        importNewGuild(guild_id, channel_id)
        importNewChannel(channel_id, countermessage.id, leaderboardmessage.id)
        
        time.sleep(2)

        await ctx.send("Setup Complete!")

# -------------------------------------------------------------------------------------------
# On Guild Remove
@bot.event
async def on_guild_remove(guild):
    removeGuildEntries(guild)

# -------------------------------------------------------------------------------------------
# Reset Command
@bot.group(case_insensitive=True)
@commands.has_guild_permissions(administrator=True)
async def reset(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("WARNING: This command will remove all data relating to your server from the database. This includes Setup Channels, Quote Counters and Quote Leaderboards.\nThis should only be used for a necessary reset.\n\nTo continue execute `.qtrReset Confirm` within the respective quotes channel.")

@reset.command()
async def confirm(ctx):
    CounterMessage_ID = None
    LeaderMessage_ID = None
    channel = ctx.channel
    
    await ctx.send("Deleting data...")
    
    try:
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #SELECT STATEMENT
        sql_Select = """SELECT CounterMessage_ID, LeaderMessage_ID FROM tblMessageIDs WHERE Channel_ID = ?"""
        
        sqlCursor.execute(sql_Select, (ctx.channel.id,))
        records = sqlCursor.fetchall()

        for row in records:
            CounterMessage_ID = row[0]
            LeaderMessage_ID = row[1]
        
        print(CounterMessage_ID)
        delMessage = await channel.fetch_message(CounterMessage_ID)
        await delMessage.delete()
        
        delMessage = await channel.fetch_message(LeaderMessage_ID)
        await delMessage.delete()
        
        sqlCursor.close()
        sqliteConnection.close()
        
        
    except sqlite3.Error as e: #Catch Error in Inputting
        print("Failed to find information into SQL table - Reset. Error:", e)      
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("Database Connection Closed")
            
    removeGuildEntries(ctx.guild)
    
    await ctx.send("Data deleted. Thank you for using Qtr!")
    
# -------------------------------------------------------------------------------------------
# Quote Made
@bot.event
async def on_message(message):
    quoteRegex = re.search(r'"(.*)"\s*-\s*(.*)', message.content) # Makes sure message = "Quote" - Name
    if quoteRegex:
        try:
            sqliteConnection = sqlite3.connect(db_file)
            sqlCursor = sqliteConnection.cursor()
            print("\nDatabase Connection Success")
            
            #SELECT STATEMENTS
            sql_Select_tblGuild = """SELECT Channel_ID FROM tblGuilds WHERE Guild_ID = ?"""
            
            sqlCursor.execute(sql_Select_tblGuild, (message.guild.id,))
            
            needToUpdate = False
            iCounter = 0
            records = sqlCursor.fetchall()
            for row in records:
                if message.channel.id == row[iCounter]:
                    quoteRegex = re.search(r'"(.*)"\s*-\s*(.*)', message.content) # Makes sure message = "Quote" - Name
                    if quoteRegex:
                        quoteName = quoteRegex.group(2) #Grabs name
                        #Format Name
                        quoteName = quoteName.lower() # Lower Case
                        quoteName = quoteName.capitalize() # Capatilise
                        #print(quoteName) # Debugging
                        addCounter(quoteName, message)
                        needToUpdate = True
                        
                iCounter += 1
            
            if needToUpdate == True:    
                try:
                    channel = message.channel
                    #SELECT STATEMENTS
                    sql_Select_QuoteCount = """SELECT Quote_Name, Quote_Count FROM tblQuotes WHERE Guild_ID = ? ORDER BY Quote_Count DESC LIMIT 20"""
                    sqlCursor.execute(sql_Select_QuoteCount, (message.guild.id,))
                    records = sqlCursor.fetchall()
                    
                    ##Grab CounterMessage_ID
                    sql_Select_CounterMessage_ID = """SELECT CounterMessage_ID FROM tblMessageIDs WHERE Channel_ID = ?"""
                    sqlCursor.execute(sql_Select_CounterMessage_ID, (channel.id,))
                    CounterMessage = sqlCursor.fetchone()
                    
                    embedMessage = await (channel).fetch_message(CounterMessage[0])
                    embed = embedMessage.embeds[0]
                    embed.clear_fields()
                    
                    iCounter = 1
                    for rows in records:
                        fieldName = str(iCounter)+ ") " + rows[0]
                        embed.add_field(name=fieldName, value=rows[1], inline=False)
                        iCounter += 1
                        
                    await embedMessage.edit(embed=embed)
        
                except sqlite3.Error as e: #Catch Error in Inputting
                    print("Failed to find information into SQL table - Update Counter. Error:", e)
        
            sqlCursor.close()
        
        
        except sqlite3.Error as e: #Catch Error in Inputting
            print("Failed to find information into SQL table - Quote Made. Error:", e)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("Database Connection Ended")
                
    await bot.process_commands(message)
    
    
# -------------------------------------------------------------------------------------------
# Reaction Added
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.count > 3:
        
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #SELECT STATEMENTS
        sql_Select_tblGuild = """SELECT Channel_ID FROM tblGuilds WHERE Guild_ID = ?"""
        
        sqlCursor.execute(sql_Select_tblGuild, (reaction.message.guild.id,))
        records = sqlCursor.fetchone()
        reactionChannel = (records[0])
        
        sqlCursor.close()
        sqliteConnection.close()
        print("Database Connection Ended") 
        
        if reaction.message.channel.id == reactionChannel:
            print("Reaction Matches")
            try:
                sqliteConnection = sqlite3.connect(db_file)
                sqlCursor = sqliteConnection.cursor()
                print("\nDatabase Connection Success")
                
                #INSERT STATEMENT
                sql_Upsert_Quote = """INSERT INTO tblLeaderboard(Guild_ID, Channel_ID, Message_ID, Reactions) 
                                    VALUES (?,?,?,?)
                                    ON CONFLICT(Guild_ID, Message_ID)
                                    DO UPDATE SET Reactions = Reactions+1
                                    """
                
                import_variables = (reaction.message.guild.id, reaction.message.channel.id, reaction.message.id, reaction.count)
                sqlCursor.execute(sql_Upsert_Quote, import_variables)
                sqliteConnection.commit()
                print("Reaction Inserted/Updated")
                
                #SELECT STATEMENTS
                sql_Select_Reactions = """SELECT Message_ID, Reactions FROM tblLeaderboard WHERE Guild_ID = ? ORDER BY Reactions DESC LIMIT 20"""
                sqlCursor.execute(sql_Select_Reactions, (reaction.message.guild.id,))
                records = sqlCursor.fetchall()
                
                ##Grab CounterMessage_ID
                sql_Select_LeaderboardMessage_ID = """SELECT LeaderMessage_ID FROM tblMessageIDs WHERE Channel_ID = ?"""
                sqlCursor.execute(sql_Select_LeaderboardMessage_ID, (reaction.message.channel.id,))
                LeaderboardMessage = sqlCursor.fetchone()
                
                embedMessage = await (reaction.message.channel).fetch_message(LeaderboardMessage[0])
                embed = embedMessage.embeds[0]
                embed.clear_fields()
                
                iCounter = 1
                for rows in records:
                    fieldMessage = await (reaction.message.channel).fetch_message(rows[0])                     
                    fieldName = str(iCounter)+ ") " + fieldMessage.content
                    embed.add_field(name=fieldName, value=rows[1], inline=False)
                    iCounter += 1
                
                await embedMessage.edit(embed=embed)
                
                sqlCursor.close()
                sqliteConnection.close()
                
            except sqlite3.Error as e: #Catch Error in Inputting
                print("Failed to insert information into SQL table - On_Reaction. Error:", e)
            finally:
                if (sqliteConnection):
                    sqliteConnection.close()
                    print("Database Connection Ended")
                
        
    
             
# -------------------------------------------------------------------------------------------
##Functions 

#Adds New Guild and Channel to Guild Table
def importNewGuild(messageGuild, messageChannel): #Imports new record into Guild_Channel 
    try:
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #INSERT STATEMENT
        sql_Insert = """INSERT INTO tblGuilds (Guild_ID, Channel_ID) VALUES (?,?);"""
        
        import_variables = (messageGuild, messageChannel)
        sqlCursor.execute(sql_Insert, import_variables)
        sqliteConnection.commit()
        print("Guild-Channel Record Inserted Successfully")
        
        sqlCursor.close()
        sqliteConnection.close()
        
    except sqlite3.Error as e: #Catch Error in Inputting
        print("Failed to insert information into SQL table - importNewGuild. Error:", e)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("Database Connection Ended")

#Adds new Channel and Message IDs to Message IDs table            
def importNewChannel(messageChannel, counter_messageID, leaderboard_messageID): #Imports new record into Guild_Channel
    try:
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #INSERT STATEMENT
        sql_Insert = """INSERT INTO tblMessageIDs (Channel_ID, CounterMessage_ID, LeaderMessage_ID) VALUES (?,?,?);"""
        
        import_variables = (messageChannel, counter_messageID, leaderboard_messageID)
        sqlCursor.execute(sql_Insert, import_variables)
        sqliteConnection.commit()
        print("Channel-Message Record Inserted Successfully")
        
        sqlCursor.close()
        sqliteConnection.close()
        
    except sqlite3.Error as e: #Catch Error in Inputting
        print("Failed to insert information into SQL table - importNewChannel. Error:", e)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("Database Connection Ended")

#Inserts new quote / Updates quote to database    
def addCounter(userName, message):
    channel = message.channel.id
    try:
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #SELECT STATEMENTS
        #sql_Select_tblMessageIDs = """SELECT CounterMessage_ID FROM tblMessageIDs WHERE Channel_ID = ?"""
        sql_Upsert_Quote = """INSERT INTO tblQuotes(Guild_ID, Quote_Name, Quote_Count) 
                              VALUES (?,?,?)
                              ON CONFLICT(Guild_ID, Quote_Name)
                              DO UPDATE SET Quote_Count=Quote_Count+1
                              """
        
        import_variables = (message.guild.id, userName, 1)
        sqlCursor.execute(sql_Upsert_Quote, import_variables)
        sqliteConnection.commit()
        print("Quote Inserted/Updated")
        
        sqlCursor.close()
        sqliteConnection.close()
    
    except sqlite3.Error as e: #Catch Error in Inputting
        print("Failed to find information in SQL table - Add Counter. Error:", e)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("Database Connection Ended")
    
# Removes database entries for a guild    
def removeGuildEntries(guild):
    try:
        sqliteConnection = sqlite3.connect(db_file)
        sqlCursor = sqliteConnection.cursor()
        print("\nDatabase Connection Success")
        
        #SELECT STATEMENTS
        sql_Select_tblGuild = """SELECT Channel_ID FROM tblGuilds WHERE Guild_ID = ?"""
        sqlCursor.execute(sql_Select_tblGuild, (guild.id,))
        records = sqlCursor.fetchall()
        
        iCounter = 0
        for row in records:
            #Delete Message IDs
            sql_Select_tblMessageIDs = """SELECT Channel_ID FROM tblMessageIDs WHERE Channel_ID = ?"""
            sqlCursor.execute(sql_Select_tblMessageIDs, (row[iCounter],))
            MessageRecords = sqlCursor.fetchall()
            
            iMessageCounter = 0
            for rows in MessageRecords:
                sql_Delete_tblMessageIDs = """DELETE FROM tblMessageIDs WHERE Channel_ID = ?"""
                sqlCursor.execute(sql_Delete_tblMessageIDs, (rows[iMessageCounter],))
                sqliteConnection.commit()
                iMessageCounter += 1
            
            sql_Select_tblQuotes = """SELECT Guild_ID FROM tblQuotes WHERE Guild_ID = ?"""
            sqlCursor.execute(sql_Select_tblQuotes, (guild.id,))
            QuoteRecords = sqlCursor.fetchall()
            
            iQuoteCounter = 0
            for rows in QuoteRecords:
                sql_Delete_tblQuotes = """DELETE FROM tblQuotes WHERE Guild_ID = ?"""
                sqlCursor.execute(sql_Delete_tblQuotes, (guild.id,))
                sqliteConnection.commit()
                iQuoteCounter += 1
            
            print("Guild ID is present in database. Removing entry...")
            sql_Update_tblGuild = """DELETE FROM tblGuilds WHERE Guild_ID = ?"""
            sqlCursor.execute(sql_Update_tblGuild, (guild.id,))
            sqliteConnection.commit()
            
            iCounter += 1     
            
        sqlCursor.close()
        
    except sqlite3.Error as e: #Catch Error in Inputting
        print("Failed to find information into SQL table - Guild Remove. Error:", e)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("Database Connection Ended") 
    

# -------------------------------------------------------------------------------------------
# Bot Key (DO NOT SHOW)
bot.run(token)
    

