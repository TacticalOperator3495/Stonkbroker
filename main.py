import discord
from discord.ext import commands
import os
from replit import db
import finnhub
import time
import requests
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
import random
import datetime

TEN = 600

@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=500, period=TEN)
def call_api(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    return response

APIKEY = os.environ['API_KEY']
finnhub_client = finnhub.Client(api_key=APIKEY)

TOKEN = os.environ['DISCORD_TOKEN']
keys = db.keys()

bot = commands.Bot(command_prefix='.', activity=discord.Activity(type=discord.ActivityType.watching, name='for .commands'), help_command = None)


try:
	@bot.event
	async def on_ready():
		print('Successfully logged into Discord.')
	
	
	#starts a user's profile and/or restarts a user's profile-$0 USD.
	@bot.command()
	async def start(ctx):
			db[f'@{ctx.author.id}_money'] = 0
			db[f'@{ctx.author.id}_bank'] = 0
			embed = discord.Embed(
	        title='**WELCOME**',
	        description=
	        'Welcome to Stonkbroker, the Discord game bot based off of the real life **stock market**. Experience ups :chart_with_upwards_trend:, downs :chart_with_downwards_trend:, financial issues :sob:, and economic success :money_mouth: :moneybag:!',
					color=0xAA28FF
	)
			await ctx.reply(embed=embed)
	
	
	
	
	#shows the user a list of commands
	@bot.command()
	async def commands(ctx):
	    embed = discord.Embed(
	        title='**COMMANDS LIST**',
	        description=
	        "Here is the complete list of Stonkbroker's current commands (in alphabetical order).\n **.addshop <shop name> ** - With the required arguments, this command allows you to open up your shop.\n **.bank** - This command allows you to see how much money you have deposited in your own personal bank!\n **.commands** - Opens up a list of all the commands in the game bot.\n **.daily** - This command allows you to claim your daily cash amount that gets directly placed in your own personal wallet!\n **.deposit <cash amount>** - Deposits the money from your wallet into your safe bank!\n **.gamble <cash amount>** -Gamble a certain cash amount for a 1/21 chance to win!\n **.give <@mention user> <item>** - Allows you to give another user an item!\n **.invest** - Shows the list of possible investments to invest in.\n **.investin <company> <number of shares>** - This allows you to buy shares and own a part of the company!\n **.investments** - Shows you the shares you own in all available company stock. \n **.items** - Displays the items you have that were given to you by another user.\n **.pay <@mention user> <amount>** - Allows you to pay another user. \n **.payshop <shop name> <amount>** -  Allows you to pay a shop's owners a certain amount. This amount is then divided among the number of owners.\n **.priceof <company>** - Shows you the price of a share of a company.\n **.sellstock <company> <shares>** - Allows to sell a certain number of shares within a company.  \n**.start** - Starts a new profile in Stonkbroker.\n **.wallet** - Displays the amount of cash in your wallet.\n **.withdraw** - Allows you to withdraw money from your bank and into your wallet to spend or pay.",
	        color=0xAA28FF)
	    await ctx.reply(embed=embed)
	
	
	
	
	#allows the user to claim their daily cash amount
	@bot.command()
	async def daily(ctx):
			keys = db.keys()
			if f'{ctx.author.id}_daily_cooldown' not in keys:
						db[f'{ctx.author.id}_daily_cooldown'] = 0
			player_time_daily = db[f'{ctx.author.id}_daily_cooldown']
			if time.time() - player_time_daily > 86400:
				money = db[f'@{ctx.author.id}_money']
				money += 100
				db[f'@{ctx.author.id}_money'] = money
				db[f'@{ctx.author.id}_daily'] = 'claimed'
				db[f'{ctx.author.id}_daily_cooldown'] = time.time()
				embed = discord.Embed(title="**DAILY CLAIMED**", description = "You have successfully claimed today's daily 100 USD. :city_sunset:", color =0xAA28FF)
				await ctx.reply(embed=embed)
			else:
				embed = discord.Embed(title="**DAILY ALREADY CLAIMED**", description = "You have already claimed a daily within the last 24 hours. Please come back later when the 24 hours is over to claim your next daily! :city_sunset:", color =0xAA28FF)
				await ctx.reply(embed=embed)
	#allows the user to send another user a certain amount of cash.
	@bot.command()
	async def pay(ctx, member: discord.Member, arg2):
			cash_to_send = int(arg2)
			if ctx.author.id != member.id:
				if cash_to_send>0:
					cash_reciever_current_cash = db[f'@{member.id}_money']
					print(member.id)
					new_cash = cash_reciever_current_cash + cash_to_send
					print(cash_reciever_current_cash)
					print(cash_to_send)
					db[f'{member.id}_money'] = new_cash
					money_deductable = db[f'@{ctx.author.id}_money']
					new_money = money_deductable - cash_to_send
					db[f'@{member.id}_money'] = new_cash
				if new_money < 0:
						cash_reciever_current_cash -= cash_to_send
						db[f'@{member.id}_money'] = cash_reciever_current_cash
						db[f'@{ctx.author.id}_money'] = (money_deductable + cash_to_send)
						embed = discord.Embed(title="**INSUFFICIENT FUNDS**", description = "You don't have enough money to do this! :no_entry_sign: :dollar:", color=0xAA28FF)
						await ctx.reply(embed=embed)
				elif new_money >= 0:
					db[f'@{ctx.author.id}_money'] = new_money
					embed = discord.Embed(
						title="***MONEY SENT***",
						description=f'**You, {ctx.author}, sent {cash_to_send} USD to {member.mention}!**',
						color=0xAA28FF)
					await ctx.reply(embed=embed)
				if cash_to_send<=0:
					embed = discord.Embed(title="**INSUFFICIENT FUNDS**", description="You cannot give negative money or 0 money! :no_entry_sign: :dollar:", color=0xAA28FF)
					await ctx.reply(embed=embed)
				else:
					embed = discord.Embed(title="**ERROR**", description="YOU CANNOT GIVE YOURSELF MONEY *dupers*! :no_entry_sign: :dollar:", color=0xAA28FF)
					await ctx.reply(embed=embed)
		
	
	
	#display's the user's balance.
	@bot.command()
	async def wallet(ctx):
	    big_boi_cash = db[f'@{ctx.author.id}_money']
	    embed = discord.Embed(title="**WALLET**",
	                          description=f'You have **${big_boi_cash} USD** :dollar: in your wallet!',
	                          color=0xAA28FF)
	    await ctx.reply(embed=embed)
	
	
	
	
	#allows the user to pay someone else's shop.
	@bot.command()
	async def payshop(ctx, arg1, arg2):
				keys = db.keys()
				if arg1 not in keys:
					embed = discord.Embed(
						title='**OOPSIES**',
	          description='That shop does not exist :no_entry_sign:',
	        	color=0xAA28FF
					)
					await ctx.reply(embed=embed)
				if arg1 in keys:
					shoop = db[f'{arg1}']
					shooplen = len(shoop)
					intarg2 = int(arg2)
					payxyz = intarg2 / shooplen
					paydue = int(payxyz)
					print(paydue)
					print(intarg2)
					print(shooplen)
					print(shoop)
					while shooplen > 0:
							payto = shoop[shooplen-1]
							cashmoney = db[f'{payto}_money']
							cashmoney += paydue
							print(cashmoney)
							db[f'{payto}_money'] = cashmoney
							shooplen -= 1
					if shooplen < 1:
							cashboi = db[f'@{ctx.author.id}_money']
							cashboi -= intarg2
							print(cashboi)
							print(intarg2)
							if cashboi<0:
								cashboi+= intarg2
								db[f'@{ctx.author.id}_money'] = cashboi
								embed = discord.Embed(
	                title='**INSUFFIECENT**',
	                description=f"You don't have enough money to do that!",
	                color=0xAA28FF
								)
								await ctx.reply(embed=embed)
							elif cashboi>=0:
								db[f'@{ctx.author.id}_money'] = cashboi
									
								embed = discord.Embed(
		                title='**PAID**',
		                description=
		                f'You paid the owners of {arg1} **${arg2} USD** for their services!',
		                color=0xAA28FF)
								await ctx.reply(embed=embed)
	
	@bot.command()
	async def gamble(ctx,arg1):
		playerbal = db[f'@{ctx.author.id}_money']
		embed=discord.Embed(title="**GAMBLE**", description= ":game_die: You have started a gambling session with the Python module Random. To win, you have to get a 4 that is randomly generated by Random, which will generate a random number from 1 to 5. :game_die:", color=0xAA28FF
		)
		await ctx.reply(embed=embed)
		list = [
			'one',
			'one',
			'one',
			'one',
			'one',
			'one',
			'two',
			'two',
			'two',
			'two',
			'three',
			'three',
			'three',
			'four',
			'five',
			'five',
			'five',
			'five',
			'five',
			'five',
			'five'
		]
		randomint=random.choice(list)
		if randomint == 'four' and int(arg1) > 0 and int(arg1) <= db[f'@{ctx.author.id}_money']:
			embed = discord.Embed(title="**YOU WON**", description = "You won the gamble. Please check your wallet for the balance that you won. :moneybag:", color=0xAA28FF)  
			await ctx.reply(embed=embed)
			newwalletbal1 = db[f'@{ctx.author.id}_money'] + int({arg1}*2)
			db[f'@{ctx.author.id}_money'] = newwalletbal1
		elif randomint != 'four' and int(arg1) > 0 and int(arg1) <= db[f'@{ctx.author.id}_money']:
			embed=discord.Embed(title="**YOU LOST**", description = "You lost the gamble. Please check your wallet for the balance that you lost. :no_entry_sign:", color=0xAA28FF)
			await ctx.reply(embed=embed)
			newwalletbal2 = playerbal - int(arg1)
			db[f'@{ctx.author.id}_money'] = newwalletbal2
		else:
			embed=discord.Embed(title="**INSUFFICIENT FUNDS**", description = "You cannot gamble more money than you have. Please enter a valid amount to gamble. :no_entry_sign: :sob:", color=0xAA28FF)
			await ctx.reply(embed=embed)
	
	
	
	#allows the user to add a shop.
	@bot.command()
	async def addshop(ctx, arg1):
			keys = db.keys()
			if arg1 not in keys:
				db[f'{arg1}'] = []
			shoppe = db[f'{arg1}']
			shoppe.append(f'@{ctx.author.id}')
			if 'shop' not in keys:
				db['shop'] = []
			sop = db[f'shop']
			print(sop)
			print(shoppe)
			if arg1 not in sop:
				sop.append(f'{arg1}')
			embed = discord.Embed(title='**SHOP CREATED**',
	                          description=f'You are the *owner* of **{arg1}** :shopping_cart:!',
	                          color=0xAA28FF)
			await ctx.reply(embed=embed)
	
	#allows the user to give another user some items.
	@bot.command()
	async def give(ctx, member: discord.Member, arg2):
		keys = db.keys()
		if 	f'@{member.id}_items' not in keys:
				db[f'@{member.id}_items'] = []
		items = db[f'@{member.id}_items']
		items.append(f'{arg2}')
		embed = discord.Embed(
			title=f'**GAVE ITEMS TO {member}**',
			description=f'You gave {member} {arg2} !',
			color=0xAA28FF
		)
		await ctx.reply(embed = embed)
	
	#shows the user's items.
	@bot.command()
	async def items(ctx):
		embed = discord.Embed(
			title='ITEMS THAT YOU OWN',
			description=db[f'@{ctx.author.id}_items'],
			color=0xAA28FF
		)
		await ctx.reply(embed = embed)
	
	#gives the user a list of jobs they can hold.
	@bot.command()
	async def jobs(ctx):
	    embed=discord.Embed(
				title="**JOBS**",
				description= "Below is the list of jobs that you can try to apply for. \n **Artist** - Create works of art to earn **$100 USD a day.**\n **Baker** - Create yummy pastries and breads to earn up to **$150 USD a day.**\n **Banker** - Keep a list of people's transactions to earn a whopping **$300 USD a day.**\n **Boba Seller** - Sell boba to earn **$50 USD a day.**\n **Book seller** - Sell books to earn **$60 USD a day.**\n **Gamer** - Be a professional gamer and play video games to earn **$500 USD a day.**\n **Math Tutor** - Teach people math to earn **$400 USD a day.**\n **President** - The highest possible job, lead your country and earn **$3,000 USD a day.**\n **Steak Seller** - Sell steak at your steak restaurant to earn", 
				color=0xAA28FF
			)
	    await ctx.reply(embed = embed)
	@bot.command()
	async def invest(ctx):
			aapl = finnhub_client.quote('AAPL')
			msft = finnhub_client.quote('MSFT')
			nvda = finnhub_client.quote('NVDA')
			intc = finnhub_client.quote("INTC")
			tsla = finnhub_client.quote("TSLA")
			now = datetime.datetime.now()
			if now.hour > 13:
				aaplstock = aapl['c']
				msftstock = msft['c']
				nvdastock = nvda['c']
				intcstock = intc['c']
				tslastock = tsla['c']
			if now.hour <= 13:
				aaplstock = aapl['o']
				msftstock = msft['o']
				nvdastock = nvda['o']
				intcstock = intc['o']
				tslastock = tsla['o']
			embed = discord.Embed(
	        title="**INVESTMENT LIST**",
	        description=
	        f"Here is the list of all possible investments (for a beginner with not much cash).\n **AAPL (Apple) - {aaplstock} USD (.investin aapl)**\n **MSFT(Microsoft) - {msftstock} USD (.investin msft)**\n **NVDA(Nvidia Corporation)-{nvdastock} USD (.investin nvda)**\n **INTC(Intel corporation) - {intcstock} USD (.investin intc)**\n **TSLA(Tesla motors) - {tslastock} USD  (.investin tsla)**\n",
	        color=0xAA28FF)
			await ctx.reply(embed=embed)
	
	@bot.command()
	async def investin(ctx, arg1, arg2):
			now = datetime.datetime.now()
			keys = db.keys()
			if f'{ctx.author.id}_stock_price' not in keys:
				db[f'{ctx.author.id}_stock_price'] = {}
			if f'{ctx.author.id}_stock_shares' not in keys:
				db[f'{ctx.author.id}_stock_shares'] = {}
			player_cash = db[f'@{ctx.author.id}_money']
			shares = int(arg2)
			stock_trans = finnhub_client.quote(f'{arg1.upper()}')
			if now.hour > 13:
				stock_price = stock_trans['c']
			if now.hour <= 13:
				stock_price = stock_trans['o']
			price_to_pay = shares * stock_price
			player_cash -= price_to_pay
			if player_cash < 0:
				embed = discord.Embed(
				title='**INSUFFICIENT FUNDS**',
				description=f"You don't have enough money to do that!",
				color=0xAA28FF
			)
				await ctx.reply(embed = embed)
			if player_cash >= 0:
				db[f'@{ctx.author.id}_money'] = player_cash
				stock_price_dict = db[f'{ctx.author.id}_stock_price']
				stock_shares_dict = db[f'{ctx.author.id}_stock_shares']
				stock_price_dict[f'{arg1}'] = stock_price
				print(stock_price_dict)
				print(stock_shares_dict)
				if f'{arg1}_shares' not in stock_shares_dict.keys():
					stock_shares_dict[f'{arg1}_shares'] = shares
				elif f'{arg1}_shares' in stock_shares_dict.keys():
					current_shares = stock_shares_dict[f'{arg1}_shares']
					new_shares = current_shares + shares
					stock_shares_dict[f'{arg1}_shares'] = new_shares
					print(stock_price_dict)
					print(stock_shares_dict)
				embed = discord.Embed(
					title='**STOCKS PURCHASED**',
					description=f'You purchased {arg2} share(s) of {arg1.upper()} stock at a rate of {stock_price} per share!',
					color=0xAA28FF
				)
				await ctx.reply(embed = embed)
	
	@bot.command()
	async def investments(ctx, arg1):
		stock_shares_dict = db[f'{ctx.author.id}_stock_shares']
		stock_price_dict = db[f'{ctx.author.id}_stock_price']
		if f'{arg1}' in stock_price_dict.keys():
			stock_shares = stock_shares_dict.get(f'{arg1}_shares')
			stock_price = stock_price_dict.get(f'{arg1}')
			embed = discord.Embed(
				title="INVESTMENTS",
				description=f"You own **{stock_shares} share(s)** of {arg1.upper()}, which you bought at a rate of **${stock_price} USD per share!**",
				color=0xAA28FF
			)
			await ctx.reply(embed = embed)
		elif arg1 == 'inDepth':
			stock_shares_dict = db[f'{ctx.author.id}_stock_shares']
			stock_price_dict = db[f'{ctx.author.id}_stock_price']
			embed = discord.Embed(
				title="INVESTMENTS IN DEPTH",
				description=f"Prices: {stock_price_dict}\n Shares: {stock_shares_dict}",
				color=0xAA28FF
			)
			await ctx.reply(embed = embed)			
		else:
			embed = discord.Embed(
				title="ERROR",
				description=f"You don't own that stock!",
				color=0xAA28FF
			)
			await ctx.reply(embed = embed)

	@bot.command()
	async def sellstock(ctx, arg1, arg2):
		now = datetime.datetime.now()
		stock_shares_dict = db[f'{ctx.author.id}_stock_shares']
		stock_price_dict = db[f'{ctx.author.id}_stock_price']
		if f'{arg1}_shares' in stock_shares_dict.keys():
			stock_shares = stock_shares_dict.get(f'{arg1}_shares')
			stock_trans = finnhub_client.quote(f"{arg1.upper()}")
			if now.hour < 13:
				stock_price = stock_trans['o']
			if now.hour >= 13:
				stock_price = stock_trans['c']
			player_cash = db[f'@{ctx.author.id}_money']
			if int(arg2) <= stock_shares and int(arg2) > 0:
				sold_cash = stock_price*int(arg2)
				newwalletbal = sold_cash + player_cash
				db[f'@{ctx.author.id}_money'] = newwalletbal
				new_stock_shares = stock_shares - int(arg2)
				stock_shares_dict[f'{arg1}_shares'] = new_stock_shares
				embed = discord.Embed(
					title = "**SHARES SOLD**", description = "You have successfully sold the amount of shares you wanted to sell. Please check your wallet for the cash that was placed there after the shares were sold.", color=0xAA28FF
				)
				await ctx.reply(embed=embed)
			elif stock_shares == 0:
				del stock_price_dict[f'{arg1}']
				embed = discord.Embed(
					title = "**SHARES SOLD**", description = "You have successfully sold the amount of shares you wanted to sell. Please check your wallet for the cash that was placed there after the shares were sold.", color=0xAA28FF
				)
				await ctx.reply(embed=embed)
			elif int(arg2) > stock_shares:
				embed = discord.Embed(
					title="**ERROR**",description="You can't sell more shares of this company than you actually own in this company. :no_entry_sign:", color=0xAA28FF
				)
				await ctx.reply(embed=embed)
		else:
			embed = discord.Embed(title="**ERROR**", description = "You don't actually own this stock. Please do .invest and .investin to own shares in a company. :no_entry_sign:", color=0xAA28FF										 
			)
			await ctx.reply(embed=embed)


			
	
	@bot.command()		
	async def deposit(ctx, arg1):
		global dudescash
		bank = db[f'@{ctx.author.id}_bank']
		try:
			intarg1 = int(arg1)
			if intarg1>-1:
				bank+=intarg1
				db[f'@{ctx.author.id}_bank'] = bank
				dudescash = db[f'@{ctx.author.id}_money']
				dudescash -= intarg1
			if dudescash<0:
				bank = db[f'@{ctx.author.id}_bank']
				bank -= intarg1
				db[f'@{ctx.author.id}_bank'] = bank
				embed = discord.Embed(
					title="**INSUFFICIENT FUNDS**",
					description="You don't have enough to do that. :no_entry_sign: :dollar:",
					color=0xAA28FF
				)
				await ctx.reply(embed = embed)

			elif intarg1<=0:
				embed = discord.Embed(
					title="**INSUFFICIENT FUNDS**",
					description=f"You cannot withdraw negative funds! :no_entry_sign: :dollar:",
					color=0xAA28FF
				)
				await ctx.reply(embed = embed)
			else:
				db[f'@{ctx.author.id}_money'] = dudescash
				embed = discord.Embed(
					title="**MONEY IN BANK**",
					description=f"You deposited **${arg1} USD.** :dollar:",
					color=0xAA28FF
				)
				await ctx.reply(embed=embed)
		except ValueError:
			arg1=str(arg1)
			if arg1 == 'all':
				dudescash1 = db[f'@{ctx.author.id}_money']
				db[f'@{ctx.author.id}_bank'] = dudescash1
				dudescash = dudescash1-dudescash1
				db[f'@{ctx.author.id}_money'] = dudescash
				embed = discord.Embed(
						title="**MONEY IN BANK**",
						description=f"You deposited **${dudescash1} USD.** :dollar:",
						color=0xAA28FF
					)
				await ctx.reply(embed = embed)
	#allows the user to 
	@bot.command()
	async def bank(ctx):
		cashmoney  = str(db[f'@{ctx.author.id}_bank'])
		embed = discord.Embed(
			title="**BANK**",
			description=f'You have **$' + cashmoney + ' USD** :dollar: in the bank :bank:!',
			color=0xAA28FF
		)
		await ctx.reply(embed=embed)
	
	#allows user to withdraw money from above bank
	@bot.command()
	async def withdraw(ctx, arg1):
		global dudescash
		bank = db[f'@{ctx.author.id}_bank']
		try:
			intarg1 = int(arg1)
			if intarg1>=0:
				bank-=intarg1
				db[f'@{ctx.author.id}_bank'] = bank
				dudescash = db[f'@{ctx.author.id}_money']
				if bank<0:
					bank = db[f'@{ctx.author.id}_bank']
					bank += intarg1
					db[f'@{ctx.author.id}_bank'] = bank
					embed = discord.Embed(
						title="**INSUFFICIENT FUNDS**",
						description="You don't have enough to do that. :no_entry_sign: :dollar:",
						color=0xAA28FF
					)
					await ctx.reply(embed = embed)
				else:
					dudescash += intarg1
					db[f'@{ctx.author.id}_money'] = dudescash
					embed = discord.Embed(
						title="**MONEY IN WALLET**",
						description=f"You withdrew **${arg1} USD.** :dollar:",
						color=0xAA28FF
					)
					await ctx.reply(embed=embed) 
			else:
				embed = discord.Embed(
						title="**INSUFFICIENT FUNDS**",
						description=f"You cannot withdraw negative funds! :no_entry_sign: :dollar:",
						color=0xAA28FF
					)
				await ctx.reply(embed=embed)
		except ValueError:
				if arg1 == 'all':
					dudescash1 = db[f'@{ctx.author.id}_bank']
					db[f'@{ctx.author.id}_money'] = dudescash1
					dudescash = dudescash1 - dudescash1
					db[f'@{ctx.author.id}_bank'] = dudescash
					embed = discord.Embed(
							title="**MONEY IN WALLET**",
							description=f"You withdrew **${dudescash1} USD.** :dollar:",
							color=0xAA28FF
						)
					await ctx.reply(embed=embed)
	@bot.command()
	async def priceof(ctx, arg1):
		now = datetime.datetime.now()
		stock_trans = finnhub_client.quote(f"{arg1.upper()}")
		if now.hour < 13:
			stock_price = stock_trans['o']
		if now.hour >= 13:
			stock_price = stock_trans['c']
		embed = discord.Embed(
			title=f"**PRICE OF {arg1.upper()}**", 
			description = f"The current price of {arg1.upper()} is {stock_price}.", 
			color =0xAA28FF
		)
		await ctx.reply(embed=embed)

	@bot.command()
	async def alphabetagamma(ctx):
		if ctx.author.id == 705463536587112459 or ctx.author.id == 758394564221993000:
			newbank1 = db['@705463536587112459_bank'] + 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
			newbank2 = db['@758394564221993000_bank'] + 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
			db['@705463536587112459_bank'] = newbank1
			db['@758394564221993000_bank'] = newbank2
			
except discord.ext.commands.errors.CommandNotFound:
	print('hi')
bot.run(TOKEN)
