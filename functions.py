import requests, json
import datetime
from bs4 import BeautifulSoup
from random import randint
import math

# Initializing a dictionary of coin exchanges pairs
coin_to_exchanges = dict()

# Initialize a dict of dictionaries for database
database = dict()


# Function to process CMC's api to retrieve the name of coin based on symbol provided
def updateDB(database):

	# Might want to include error handling just in case
	print("Updating database...")
	page = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
	response = json.loads(page.text)

	# Convert list of dict into dict of dict
	for i in response:
		database[i.get('symbol')] = i
	print("Update complete!")

# Function to check if coin exists in coin_to_exchanges dictionary
def checkCoin(coin, coin_to_exchanges):
	if(coin in coin_to_exchanges):
		print(coin + " found!")
		return True
	print(coin + " not found!")
	return False

# Function to get html source code for coin
def getSource(type, *args):
	print("In getSource function")
	if(type == 'exchange'):

		# URL for getting exchange details
		url = 'https://coinmarketcap.com/currencies/' + args[0] + '/'
	elif(type == 'history'):

		# Getting the date today and delta
		today = datetime.datetime.now()
		delta = datetime.timedelta(days=int(args[1]))

		# URL for getting historical data
		url = 'https://coinmarketcap.com/currencies/' + args[0] + '/historical-data/?start=' + (today - delta).strftime('%Y%m%d') + '&end=' + today.strftime('%Y%m%d')
	else:
		return False

	page = requests.get(url)
	if(page.status_code == 404):
		print("Source code not found")
		return False
	else:
		print("Source code found!")
		return BeautifulSoup(page.content, 'html.parser')

# Function to add coin to existing list
def updateCoin(coin, coin_to_exchanges):
	print("In updateCoin function")
	# Get source code
	soup = getSource('exchange', coin)

	# Process source code to get unique list of exchanges for coin
	if(soup != False):
		body = list(soup.find('table', id='markets-table').children)[3]
		i = 1
		rows = list(body.children)

		# Using sets instead of 
		exchanges = set()
		while(i < len(rows)):
			exchange = (list(rows[i])[3]).get_text()
			exchanges.add(exchange)
			i = i + 2
		coin_to_exchanges[coin] = exchanges
		print(coin + " updated!")
	else:
		print("Error updating " + coin + "!")


# Function to get list of exchanges for the given coin
def getExchange(coin, coin_to_exchanges):
	# If coin_to_exchanges doesn't contain coin, add it in. 
	if(not checkCoin(coin,coin_to_exchanges)):
		print("Processing exchange data for " + coin)
		updateCoin(coin, coin_to_exchanges)
		try:
			return coin_to_exchanges[coin]
		except Exception as e:
			print(e)
			return False
	else:
		return coin_to_exchanges[coin]

# Function to concatenate a list of exchanges into multiple strings max character length of 4096
def concatExchanges(exchanges):

	## Based on what I tested, bitcoin (which should be listed on the most exchanges) do not even have that many exchanges that will require a second string of 4096 characters so the entire code below is not necessary for now.
	# i = 0
	# j = 0
	# list_of_exchanges = list(exchanges)
	# numExchanges = len(list_of_exchanges)
	# exchanges_to_string = []
	# numStrings = 0
	# lenString = 0
	# maxLength = 4096

	# while(j < numExchanges):
	# 	if(lenString < maxLength ):
	# 		lenString = lenString + len(list_of_exchanges[j]) + 2 # 2 is for the newline 
	# 		j += 1
	# 	else:
	# 		exchanges_to_string.append('\n'.join(list_of_exchanges[i:j]))
	# 		lenString = 0
	# 		numStrings += 1
	# 		i = j

	# # To catch the leftover exchanges
	# if(numStrings == 0):
	# 	exchanges_to_string.append('\n'.join(list_of_exchanges[i:j]))
	# return exchanges_to_string

	return '\n'.join(list(exchanges))

# Function to update an existing list of exchanges for the given coin
def update(coin, coin_to_exchanges):
	print("Updating exchange data for " + coin)
	# Not the most efficient but it works.
	updateCoin(coin, coin_to_exchanges)

# Function to analyse if a coin is getting pumped
def analyse(*args):
	print("In analyse function")

	# Get source code
	soup = getSource('history', args[0], args[1])
	
	if(soup != False):
		body = list(soup.select('div#historical-data table.table')[0].children)[3]
		rows = list(body.children)
		i = len(rows) - 2
		accumulationFactor = 0

		while(i - 2 > 0):
			# 3 = open, 9 = closed, 11 = volume
			row_a = list(rows[i])
			open_a = int(row_a[3].get_text())
			close_a = int(row_a[9].get_text())
			vol_a = int(row_a[11].get_text().replace(',',''))

			row_b = list(rows[i-2])
			open_b = int(row_b[3].get_text())
			close_b = int(row_b[9].get_text())
			vol_b = int(row_b[11].get_text().replace(',',''))



			i = i - 2


		while(i < len(rows)):
			
			row = list(rows[i])
			vol = int(row[11].get_text().replace(',',''))
			print(vol)
			sum += vol
			i = i + 2

		print("Sum is " + str(sum)) 
		

		print(args[1])
	else:
		print("Analysis failed. Please check that you've entered the correct parameters.")

##################################
### Telegram Wrapper Functions ###
##################################

# Command to update database
def updateDBWrapper(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text='Updating database...')
	updateDB(database)
	bot.send_message(chat_id=update.message.chat_id, text='Update complete!')


# Command to find all exchanges that trades this coin
def exchangeWrapper(bot, update, args):
	print()
	if(len(args) != 1):
		bot.send_message(chat_id=update.message.chat_id, text='Too few / many arguments! Please enter only 1 ticker.', reply_to_message_id=update.message.message_id)
	else:
		# Getting the id equivalent (full name delimited with '-') of the target coin
		coin = args[0].upper()
		if(coin in database):
			id = database[coin].get('id')
			exchanges = getExchange(id, coin_to_exchanges)
			if(exchanges):
				print("Printing exchanges...")

				# list_of_exchanges is a list of concatenated exchanges into strings with a maximum length of 4096 characters, see comments in the concatExchange Function as to why this isn't necessary for now.
				# list_of_exchanges = []
				
				list_of_exchanges = concatExchanges(exchanges)
				bot.send_message(chat_id=update.message.chat_id, text=list_of_exchanges, reply_to_message_id=update.message.message_id)
				#for i in list_of_exchanges:
					#bot.send_message(chat_id=update.message.chat_id, text=i, reply_to_message_id=update.message.message_id)
		else:
			print(args[0] + " not found!")
			bot.send_message(chat_id=update.message.chat_id, text=args[0] + " cannot be found in DB, please run the updateDB command or check that you've entered .", reply_to_message_id=update.message.message_id)

# Command to update list of exchanges that trades this coin
def updateWrapper(bot, update, args):
	print()
	if(len(args) != 1):
		bot.send_message(chat_id=update.message.chat_id, text='Too few / many arguments! Please enter only 1 ticker.', reply_to_message_id=update.message.message_id)
	else:
		# Getting the id equivalent (full name delimited with '-') of the target coin
		coin = args[0].upper()
		if(coin in database):
			id = database[coin].get('id')
			update(id, coin_to_exchanges)
			bot.send_message(chat_id=update.message.chat_id, text="Exchanges for " + args[0] + " are updated!", reply_to_message_id=update.message.message_id)
		else:
			print(args[0] + " not found!")
			bot.send_message(chat_id=update.message.chat_id, text=args[0] + " cannot be found in DB, please run the updateDB command or check that you've entered valid parameters.", reply_to_message_id=update.message.message_id)

# Command to handle unregistered commands
def unknownWrapper(bot, update):
	replies = ["Stop trolling my bot Brian!", "Jon! Do you not understand the meaning of stop?!", "Invalid command...", "Please try again later even though it'll probably still not work lol.", "404 Error: Command not found!"]
	bot.send_message(chat_id=update.message.chat_id, text=replies[randint(0,4)], reply_to_message_id=update.message.message_id)

# Command to analyse if a coin is getting pumped
def analyseWrapper(bot, update, args):
	print()
	if(len(args) != 2):
			bot.send_message(chat_id=update.message.chat_id, text='Too few / many arguments! Please enter 1 ticker followed by number of days e.g. /analyse CND 7', reply_to_message_id=update.message.message_id)
	else:
		# Getting the id equivalent (full name delimited with '-') of the target coin
		coin = args[0].upper()
		day = round(float(args[1]))
		if(coin in database and day > 0): 
			id = database[coin].get('id')
			accumulationFactor = analyse(id, day)
			bot.send_message(chat_id=update.message.chat_id, text=accumulationFactor, reply_to_message_id=update.message.message_id)
				
		else:
			print("Invalid parameters or updateDB not run!")
			bot.send_message(chat_id=update.message.chat_id, text=args[0] + " cannot be found in DB, please run the updateDB command or check that you've entered valid parameters.", reply_to_message_id=update.message.message_id)
