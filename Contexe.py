'''
Ayo, Rath here! Cont.exe is a bot designed for running Jay Dragon's Flower Court, so it's got a few specific
functions in mind. The primary one is anonymized, simultaneous mail sending. Players need to be able to send
the bot their messages and only have them revealed when everyone opens the server-wide mailbox. As a function
of that, the bot also has players assign themselves to roles, so that when sending mail you can put in player
names or roles and both come out exactly the same. Additionally, there's a coin flip function for when the
Whispers game happens, including reminders of what side means what.

The bot recognizes a wide variety of inputs as valid (including a lot of alternate commands and emotes), but
I made the conscious decision to make player names in the #send function very rigid. That way there's no chance
of confusion, typos or differing typing styles spoiling who's sending what messages.
'''

import discord, random

TOKEN = [censored]
ARCHETYPES = ('prinxarch', 'infante', 'doxe', 'contex', 'stranger', 'courtesan', 'cinderella', 'dignitary',
              'baronne', 'knight', 'dowager', 'tycoon')

SEND_COMMANDS = ('send', 'message', 'letter')
MAIL_COMMANDS = ('mail', 'mailbox')
ASGN_COMMANDS = ('assign', 'role')
LIST_COMMANDS = ('list', 'players')
FLIP_COMMANDS = ('flip', 'coin')
HELP_COMMANDS = ('help', 'what', 'huh', 'um')

HEARTS = ('<3', 'heart', ':<3:', ':sparkling_heart:', ':heart_decoration:', ':heart_exclamation:', ':heart_eyes:',
          ':heart_eyes_cat:', ':hearts:', ':black_heart:', ':blue_heart:', ':brown_heart:', ':couple_with_heart:',
          ':couple_with_heart_woman_man:', ':gift_heart:', ':green_heart:', ':kissing_heart:', ':orange_heart:',
          ':purple_heart:', ':revolving_hearts:', ':smiling_face_with_3_hearts:', ':two_hearts:', ':white_heart:',
          ':yellow_heart:', ':heartbeat:', ':heartpulse:', ':couple_mm:', ':couple_ww:', 'valentine', 'valentines')
CROSSES = ('x', ':x:', ':heavy_multiplication_x:', ':regional_indicator_x:', ':negative_squared_cross_mark:',
           ':broken_heart:', 'rejection', 'rejections')
RINGS = ('o', ':o:', ':regional_indicator_o:', ':zero:', ':ring:', 'proposal', 'proposals')
SKULLS = ('skull', 'death', ':skull:', ':skull_crossbones:', ':knife:', ':dagger:', 'assassination', 'assassinations')

players = []
mailbox = []

client = discord.Client()

def server_instance(input_list, server_id):
    # this function's used to ensure that whenever you message a server,
    # it has both an assigned player list and an assigned mailbox
    found_server = False
    for i in range(len(input_list)):
        if input_list[i][0] == server_id and not found_server:
            found_server = True
    if not found_server:
        input_list.append([server_id])
    return input_list

def clear_server_info(input_list, server_id):
    # deletes the info stored in a server's unique sublist, but doesn't delete its tag
    for i in range(len(input_list)):
        if input_list[i][0] == str(server_id):
            del input_list[i][1:]
    return input_list

def flatten_list(list):
    # this is cuz i got lazy and didn't want to muck up the #send function even more
    # it lets us verify that the get_pair() function is actually going to find something when it goes digging
    newlist = []
    for i in range(len(list)):
        for o in range(len(list[i])):
            for u in range(len(list[i][o])):
                newlist.append(list[i][o][u])
    return newlist

def get_pair(item, input_list, server_id):
    # makes sure that whether the user is inputting a player's username or title the system returns both
    for i in range(len(input_list)):
        if input_list[i][0] == str(server_id):
            for o in range(len(input_list[i]) - 1):
                if item in input_list[i][o + 1]:
                    return input_list[i][o + 1][0], input_list[i][o + 1][1]


@client.event
async def on_message(message):
    # i don't want to listen to myself speak all day
    if message.author == client.user:
        return

    # ah, a message! i wonder what it says...
    if message.content.startswith('#') or isinstance(message.channel, discord.DMChannel):
        
        # need to keep all the paperwork tidy and responses consistent
        global players
        global mailbox
        
        # these make the rest of the code a little more legible
        channel = message.channel
        if not isinstance(message.channel, discord.DMChannel):
            guild_id = str(message.guild.id)
        
        # gotta clean up the input a bit for later stages
        command = message.content
        if command.startswith('#'):
            command = command[1:]
        command = command.strip()
        command = command.lower()
        command = command.split()
        
        # and lastly make sure the server has a dedicated player list and mailbox
        if not isinstance(message.channel, discord.DMChannel):
            players = server_instance(players, guild_id)
            mailbox = server_instance(mailbox, guild_id)
        
        if command[0] in SEND_COMMANDS:
            # put mail in the mailbox. [0] - send command, [1] - server id, [2] - first user, [3] - emote, [4] - second user
            if len(command) >= 4:
                valid_server = False
                for i in range(len(mailbox)):
                    if mailbox[i][0] == command[1]:
                        valid_server = True
                        if (command[3] in HEARTS or command[3] in CROSSES) and (len(command) >= 5):
                            if (command[2] in flatten_list(players) and (command[4] in flatten_list(players))):
                                to_name, to_title = get_pair(command[2], players, command[1])
                                from_name, from_title = get_pair(command[4], players, command[1])
                                if command[3] in HEARTS:
                                    msg = to_title.title() + " " + to_name.title() + " receives :heart: from " + from_title.title() + " " + from_name.title()
                                    mailbox[i].append(msg)
                                    await channel.send("Message confirmed.\n(" + msg + ")")
                                    
                                elif command[3] in CROSSES:
                                    msg = to_title.title() + " " + to_name.title() + " receives :x: from " + from_title.title() + " " + from_name.title()
                                    mailbox[i].append(msg)
                                    await channel.send("Message confirmed.\n(" + msg + ")")
                                    
                                else:
                                    await channel.send("Incorrect syntax. Use `# send [server id] [recipient] [emote] [sender]` "
                                                       "(though you can ignore the sender field if giving a proposal or assassination, "
                                                       "or simply wish to remain anonymous!)")
                            else:
                                await channel.send("Player name not recognized. Try using `# list` to find them, or `# assign`"
                                                   " if they don't have a character yet.")
                        
                        elif (command[3] in HEARTS or command[3] in CROSSES):
                            # if there's no sender field, the message is anonymous
                            if (command[2] in flatten_list(players)):
                                to_name, to_title = get_pair(command[2], players, command[1])
                                if command[3] in HEARTS:
                                    msg = to_title.title() + " " + to_name.title() + " receives :heart: from a mysterious benefactor."
                                    mailbox[i].append(msg)
                                    await channel.send("Message confirmed.\n(" + msg + ")")
                                    
                                elif command[3] in CROSSES:
                                    msg = to_title.title() + " " + to_name.title() + " receives :x: from a mysterious rival."
                                    mailbox[i].append(msg)
                                    await channel.send("Message confirmed.\n(" + msg + ")")
                                    
                                else:
                                    await channel.send("Incorrect syntax. Use `# send [server id] [recipient] [emote] [sender]` "
                                                       "(though you can ignore the sender field if giving a proposal or assassination, "
                                                       "or simply wish to remain anonymous!)")
                                
                            else:
                                await channel.send("Player name not recognized. Try using `# list` to find them, or `# assign`"
                                                   " if they don't have a character yet.")
                                
                        elif (command[3] in RINGS or command[3] in SKULLS):
                            if (command[2] in flatten_list(players)):
                                to_name, to_title = get_pair(command[2], players, command[1])
                                if command[3] in RINGS:
                                    msg = to_title.title() + " " + to_name.title() + " receives :ring: from " + message.author.name
                                    mailbox[i].append(msg)
                                    await channel.send("Message confirmed.\n(" + msg + ")")
                                    
                                elif command[3] in SKULLS:
                                    msg = to_title.title() + " " + to_name.title() + " receives :skull:"
                                    mailbox[i].append(msg)
                                    await channel.send("Message confirmed.\n(" + msg + ")")
                                    
                                else:
                                    await channel.send("Incorrect syntax. Use `# send [server id] [recipient] [emote] [sender]` "
                                                       "(though you can ignore the sender field if giving a proposal or assassination, "
                                                       "or simply wish to remain anonymous!)")
                                
                            else:
                                await channel.send("Player name not recognized. Try using `# list` to find them, or `# assign`"
                                                   " if they don't have a character yet.")
                        
                        else:
                            await channel.send("Incorrect syntax. Use `# send [server id] [recipient] [emote] [sender]` "
                                               "(though you can ignore the sender field if giving a proposal or assassination, "
                                               "or simply wish to remain anonymous!)")
                
                if not valid_server:
                    await channel.send("Could not find server. Remember to use `# send [server id] [recipient] [emote] [sender]`,"
                                       " and the server ID can be found by using `# help` on that server.")
            
            else:
                await channel.send("Incorrect syntax. Use `# send [server id] [recipient] [emote] [sender]` "
                                   "(though you can ignore the sender field if giving a proposal or assassination, "
                                   "or simply wish to remain anonymous!)")
            
        elif command[0] in MAIL_COMMANDS and not isinstance(message.channel, discord.DMChannel):
            # open or clear the mailbox
            if len(command) > 1 and command[1] == 'clear':
                # clear
                mailbox = clear_server_info(mailbox, guild_id)
                await channel.send("Mailbox cleared.")
                
            else:
                # open server mailbox publicly
                msg = ""
                letters = 0
                for i in range(len(mailbox)):
                    if mailbox[i][0] == guild_id:
                        msg = "**Mailbox Contents**:"
                        mailbox[i].sort()
                        for o in range(len(mailbox[i]) - 1):
                            if (o != len(mailbox[i]) - 1) and (len(msg + str(mailbox[i][o + 1])) >= 2000):
                                await channel.send(msg)
                                msg = ""
                                msg += str(mailbox[i][o + 1])
                                letters += 1
                            else:
                                msg += "\n" + str(mailbox[i][o + 1])
                                letters += 1
                        mailbox = clear_server_info(mailbox, guild_id)
                        
                if letters > 0:
                    await channel.send(msg)
                else:
                    await channel.send("Mailbox is currently empty.")
                
        elif command[0] in ASGN_COMMANDS and not isinstance(message.channel, discord.DMChannel):
            # assign roles to players on a server
            
            if command[2] in ARCHETYPES:
                searching = True
                for i in range(len(players)):
                    if players[i][0] == guild_id and searching:
                        if not any(command[2] in x for x in players[i]):
                            players[i].append([command[1], command[2]])
                            
                        else:
                            for x in range(len(players[i])):
                                if command[2] in players[i][x]:
                                    players[i][x][0] = command[1]
                        
                        searching = False
                        # ensures that even if the server tag is mistakenly doubled up, the player assignments won't be
                        
                await channel.send(command[1].title() + " assigned to " + command[2].title())
            else:
                msg = "Sorry, I don't recognize \"" + command[2] + "\" as a role. The valid roles are "
                for i in range(len(ARCHETYPES)):
                    if i == len(ARCHETYPES) - 1:
                        msg += "and " + ARCHETYPES[i].title() + "."
                    else:
                        msg += ARCHETYPES[i].title() + ", "
                await channel.send(msg)
            
        elif command[0] in LIST_COMMANDS and not isinstance(message.channel, discord.DMChannel):
            if len(command) > 1 and command[1] == 'clear':
                # clears the player list from the current server
                players = clear_server_info(players, guild_id)
                await channel.send("Player list cleared.")
            
            else:
                player_count = 0
                for i in range(len(players)):
                    if players[i][0] == guild_id:
                        msg = "**" + message.guild.name + " player list**:"
                        for o in range(len(players[i]) - 1):
                            msg += "\n" + str(players[i][o + 1][0]).title() + " as the " + str(players[i][o + 1][1]).title()
                            player_count += 1
                        msg += ("\n\nTo add a player, use `# assign [player] [role]`. To clear the list of players, use "
                               "`# list clear`.")
                
                if player_count > 0:
                    # send the server's user list
                    await channel.send(msg)
                    
                else:
                    # if there wasn't a list for the server, it's a no go
                    await channel.send("No players currently on this server.")
        
        elif command[0] in FLIP_COMMANDS:
            # coin flip function for the whispers game
            coin = random.randint(0, 1)
            
            if coin == 0:
                await channel.send("Tails. The question is revealed.")
                
            elif coin == 1:
                await channel.send("Heads. Secrets are kept.")
                
            else:
                # landed on its edge...?
                await channel.send("Uhh, that's not supposed to happen.")
        
        elif command[0] in HELP_COMMANDS:
            # help! i need somebody! help! not just anybody!
            if isinstance(message.channel, discord.DMChannel):
                await channel.send("**HELP**\n`Cont.exe` is a bot designed to help run online games of Jay Dragon's excellent "
                                   "post-apoc pop punk political dating sim Flower Court (jdragsky.itch.io/flower-court). It keeps track of players "
                                   "in the game, keeps server-specific mailboxes until it's time to open them, and has a coin flip "
                                   "function for use in the Whispers Game. It was programmed and maintained by Rathayibacter. Hit "
                                   "me up on twitter if you have any issues."
                                   "\n\n**COMMANDS**"
                                   "\n`# send [server code] [recipient] [emote] (sender)` - Put a valentine (`<3`), rejection (`x`), "
                                   "proposal (`o`) or assassination (`skull`) in the server's mailbox. `(sender)` is optional, and "
                                   "should be left off if you want to send your message anonymously. Please note that at least one "
                                   "player has to be assigned on a server in order for this function to be able to send that server "
                                   "mail."
                                   "\n`# flip` - Flip a coin."
                                   "\n`# help` - Uh, this. Right now."
                                   "\nThe `# assign`, `# list` and `# mailbox` commands only function on a server.")
                # dms need a unique help page since they don't have a server code and not all functions work in them
                
            else:
                await channel.send("**HELP**\n`Cont.exe` is a bot designed to help run online games of Jay Dragon's excellent "
                                   "post-apoc pop punk political dating sim Flower Court (jdragsky.itch.io/flower-court). "
                                   "It keeps track of players in the game, allows for anonymous mail to be DM'd to server-specific "
                                   "mailboxes and kept hidden until it's time to reveal them, and has a coin flip function for use "
                                   "in the Whispers Game. It was programmed and maintained by Rathayibacter. Hit me up on twitter "
                                   "if you have any issues."
                                   "\n> Server code: " + guild_id + "\n\n**COMMANDS**"
                                   "\n`# assign [name] [role]` - Associate a player's name with their in-game role."
                                   "\n`# list (clear)` - Lists all assigned players, or use `(clear)` to unassign all players."
                                   "\n`# mailbox (clear)` - Opens the server's mailbox, or use `(clear)` to delete the contents "
                                   "without revealing them."
                                   "\n`# send [server code] [recipient] [emote] (sender)` - Put a valentine (`<3`), rejection (`x`), "
                                   "proposal (`o`) or assassination (`skull`) in the server's mailbox. `(sender)` is optional, and "
                                   "should be left off if you want to send your message anonymously."
                                   "\n`# flip` - Flip a coin."
                                   "\n`# help` - Uh, this. Right now.")
        
        elif command[0] in MAIL_COMMANDS or command[0] in ASGN_COMMANDS or command[0] in LIST_COMMANDS:
            await channel.send("Sorry, I can't perform that action in a DM.")
        
        else:
            # if user gives weird input, we help usher them along but don't spam them with the huge help message right away
            await channel.send("Confused? Try `# help`!")

@client.event
async def on_ready():
    print('Logged in as\n' + client.user.name + '\n' + str(client.user.id) + '\n' + '------')

client.run(TOKEN)
