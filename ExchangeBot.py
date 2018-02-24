# Import libraries
import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import functions

# Main code
def main():

	# Initiate logging module
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

	# Retrieve token from external file
	f = open('/Users/simon/Documents/Github/Accumulation Tracker/token.txt', 'r')
	tokenId = f.readline()

	# Create bot object and its corresponding updater and dispatcher
	bot = telegram.Bot(token=tokenId)
	updater = Updater(token=tokenId)
	dispatcher = updater.dispatcher 

	# Creating the relevant command handlers
	updateDB_handler = CommandHandler('updateDB', functions.updateDBWrapper)
	exchange_handler = CommandHandler('exchange', functions.exchangeWrapper, pass_args=True)
	update_handler = CommandHandler('update', functions.updateWrapper, pass_args=True)
	# unknown_handler = MessageHandler(Filters.command, functions.unknownWrapper)
	
	# Adding the handlers to the dispatcher
	dispatcher.add_handler(updateDB_handler)
	dispatcher.add_handler(exchange_handler)
	dispatcher.add_handler(update_handler)
	# dispatcher.add_handler(unknown_handler)

	# WIP functions  
	# analyse_handler = CommandHandler('analyse', functions.analyseWrapper, pass_args=True)
	# dispatcher.add_handler(analyse_handler)


	# Start the bot
	print('starting bot!')
	updater.start_polling(clean=True)

if __name__ == "__main__":
	main()