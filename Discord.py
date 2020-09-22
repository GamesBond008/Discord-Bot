from discord.ext import commands 
import discord
import asyncio
import os
import Downloader as down
temp=False
play_order=[]
CHANNEL=None
CHECK=None
VOICE=None
commands_channel_name=''															#Put Your Commands Channel Name here
server_name=''																		#Put Your Server Name Here
path=''                      														#Insert The path where You want Your Audio File to be Put in
token=''																			#Insert Token of Your Bot Here
bot = commands.Bot(command_prefix='!')
guild=0
msg_count={}
embed=lambda title: discord.Embed(description=title,colour=16751530)

#Sending the message from bot in embeded (Bold) text

async def send(text):
	await main_channel.send(embed=embed(text))

#Detecting the bot is ready or not

@bot.event
async def on_ready():
	global guild,main_channel
	print('Logged in as: ',bot.user)
	for guild in bot.guilds:
		if(guild.name==server_name):									 #Detect the server 
			for channel in guild.channels:								 #Looping through all channels in server untill bot finds the channel in which you want bot to send message in specific channel
				if(channel.name==commands_channel_name):							 #Bot gives message only in 'commands' channel
					main_channel=channel 								 #Giving the bot text channel to send messages
					break
	await main_channel.send(embed=embed('Connected To The Server')) 	 #Bot sending message that he is online and ready to take commands from server

@bot.command(pass_context=True,help='Print\'s Out the latency of Bot To the Server.')
async def ping(ctx):
	await ctx.send(str(round(bot.latency*1000))+'ms')					 #Sends ping of the bot

@bot.command(pass_context=True,help='Give\'s Number of Members in Server(including BOTS).')
async def members(ctx):
	await ctx.send('Number of Members in This Server is: '+str(guild.member_count))

@bot.event
async def on_member_join(member):
	e=discord.Embed(title='Welcome '+member.display_name+' To the Server')
	await guild.system_channel.send(embed=embed(e))

@bot.command(pass_context=True,hidden=True)
async def send(ctx,name):
	member=guild.get_member_named(name)
	await member.send('Nice')

@bot.event
async def on_member_update(before,after):
	if(after.bot):
		return
	if(after.status!=before.status):
		e=discord.Embed(title=after.display_name+' is '+str(after.status))
		await main_channel.send(embed=e)

@bot.command(pass_context=True,help='Gives Count of Number of messages each User did(Excluding Bots).')
async def count(ctx):
	s=''
	for i in msg_count:
		s+='\n'+i+' : '+str(msg_count[i])
	await ctx.send(s)

@bot.command(pass_context=True,aliases=['j'],help='Join\'s The Voice Channel The user\'s Currently in.')
async def join(ctx):
	global CHANNEL,VOICE
	try:
		CHANNEL=ctx.message.author.voice.channel
		VOICE= await CHANNEL.connect()
		await ctx.send(embed=embed('Connected To the '+CHANNEL.name+' Voice Channel '+ctx.message.author.mention))
	except Exception as e:
		print(e)
		await guild.system_channel.send(embed=embed('Can\'t Connect to the Voice Channel '+ctx.message.author.name))

@bot.command(pass_context=True,help='Skips to the Next Audio if any in queue')
async def skip(ctx):
	try:
		if(VOICE.is_playing() or VOICE.is_paused()):
			VOICE.stop()
			await main_channel.send(embed=embed('Skipped'))
	except:
		await main_channel.send(embed=embed('No Audio Is Playing At the moment.'))

@bot.command(pass_context=True,help='Stop the Audio Playing and Disconnects the bot.')
async def stop(ctx):
	global VOICE,play_order,CHECK
	try:
		if(VOICE.is_playing() or VOICE.is_paused()):
			CHECK=1
			VOICE.stop()
	except:
		await main_channel.send(embed=embed('Not Playing Any Audio'))

@bot.command(pass_context=True,help='Disconnects the Bot from the Voice Channel, if Connected to any.')
async def disconnect(ctx):
	global VOICE,play_order
	try:
		if(VOICE.is_playing() or VOICE.is_paused()):
			await VOICE.disconnect()
			for file in os.listdir(path):
				os.remove(path+file)
			play_order=[]
			VOICE=None
			await main_channel.send(embed=embed('Disconnected'))
		else:
			await VOICE.disconnect()
			await main_channel.send(embed=embed('Disconnected'))
	except:
		await main_channel.send(embed=embed('Not Connected to A Voice Channel'))

@bot.command(pass_context=True,help='Pause The Audio if any is Playing.')
async def pause(ctx):
	try:
		VOICE.pause()
		await main_channel.send(embed=embed('Paused'))
	except:
		await main_channel.send(embed=embed('The Bot isn\'t Connected/There\'s no Song Playing At The Moment.'))

@bot.command(pass_context=True,help='Resumes The Audio if any is playing.')
async def resume(ctx):
	try:
		VOICE.resume()
		await main_channel.send(embed=embed('Resumed'))
	except:
		await main_channel.send(embed=('The Bot isn\'t Connected/There\'s no Song Playing at The Moment.'))

@bot.command(pass_context=True,help='Play\'s The Audio/Playlist Url Given.',description='Put !play and then The URL of the song/Playlist Seperated By a Space(Currently Only Youtube URL\'s are Accepted)')
async def play(ctx,url):
	global VOICE,CHANNEL,play_order,temp
	if(VOICE==None):
		try:
			CHANNEL= ctx.message.author.voice.channel
			VOICE=await CHANNEL.connect()
		except Exception as e:
			print(e)
			await ctx.send(embed=embed('Can\'t Connect to the Channel @'+ctx.message.author.mention()))
			return
	if('list' in url.lower()):
		await ctx.send(embed=embed('Getting Everything Ready'))
		temp=down.downloader(url)
		await playlist_start()
		return
	elif(not play_order):
		await ctx.send(embed=embed('Getting Everything Ready'))
		play_order.append(down.downloader(url))
		await start(play_order[0])
		return
	play_order.append(down.downloader(url))

async def playlist_start():
	global temp
	try:
		for file_name in os.listdir(path):
			VOICE.play(discord.FFmpegPCMAudio(path+file_name))
			await main_channel.send(embed=embed('Playing '+file_name[:-4]))
			while(VOICE.is_playing() or VOICE.is_paused()):
				if False:
					pass
				await asyncio.sleep(1)
			else:
				await asyncio.sleep(1)
				await queue(file_name)
		if(len(os.listdir(path))==0):
			await VOICE.disconnect()
			await main_channel.send(embed=embed('Disconnected'))
			temp=False
	except Exception as e:
		await main_channel.send(embed=embed('Disconnected'))

async def start(title):
	title=title.replace('"',"'").replace('|','_').replace('/','').replace('?','').replace('\\','').replace('*','')
	try:
		for file_name in os.listdir(path):
			if(title in file_name):
				break
		await main_channel.send(embed=embed('Playing '+title))
		VOICE.play(discord.FFmpegPCMAudio(path+file_name))
		while (VOICE.is_playing() or VOICE.is_paused()):
			if False:
				continue
			await asyncio.sleep(1)
		else:
			await queue(file_name)
	except Exception as e:
		print(e)
		await main_channel.send(embed=embed("An Error Has Occured"))

async def queue(title):
	global play_order,VOICE,CHECK,temp
	if(CHECK!=1 and play_order):
		try:
			if(len(play_order)==1):
				os.remove(path+title)
				play_order.pop(0)
				await main_channel.send(embed=embed('Disconnected'))
				await VOICE.disconnect()
				VOICE=None
			else:
				os.remove(path+title)
				play_order.pop(0)
				await start(play_order[0])
		except Exception as e:
			print(e)
			await main_channel.send(embed=embed('An Error has Occured'))
	elif (temp!=False and CHECK!=1):
		os.remove(path+os.listdir(path)[0])
	else:
		CHECK=None
		for file in os.listdir(path):
			os.remove(path+file)
		play_order=[]
		await main_channel.send(embed=embed('Disconnecting'))
		await VOICE.disconnect()
		VOICE=None
		temp=False

@bot.command(pass_context=True,aliases=['69'],hidden=True)
async def Secret(ctx):
	await ctx.send('Nice')

@bot.event
async def on_message(message):
	if(not message.author.bot):
		global msg_count
		if(message.author.name not in msg_count):
			msg_count[message.author.name]=1
		else:
			msg_count[message.author.name]+=1
	await bot.process_commands(message)

bot.run(token)