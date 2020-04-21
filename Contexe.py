'''
Ayo, Rath here! Cont.exe is a bot designed for running Jay Dragon's Flower Court (https://jdragsky.itch.io/flower-court).

This is an updated version of the bot, with an improved assignment command that actually keeps track of users rather than
just pairing strings, much more efficient and readable handling of server data, and a new function for creating unique
ordered Whispers Game sequences, courtesy of MsPelligrino. Thanks again for the contribution! As always, if you have any
issues with the bot, you can hit me up on twitter at @Rathayibacter. Have fun!
'''

import discord, random, json

TOKEN = '[censored]'

ARCHETYPES = ('prinxarch', 'infante', 'doxe', 'contex', 'stranger', 'courtesan', 'cinderella', 'dignitary',
              'baronne', 'knight', 'dowager', 'tycoon')

SEND_COMMANDS = ('send', 'message', 'letter')
MAIL_COMMANDS = ('mail', 'mailbox', 'read')
ASGN_COMMANDS = ('assign', 'role', 'append')
LIST_COMMANDS = ('list', 'players')
DELT_COMMANDS = ('clear', 'delete', 'empty')
ORDR_COMMANDS = ('order', 'sequence', 'shuffle', 'pairing', 'pairings')
HDDN_COMMANDS = ('hidden', 'identity', 'identities', 'secret')
FLIP_COMMANDS = ('flip', 'coin', 'random')
DECK_COMMANDS = ('deck', 'cards', 'shuffle')
HELP_COMMANDS = ('help', 'what', 'huh', 'um')

HEARTS = ('heart', 'hearts', '<3', '❤', '❤️', '💙', '💚', '💜', '💛', 'valentine', 'valentines')
CROSSES = ('cross', 'crosses', 'x', '❌', '💔', 'rejection', 'rejections')
RINGS = ('ring', 'rings', 'o', '0', '⭕', '💍', 'proposal', 'proposals')
SKULLS = ('skull', 'skulls', 'death', '💀', '🔪', 'assassination', 'assassinations')

SUITS = ('Hearts', 'Spades', 'Diamonds', 'Clubs')
VALUES = ('King', 'Queen', 'Jack', 'Ten', 'Nine', 'Eight', 'Seven', 'Six', 'Five', 'Four', 'Three', 'Two', 'Ace')
                                                                                                           #000000 #A4A4A4 #FFFFFF #810081

serverdata = {}
client = discord.Client()


def get_user_id(info):
    # get a user's id from a variety of different identifiable characteristics
    for i in client.get_all_members():
        ids = [i.name.lower(), i.name.lower() + '#' + i.discriminator, '<@!' + str(i.id) + '>', str(i.id)]
        if info in ids:
            return (i.id)
        

def find_name_and_title(info, d):
    # grab a player's name and title from the server data
    if info in ARCHETYPES and info in list(d):
        title, name = info.title(), d[info]['name'].title()
        return (title, name)
    else:
        for key in d:
            if (info in d[key]['name'] or
                info in d[key]['nick'] or
                info in d[key]['@']):
                title, name = key.title(), d[key]['nick'].title()
                return (title, name)
    return False


def permute(l):
    return random.sample(l, len(l))


def add_next_player(unseen_pairs, partial_ordering):
    # Get the last person we chose
    prev = partial_ordering[-1]
    # Get a random ordering of everyone that cur hasn't asked yet
    possible = permute(unseen_pairs[prev]) #random.sample(unuseen_pairs[prev], len(unuseen_pairs[prev]))
    for p in possible:
        if not p in partial_ordering:
            partial_ordering.append(p)
            unseen_pairs[prev].remove(p)
            return True
    # It's possible that the current ordering is a dead-end and
    # there were no valid paths
    return False


def get_n_unique_orderings(nrounds, players):
    if (len(players) < 5):
        return False

    # Construct a map from every player to a list of every other player
    unseen_pairs = {}
    for p in players:
        unseen_pairs[p] = [p2 for p2 in players if not p2 == p]

    # Choose who asks the first question from this random list
    start_players = permute(players) #random.sample(players, len(players))
    cur_start = 0
    count = 0

    random_orderings = []

    for i in range(nrounds):
        # Retry until we've found a valid ordering.
        while True:
            random_ordering = start_players[cur_start:cur_start+1]
            while len(random_ordering) < len(players):
                if not add_next_player(unseen_pairs, random_ordering):
                    # Undo all the modifications we made to unseen_pairs
                    for i in range(len(random_ordering) - 1):
                        unseen_pairs[random_ordering[i]].append(random_ordering[i+1])

                    # If this ordering failed, restart with a new first player
                    cur_start = (cur_start + 1) % len(start_players)
                    count += 1
                    random_ordering = start_players[cur_start:cur_start+1]

                    if count > 100:
                        print("aborting bc we entered stuck state - probably there were less than 5 players")
                        return False

            if not random_ordering[0] in unseen_pairs[random_ordering[-1]]:
                #undo changes, retry
                for i in range(len(random_ordering) - 1):
                        unseen_pairs[random_ordering[i]].append(random_ordering[i+1])
                # If this ordering failed, restart with a new first player
                cur_start = (cur_start + 1) % len(start_players)
                count += 1
                continue

            # update relationship for last pair
            unseen_pairs[random_ordering[-1]].remove(random_ordering[0])
            break

        # Update start player so that we don't start with them again
        start_players.remove(random_ordering[0])

        # Slide along 1st player
        cur_start = (cur_start + 1) % len(start_players)

        random_orderings.append(random_ordering)

    return random_orderings


@client.event
async def on_message(message):
    # i don't want to listen to myself speak all day
    if message.author == client.user:
        return

    # ah, a message! i wonder what it says...
    if message.content.startswith('#') or isinstance(message.channel, discord.DMChannel):
        
        # need to keep all the paperwork tidy and responses consistent
        global serverdata
        
        # make the code more legible and ensure each server has an appropriate entry in the listing
        channel = message.channel
        if not isinstance(message.channel, discord.DMChannel):
            guild_id = str(message.guild.id)
            if guild_id not in serverdata:
                serverdata[guild_id] = [{}, [], [], False]
                # these are, in order: the dict of player roles and names, the mailbox, the list of
                # unused ordered pairs, and the boolean for whether the player list has changed since
                # the last set of ordered pairs was created
        
        # and clean up the input a bit for later stages
        command = message.content
        if command.startswith('#'):
            command = command[1:]
        command = command.strip()
        command = command.lower()
        command = command.split()
        
        # the real meat of the operation
        if command[0] in SEND_COMMANDS:
            # puts a message in a server's mailbox. syntax is #[server id] [recipient] [emote] (sender)
            
            if len(command) > 3:
                if command[1] in serverdata:
                    recipient = find_name_and_title(command[2], serverdata[command[1]][0])
                    
                    if recipient:
                        if command[3] in HEARTS + CROSSES:
                            if len(command) > 4:
                                sender = find_name_and_title(command[4], serverdata[command[1]][0])
                                
                                if sender and command[3] in HEARTS:
                                    serverdata[command[1]][1].append(recipient[0] + ' ' + recipient[1] +
                                                                     ' was sent a Valentine (:heart:) from ' +
                                                                     sender[0] + ' ' + sender[1] + '.')
                                    await channel.send("Message sent.")
                                    
                                elif sender:
                                    serverdata[command[1]][1].append(recipient[0] + ' ' + recipient[1] +
                                                                     ' was sent a Rejection (:x:) from ' +
                                                                     sender[0] + ' ' + sender[1] + '.')
                                    await channel.send("Message sent.")
                                    
                                else:
                                    # if the player put something in the sender field that wasn't found,
                                    # we want to make sure they know a mistake was made
                                    await channel.send("Second user not found.")
                            else:
                                # if the player didn't put a name in, the message is sent anonymously
                                if command[3] in HEARTS: 
                                    serverdata[command[1]][1].append(recipient[0] + ' ' + recipient[1] +
                                                                     ' was sent a Valentine (:heart:) ' +
                                                                     'from an anonymous admirer.')
                                    await channel.send("Message sent.")
                                    
                                else:
                                    serverdata[command[1]][1].append(recipient[0] + ' ' + recipient[1] +
                                                                     ' was sent a Rejection (:x:) from ' +
                                                                     'an anonymous opponent.')
                                    await channel.send("Message sent.")
                            
                        elif command[3] in RINGS + SKULLS:
                            # the last round behaves differently, and we no longer need player input for the sender
                            sender = find_name_and_title(message.author.name.lower(), serverdata[command[1]][0])
                            
                            if sender and command[3] in RINGS:
                                serverdata[command[1]][1].append(recipient[0] + ' ' + recipient[1] +
                                                                 ' was sent a Proposal (:ring:) from '
                                                                 + sender[0] + ' ' + sender[1] + '.')
                                await channel.send("Message sent.")
                                
                            elif sender:
                                serverdata[command[1]][1].append(recipient[0] + ' ' + recipient[1] +
                                                                 ' was sent an Assassination (:skull:).')
                                await channel.send("Message sent.")
                                
                            else:
                                # i don't anticipate this'll happen often, but it's good to have
                                await channel.send("It looks like you're not in this game. Use `#assign`" +
                                                   "on the server your game is hosted on to join.")
                        else:
                            # had issues in the past with emotes, the bot should be better about that now
                            await channel.send("Emote not found. The four kinds of emotes used in this game " +
                                               "are Hearts (:heart:), Crosses (:x:), Rings (:o:), and Skulls (:skull:). " +
                                               "You can also refer to them by name, or as valentines, rejections, "+
                                               "proposals and assassinations if you'd prefer.")
                    else:
                        await channel.send("First user not found.")
                else:
                    await channel.send("Server not found. Use `# list` or `# help` on the host server to get its unique ID.")
        
        
        elif command[0] in MAIL_COMMANDS:
            # releases the server's mailbox, or clears it without revealing its contents
            if not isinstance(message.channel, discord.DMChannel):
                if len(command) > 1 and command[1] in DELT_COMMANDS:
                    # clears the mailbox without opening it
                    serverdata[guild_id][1] = []
                    await channel.send("Mailbox cleared.")
                    
                else:
                    # copy the mailbox over, sort it by recipient, and get started!
                    mailbox = serverdata[guild_id][1].copy()
                    mailbox.sort()
                    serverdata[guild_id][1] = []
                    msg = "**Mailbox Contents**:"
                    letters = 0
                    
                    for letter in mailbox:
                        if (len(msg + letter) >= 2000):
                            # make sure we don't hit the discord message limit. fool me once!
                            await channel.send(msg)
                            msg = letter
                            letters += 1
                        else:
                            msg += "\n" + letter
                            letters += 1
                    
                    # make sure we're not just sending an empty list
                    if letters > 0:
                        await channel.send(msg)
                    else:
                        await channel.send("Mailbox is currently empty.")
            else:
                await channel.send("Sorry, this command isn't available in DMs.")
        
        
        elif command[0] in ASGN_COMMANDS:
            # assign game role to a user. syntax is "#assign [role] (user)"
            if not isinstance(message.channel, discord.DMChannel):
                if len(command) > 1 and command[1] in ARCHETYPES:
                    if len(command) == 2:
                        # if the user doesn't put a name in, it defaults to assigning them
                        player = message.author
                    else:
                        player = message.guild.get_member(get_user_id(command[2]))
                        
                    if player:
                        # make sure we actually got something earlier
                        player_tag = player.name + '#' + player.discriminator
                        
                        # what does the player want us to call them?
                        if player.nick:
                            player_nick = player.nick.lower()
                        else:
                            player_nick = player.name.lower()
                        
                        # no doubles!
                        for key in list(serverdata[guild_id][0]):
                            if player.id == serverdata[guild_id][0][key]['id']:
                                del serverdata[guild_id][0][key]
                        
                        # assigns the role, which also eliminates any previous data in that role
                        serverdata[guild_id][0][command[1]] = {'name': player.name.lower(),
                                                               'nick': player_nick,
                                                               '@': '<@!' + str(player.id) + '>',
                                                               'id': player.id}
                        
                        serverdata[guild_id][3] = True
                        await channel.send(player_nick.title() + " is now the " + command[1].title() + ".")
                        
                    else:
                        await channel.send("User not recognized. Please use their full username or their mention (`@User`).")
                        
                elif len(command) > 1:
                    await channel.send("Role not recognized. Use `# list roles` to see all available roles.")
                    
                else:
                    await channel.send("Syntax error. Please format as `#assign [role] (user)`. `user` is optional, " +
                                       "and defaults to yourself.")
            
            else:
                await channel.send("Sorry, this command isn't available in DMs.")

            
        elif command[0] in LIST_COMMANDS:
            if not isinstance(message.channel, discord.DMChannel):
                if len(command) > 1 and command[1] in DELT_COMMANDS:
                    # clears the list, useful for ending the game
                    for key in list(serverdata[guild_id][0]):
                        del serverdata[guild_id][0][key]
                    await channel.send("Player list cleared.")
                    
                else:
                    if len(serverdata[guild_id][0]) > 0:
                        msg = "**Players on this server**:\n"
                        for key in serverdata[guild_id][0]:
                            msg += serverdata[guild_id][0][key]['nick'].title() + " as the " + key.title() + '\n'
                        
                        # i wanted to make sure there's an easier way to get the server ID than #help, so i added it here too
                        msg += "\nServer ID: " + guild_id
                        await channel.send(msg)
                        
                    else:
                        await channel.send("Currently no players on this server. Use `# assign` to add them!")
            else:
                await channel.send("Sorry, this command isn't available in DMs.")
                
                
        elif command[0] in DELT_COMMANDS:
            if not isinstance(message.channel, discord.DMChannel):
                if len(command) > 1:
                    if command[1] in LIST_COMMANDS:
                        # clears the player list for the server
                        for key in list(serverdata[guild_id][0]):
                            del serverdata[guild_id][0][key]
                        serverdata[guild_id][3] = True
                        await channel.send("Player list cleared.")
                        
                    elif command[1] in MAIL_COMMANDS:
                        # empties the mailbox without opening it
                        serverdata[guild_id][1] = []
                        await channel.send("Mailbox cleared.")
                        
                    elif command[1] in ARCHETYPES and command[1] in serverdata[guild_id][0].keys():
                        # deletes an assigned role without requiring the players to clear all roles
                        del serverdata[guild_id][0][command[1]]
                        serverdata[guild_id][3] = True
                        await channel.send("Role cleared.")
                    
                    else:
                        msg = ("Syntax error. Use `# clear [list/mailbox]` to clear the server's player list or " +
                               "mailbox, or `# clear [role]` to unassign a role without replacing it.")
                        await channel.send(msg)
                else:
                    await channel.send("Use this command to clear the server's player list or mailbox.")
            else:
                await channel.send("Sorry, this command isn't available in DMs.")
            
            
        elif command[0] in ORDR_COMMANDS:
            if not isinstance(message.channel, discord.DMChannel):
                if len(serverdata[guild_id][2]) == 0 or serverdata[guild_id][3] == True:
                    # makes sure to only repopulate if the list is empty or the player list changed
                    serverdata[guild_id][3] = False
                    serverdata[guild_id][2] = []
                    
                    # get a list of player tuples to put into the sorting algorithm
                    playerlist = []
                    for key in serverdata[guild_id][0]:
                        playerlist.append((key.title(), serverdata[guild_id][0][key]['nick'].title()))
                    
                    # perform magic on them
                    whisperlist = get_n_unique_orderings(3, playerlist)
                    
                    if whisperlist:
                        # make sure we got a list as output, indicating the magic was successful
                        for i in whisperlist:
                            # add each of the three orderings to the serverdata for later use
                            serverdata[guild_id][2].append(i)
                
                if len(serverdata[guild_id][2]) > 0:
                    # if there's at least one ordered pairing
                    msg = ""
                    order = serverdata[guild_id][2].pop(0)
                    
                    for i in order:
                        # organize them for easy readability
                        msg += i[0] + " " + i[1] + " > "
                        
                    # ouroboros eats its own tail
                    msg += order[0][0] + " " + order[0][1]
                    await channel.send(msg)
                    
                else:
                    # something went wrong, and we can't make a set of three lists. this is probably due to
                    # low player counts. totally fine though, we'll just output a random list instead.
                    playerlist = []
                    for key in serverdata[guild_id][0]:
                        playerlist.append((key.title(), serverdata[guild_id][0][key]['nick'].title()))
                    
                    random.shuffle(playerlist)
                    msg = ""
                    
                    for i in playerlist:
                        msg += i[0] + " " + i[1] + " > "
                    msg += playerlist[0][0] + " " + playerlist[0][1]
                    await channel.send(msg)
                    
            else:
                await channel.send("Sorry, this command isn't available in DMs.")
            
            
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
            msg = ("Cont.exe is a bot designed to help run online games of Jay Dragon's excellent post-apoc " +
                   "pop punk political dating sim Flower Court (jdragsky.itch.io/flower-court). It was primarily " +
                   "written by Rathayibacter, with the help of MsPelligrino who contributed the `# order` function." +
                   "Thank you again!\nIf you have any issues, don't hesitate to contact me on twitter at " +
                   "@Rathayibacter.\n\n**COMMANDS**" +
                   "\n`# assign` - Assigns a role to a player. Syntax is `# assign [role] (player)`, leaving the " +
                   "`(player)` field empty if you're assigning yourself."
                   "\n`# list` - Shows all assigned players on the current server. Can also be used to clear all " +
                   "assignments with `# list clear`." +
                   "\n`# send` - Anonymously send mail to the server, which can then be opened later using the " +
                   "`# mailbox` command. Syntax is `# send [server ID] [recipient] [emote] (sender)`, leaving the " +
                   "`(sender)` field empty if you're sending it anonymously. Make sure to DM the bot this command to " +
                   "keep it hidden from the other players, and remember that you can claim to be sending mail from any " +
                   "player on the server!" +
                   "\n`# mailbox` - Opens the server-wide mailbox, so everyone can see who's been getting mail from whom. " +
                   "Can also be used to clear the mailbox without revealing its contents with `# mailbox clear` in case a " +
                   "mistake was made during the sending." +
                   "\n`# order` - Gives a randomized ordered sequence of players for use in the Whispers game. When " +
                   "possible, avoids giving any pair of players in the same order- in other words, you should be asking a " +
                   "question to someone new in each of the three rounds! " +
                   "\n`# flip` - Flips a coin, for use in the Whispers game." +
                   "\n`# help` - This, right here.\n\n")
            
            if not isinstance(message.channel, discord.DMChannel):
                msg += "Server ID: " + guild_id
                
            else:
                # just some helpful clarification for users DMing the bot
                msg += ("Please note that with the exception of `# send`, `# flip`, and `# help`, these commands don't " +
                        "function in direct messages. If you're having issues, this may be why. If you're looking for the " +
                        "server ID of the server you're playing on, use `# list` or `# help` on that server.")
                
            await channel.send(msg)
            
        else:
            await channel.send("Sorry, what was that? Try `# help` for more information, " + 
                               "or `# help me` to have the help message DM'd to you.")


@client.event
async def on_ready():
    print('Logged in as\n' + client.user.name + '\n' + str(client.user.id) + '\n' + '------')

client.run(TOKEN)
