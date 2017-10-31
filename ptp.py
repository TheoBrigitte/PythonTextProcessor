import sys, os, re, csv, collections

# extract_words return a list of words found in text
# a word is composed of one or more characters which can be :
# any lower or upper case letter, a dash or an apostrophe
def extract_words(text):
	# compile the regular expression for a word
	pattern = re.compile("[A-Za-z\-\']+")
	# match the regular expression against the whole text and return all occurences
	return re.findall(pattern, text)

# count the number of words in a text
def count_words(text):
	return len(extract_words(text))

# extract_sentences return a list of sentences found in text
def extract_sentences(text):
	# compile the regular expression for a sentence
	pattern = re.compile("""
		(.+?)					# catpure the sentence
		(?<![A-Z][a-z]\.)		# abbreviation Dr. is not end of sentence
		(?<![A-Z]\.)			# abbreviation S. is not end of sentence
		(?<=						# end of sentence can be:
			(?:
				\.[\"|”]			# quote ." 
			)
			|						# or
			.(?:\.|\?|\!)			# anything followed by . ? or !
		)
		\s+						# sentence is followed by any white characters
		(?![a-z])				# sentence do not start with lowercase
		""", re.DOTALL | re.X)
	# match the regular expression against the whole text and return all occurences
	return re.findall(pattern, text)

# create a csv with the <count> longest sentences
def longest_sentences_csv(filename, chapter, sentences, count):
	# csv headers/columns
	fields = ['length', 'sentence', 'chapter', 'ranking']

	writer = create_csv(filename, fields)

	# get the first X sentences (where X=count)
	sentences = sentences[:count]

	# write them into the csv
	for i in range(0, len(sentences), 1):
		writer.writerow({
			'length':  count_words(sentences[i]),
			'sentence': sentences[i],
			'chapter': chapter,
			'ranking': i+1,
		})

# extract longest sentences from <text> and write the first 10 into a csv
def longest_sentences(text, name, chapter):
	count = 10
	csvName = name + '-longest_sentences.csv'

	# extract sentences from the text
	sentences = extract_sentences(text)
	# sort sentences by length (which is defined by the number of words they contain)
	# ordered from longest to shortest
	sentencesByWords = sorted(sentences, key=count_words, reverse=True)

	longest_sentences_csv(csvName, chapter, sentencesByWords, count)
	print("created >", csvName)

# create a csv with the <count> most frequent words sentences
def most_frequent_words_csv(filename, chapter, words, count):
	# csv headers/columns
	fields = ["keyword", "frequency", "length", "chapter"]

	writer = create_csv(filename, fields)

	# write <count> most common words in the csv
	for i, val in enumerate(words.most_common(count)):
		writer.writerow({
			'keyword':  val[0],
			'frequency': val[1],
			'length': len(val[0]),
			'chapter': chapter,
		})

# extract most frequent words from <text> (excluding stopwords)
# and write the first 10 into a csv
def most_frequent_words(text, stopwords, name, chapter):
	count = 10
	csvName = name + '-most_frequent_words.csv'

	# lowercase the text so we avoid mismatch from uppercase
	lowerText = text.lower()
	# count words frequency
	words = collections.Counter(extract_words(lowerText))
	# filter out stopwords
	words = filter_stopwords(words, stopwords)

	most_frequent_words_csv(csvName, chapter, words, count)
	print("created >", csvName)

# filter_stopwords return counter with filtered out stopwords
def filter_stopwords(counter, stopwords):
	# copy the counter so we can modify it
	copy = counter.copy()

	# iterate over the counter and modify its copy
	# to reflect the changes
	for i in counter:
		if i in stopwords:
			del copy[i]

	return copy

# load stop words as a list of lowercase words
def load_stopwords(filename):
	f = open(filename, encoding = 'utf-8')
	text = f.read()

	return extract_words(text.lower())

# create the <filename> file
def create_csv(filename, fields):
	# create the csv file
	file = open(filename, 'w', encoding = 'utf-8')
	# wirte csv headers in the file
	writer = csv.DictWriter(file, fieldnames=fields)
	# wirte csv headers in the file
	writer.writeheader()

	return writer

# process_chapter load the file at filename and generate both
# the longest sentences and the most frequent words lists
def process_chapter(filename, chapter, stopwords):
	f = open(filename, encoding = 'utf-8')
	text = f.read()

	basename = os.path.basename(filename)
	name, ext = os.path.splitext(basename)

	longest_sentences(text, name, chapter)
	most_frequent_words(text, stopwords, name, chapter)

stopwords = load_stopwords("data/stopwordlist.txt")
process_chapter("data/Lectures on The Science of Language - Chapter1.txt", 1, stopwords)
process_chapter("data/Language: An Introduction to the Study of Speech - Chapter1.txt", 2, stopwords)
