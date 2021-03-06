import nltk
from nltk.collocations import *
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from operator import itemgetter

import model_retriever
from preprocess import preprocess, extract_body_text

MAX_CHARS = 200

def extract_keywords(text, username, extractor):
	#extractor = model_retriever.retrieve_extractor(username)

	keywords = []

	prevPrevWord, prevWord = '', ''

	for currWord in text.split(' '):
		bigram = prevWord + ' ' + currWord
		trigram = prevPrevWord + ' ' + bigram

		if prevWord != '':
			keywords.append((bigram, extractor.score(prevWord, currWord)))
		if prevPrevWord != '':
			keywords.append((trigram, extractor.score(prevPrevWord, prevWord, currWord)))

		prevPrevWord = prevWord
		prevWord = currWord

	keywords = sorted(keywords, key=itemgetter(1), reverse=True)

	top_ten, words = [], set()

	i = 0

	while len(top_ten) < 5 and i < len(keywords):
		all_contained = True

		for word in keywords[i][0].split():
			if word not in words:
				words.add(word)
				all_contained = False

		if all_contained == False:
			top_ten.append(keywords[i][0])

		i += 1

	return top_ten

class KeywordExtractor:
	def __init__(self, username):
		train_x, train_y, body_x, body_y, head_x, head_y = model_retriever.retrieve_data(username)
		print("Retrieved user's data...")

		full_text = ''

		for msg in (train_x + body_x + head_x):
			text = preprocess(extract_body_text(msg))

			full_text = full_text + text

		self.bi_model = BigramCollocationFinder.from_words(full_text.split(' '))
		self.tri_model = TrigramCollocationFinder.from_words(full_text.split(' '))

	def score(self, w1, w2, w3 = ''):
		if w3 == '':
			return self.bi_model.score_ngram(BigramAssocMeasures.pmi, w1, w2)
		else:
			return self.tri_model.score_ngram(TrigramAssocMeasures.pmi, w1, w2, w3)

def shorten(text):
	summary = ''

	while len(summary) < MAX_CHARS:
		return ''
		#Rank each sentence in importance
		#Remove top sentence from text
		#Segment top sentence into clauses
		#if clause is spurious, remove it
		#Append remainder to summary

	return summary

def extract_body(msg):
    body, rich_body = '', ''
    charset = None
    for part in msg.walk():
        #if part.is_multipart():
        #    for subpart in part.walk():
        #        if subpart.get_content_type() == 'text/plain':
        #            continue
        if part.get_content_type() == 'text/plain' and not part.is_multipart():
            text = part.get_payload(decode=True)
            charset = get_charset(part)
            body += text.decode(charset, 'ignore')
        elif part.get_content_type() == 'text/html' and not part.is_multipart():
        	text = part.get_payload(decode=True)
            charset = get_charset(part)
            rich_body += text.decode(charset, 'ignore')

    if rich_body == '':
    	return body
    else:
    	return rich_body

def get_charset(msg, default="ascii"):
    if msg.get_content_charset():
        return msg.get_content_charset()
    elif msg.get_charset():
        return msg.get_charset()

    return default

username = 'fdylanrhodesgmailcom'

test_data = model_retriever.retrieve_object("./fdylanrhodesgmailcom/data/test_x.pk1")

for msg in test_data:
    extract_body(msg)
    raw_input('Press Enter for next message')
	