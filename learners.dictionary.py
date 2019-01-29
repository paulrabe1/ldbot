# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re
import telebot


TOKEN = 'YOURAPIKEYHERE'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
	hello = bot.send_message(message.chat.id, 'Give me a word and i ll provide a definition!\nYou can use /help command for instructions.')


@bot.message_handler(commands=['help'])
def start(message):
	hello = bot.send_message(message.chat.id, 'Usage: \n 	1. Give me one word in English;\n 	2. I ll give answer you with desciption;\n 	3. Enjoy your learning!')


def chunk(in_string,num_chunks):
    chunk_size = len(in_string)//num_chunks
    if len(in_string) % num_chunks: chunk_size += 1
    iterator = iter(in_string)
    for _ in range(num_chunks):
        accumulator = list()
        for _ in range(chunk_size):
            try: accumulator.append(next(iterator))
            except StopIteration: break
        yield ''.join(accumulator)


def get_html(url):
	response = requests.get(url) 
	return response.text 


def get_definition_full(word, html):
	# Making LIST with first element 
	defs = ['Available definitions for "' + word + '" are:']
	# Getting SOUP object from WEB PAGE
	soup = BeautifulSoup(html, 'lxml')
	# Looking for html block with word types definitions and examples
	try:
		senses = soup.find_all('div', class_='entry entry_v2 boxy')
		# A loop for word types (e.g. noun/verb)
		for fl in senses:
			# Adding try cycle to decrease error chanses
			try:
				# Adding word type to list 
				a = '\n' + fl.find('span', class_='fl').get_text() + ':'
				defs.append(a.upper())
			except:
				pass
			# Looking for senses in html block
			devs = fl.find_all('div', class_='sense')
			for dev in devs:
			# Looking for definitions loop
				try:
					a = '\n -- ' + dev.find('span', class_='def_text').get_text() + ';'
					defs.append(a)
					# Looking for examples loop
					vis = dev.find_all('li', class_='vi')
					x = 0
					for vi in vis:
						b = vi.get_text()
						b = '		e.g.  ' + b.replace("\n", "")
						defs.append(b)
						x = x + 1
						if x == 2: 
							break
				except: 
					pass 
				# Another type of definitions
				try:
					a = '\n -- ' + dev.find('span', class_='un_text').get_text() + ';'
					defs.append(a)
					# Looking for examples loop
					vis = dev.find_all('li', class_='vi')
					x = 0
					for vi in vis:
						b = vi.get_text()
						b = '		e.g.  ' + b.replace("\n", "")
						defs.append(b)
						x = x + 1
						if x == 2: 
							break
				# Deleting last element (expect word type) if there are not any definitions
				except:
					pass
	except:
		pass
	if defs == ['Available definitions for "' + word + '" are:']:
		defs = 'Sorry i havent find a definiton to your word, try another!'
		return defs
	else:
		return '\n'.join(defs)


def get_definition(word, html):
	# Making LIST with first elemen
	defs = ['The most popular definitions for "' + word + '" are:'] 
	# Getting SOUP object from WEB PAGE
	soup = BeautifulSoup(html, 'lxml')
	# Looking for html block with word types definitions and examples
	try:
		senses = soup.find_all('div', class_='entry entry_v2 boxy')
		# A loop for word types (e.g. noun/verb)
		for fl in senses:
			# Adding try cycle to decrease error chanses
			try:
				# Adding word type to list 
				a = '\n' + fl.find('span', class_='fl').get_text() + ':'
				defs.append(a.upper())
				try:
					a = '-- ' + fl.find('span', class_='def_text').get_text() + ';'
					defs.append(a)
				except:
					a = '-- ' + fl.find('span', class_='un_text').get_text() + ';'
					defs.append(a)
				# else:
					# defs.pop()
				a = '    e.g.  ' + fl.find('li', class_='vi').get_text().replace("\n", "")
				defs.append(a)

			except:
				pass
	except:
		pass
	if defs == ['The most popular definitions for "' + word + '" are:']:
		defs = 'Sorry i havent find a definiton to your word, try another!'
		return defs
	else:
		a = '\n\nFor more definitons send me:' 
		defs.append(a)
		return '\n'.join(defs)



@bot.message_handler(commands=['full'], content_types=["text"])
def get_a_word_full(message):
    word = message.text.replace('/full', '')
    url = 'http://www.learnersdictionary.com/definition/' + word
    answer = get_definition_full(word, get_html(url))
    if len(answer) < 4096:
    	bot.send_message(message.chat.id, answer)
    elif 8192 > len(answer) > 4096:
    	answer = list(chunk(answer, 2))
    	bot.send_message(message.chat.id, answer[0])
    	bot.send_message(message.chat.id, answer[1])
    elif 12288 > len(answer) > 8192:
    	answer = list(chunk(answer, 3))
    	bot.send_message(message.chat.id, answer[0])
    	bot.send_message(message.chat.id, answer[1])
    	bot.send_message(message.chat.id, answer[2])
    elif len(answer) > 12288:
    	answer = list(chunk(answer, 4))
    	bot.send_message(message.chat.id, answer[0])
    	bot.send_message(message.chat.id, answer[1])
    	bot.send_message(message.chat.id, answer[2])
    	bot.send_message(message.chat.id, answer[3])    	


@bot.message_handler(content_types=["text"])
def get_a_word(message):
	word = message.text
	url = 'http://www.learnersdictionary.com/definition/' + word
	answer = get_definition(word, get_html(url))
	bot.send_message(message.chat.id, answer)
	if answer != 'Sorry i havent find a definiton to your word, try another!':
		full =  '/full ' + word
		bot.send_message(message.chat.id, full)

if __name__ == '__main__':
	while True:
		try:
			bot.polling(none_stop=True)
		except:
			pass
