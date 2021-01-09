from collections import Counter
from nltk.corpus import stopwords
from document import Document
import re
import json
from stemmer import Stemmer


class Parse:
    def __init__(self, stemming=0):
        """
         This function initiate the fields of Parse, init the stemmer and entering stop words
         :param stemming: the boolean value is stem is needed (optional)
         """
        self.stemming = stemming
        self.stemmer = Stemmer()

        # self.stop_words = frozenset(stopwords.words('english')) ??????????????????????????????????????????????????????
        self.stop_words = stopwords.words('english')
        self.stop_words.extend([':', '\'s', '.', ',', ';', '’', '?', '!', 'rt', '-', '|', '~', '(', ')', '*', '+', '='
                                '/', '"', '``', '\'\'', '\n', '\n\n', '&', 'amp', '…', '\'', '`', '[', ']', '{', '}'])
        self.covid_words = ['corona', 'coronavirus', 'covid', 'covid19', 'cvd', 'covidvirus', 'covidviruses', 'cov', 'cov19', 'covids', 'cv19', 'coronavi', 'coronavir', 'coronaviruses', 'coronovirus']

    def find_url(self, text):
        """
        This function finds the url addresses in the text (with valid conditions for urls in string)
        :param text: the full text of the tweet
        :return: list of all urls in the text
        """
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return urls

    def tokenize_urls(self, urls):
        """
        This function tokenize the url addresses in the text
        :param urls: the list of urls in the text
        :return: list of tokenized words from all urls
        """
        url_tokens = []
        tokens_ans = []
        for url in urls:
            url_tokens.extend(re.split(r';|-|/|//|:|=|\?', url))

        for token in url_tokens:
            if 'www.' in token:
                tokens_ans.append(token.replace('www.', ''))

        return tokens_ans

    def number_3digits(self, number):
        """
        This function change the format of the number to 3 digits after the point
        :param number: the number is int/float
        :return: the number in the format (with 3 digits after the point)
        """
        return "{:.4g}".format(number)

    def number_size(self, w, i, text_tokens_list):
        """
        This function checks if the word is number between some range
        :param w: the word is string
        :param i: the index is integer
        :param text_tokens_list: this is a list of tokens
        :return: the word in the range
        """
        number = int(w) if w.isdigit() else float(w)
        # Number is in thousand range
        if 1000 <= number < 1000000:
            number = number / 1000
            w = self.number_3digits(number) + "K"
        # Number is in million range
        elif 1000000 <= number < 1000000000:
            number = number / 1000000
            w = self.number_3digits(number) + "M"
        # Number is in billion range or more
        elif 1000000000 <= number:
            number = number / 1000000000
            w = self.number_3digits(number) + "B"
        # Number is in hundred range or less
        else:
            w = self.number_3digits(number)

            # Thousand
            if i+1 < len(text_tokens_list) and (text_tokens_list[i+1] == 'Thousand' or text_tokens_list[i+1] == 'thousand'):
                text_tokens_list[i+1] = 'K'
                text_tokens_list[i: (i + 2)] = [''.join(text_tokens_list[i: (i + 2)])]
                w = text_tokens_list[i]

            # Million
            elif i+1 < len(text_tokens_list) and (text_tokens_list[i+1] == 'Million' or text_tokens_list[i+1] == 'million'):
                text_tokens_list[i + 1] = 'M'
                text_tokens_list[i: (i + 2)] = [''.join(text_tokens_list[i: (i + 2)])]
                w = text_tokens_list[i]

            # Billion
            elif i+1 < len(text_tokens_list) and (text_tokens_list[i+1] == 'Billion' or text_tokens_list[i+1] == 'billion'):
                text_tokens_list[i + 1] = 'B'
                text_tokens_list[i: (i + 2)] = [''.join(text_tokens_list[i: (i + 2)])]
                w = text_tokens_list[i]

            # Fraction after the number
            elif i + 1 < len(text_tokens_list) and bool(re.search(r'^-?[0-9]+\/[0-9]+$', text_tokens_list[i + 1])):
                text_tokens_list[i: (i + 2)] = [' '.join(text_tokens_list[i: (i + 2)])]
                w = text_tokens_list[i]

        return w

    def get_entity(self, text):
        """
        This function finds the entities in the text (two or more words in sequence that starts with capital letter)
        :param text: the full text of the tweet
        :return: list of all entities in the text
        """
        entities = re.findall(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)+| [A-Z][a-z]+(?: [A-Z][a-z]+)+', text)
        for i, entity in enumerate(entities):
            entities[i] = entity.upper()
            if entity[0] == ' ':
                entities[i] = entities[i][1:]
        return entities

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply parser rules for every word within the text
        :param text: the full text of the tweet
        :return: list of tokenized words
        """
        full_text = text
        # Extract the urls from the text and tokenize them separately
        urls = self.find_url(text)
        tokenized_urls = []
        if len(urls) != 0:
            tokenized_urls = self.tokenize_urls(urls)
        for url in urls:
            text = text.replace(url, '')

        # Tokenize the text- remove all characters that not ascii,
        # then split the words in the text by punctuation marks,
        # and finally clear all white spaces
        text = re.sub(r'[^\x00-\x7F]+', ',', text)
        text_tokens = re.split(r'([^a-zA-Z0-9_]|[0-9]*/[0-9]*|[0-9]*,[0-9]*,[0-9]*,[0-9]*|[0-9]*,[0-9]*,[0-9]*|[0-9]*,[0-9]*)', text) # \W
        text_tokens = list(filter((' ').__ne__, text_tokens))
        text_tokens = list(filter(('').__ne__, text_tokens))

        # Loops on the tokens list
        i = 0
        while i < len(text_tokens):
            w = text_tokens[i]
            # Check if the is stop word- delete her
            if (w.lower() in self.stop_words) or (w in self.stop_words):
                del text_tokens[i]
                continue
            elif w.lower() in self.covid_words:
                if i < (len(text_tokens) - 1) and (text_tokens[i+1] == '19'):
                    del text_tokens[i+1]
                elif (i < (len(text_tokens) - 1) and ((text_tokens[i+1] == '-') or (text_tokens[i+1] == '_'))) and (i < (len(text_tokens) - 2) and (text_tokens[i+2] == '19')):
                    del text_tokens[i+1]
                    del text_tokens[i+1]
                text_tokens[i] = 'covid'
                i += 1
                continue
            else:
                # Find parser rules
                # (Upper case) - if first letter is capital -> all word is uppercase
                if len(w) > 1 and w[0].isupper():
                    text_tokens[i] = w = w.upper()
                # (@) - if the word is @ and after there is a word -> union those tokens
                elif w == '@' and i < (len(text_tokens) - 1):
                    text_tokens[i: (i + 2)] = [''.join(text_tokens[i: (i + 2)])]
                    # del text_tokens[i]
                    # continue
                # (#) - if the word is # and after there is a word -> union those tokens (there are more rules here)
                elif w == '#' and i < (len(text_tokens) - 1) and (text_tokens[i+1] == ',' or text_tokens[i+1] == '#'):
                    del text_tokens[i]
                    del text_tokens[i]
                    continue
                elif w == '#' and i < (len(text_tokens) - 1) and text_tokens[i+1] != ',':
                    hashword = text_tokens[i + 1]
                    text_tokens[i: (i + 2)] = [''.join(text_tokens[i: (i + 2)]).lower().replace('_', '')]
                    separate = hashword.split('_')
                    # in case the words are not separated by _ (like: #home)
                    if len(separate) == 1:
                        # in case the hashtag is all lower case
                        if separate[0].islower():
                            text_tokens.insert(i, hashword)
                            continue

                        separate = re.findall('[A-Z][^A-Z]*', separate[0])

                    # new rule: hashtag with sequenced capital letter will be merged to one term (like: #WhereIsKCR)
                    for index, word in enumerate(separate):
                        if len(word) == 1 and word.isupper():
                            j = index + 1
                            while j < len(separate) and len(separate[j]) == 1:
                                j += 1
                            separate[index: (j + 1)] = [''.join(separate[index: (j + 1)])]

                    # Add the separated words from the hashtag to the tokens list
                    is_covid = False
                    for word in reversed(separate):
                        if len(word) > 0:
                            if word.lower() in self.covid_words:
                                text_tokens.insert(i, 'covid')
                                is_covid = True
                                break
                    if not is_covid:
                        for word in reversed(separate):
                            if len(word) > 0:
                                text_tokens.insert(i, word.lower())

                # Numbers
                elif w.isdigit() or w.replace(',', '').isdigit():
                    # Remove ,
                    text_tokens[i] = w = w.replace(',', '')

                    # .
                    if (i + 1) < len(text_tokens) and text_tokens[i + 1] == '.' and (i + 2) < len(text_tokens) and text_tokens[i + 2].isdigit():
                        text_tokens[i: (i + 3)] = [''.join(text_tokens[i: (i + 3)])]
                        w = text_tokens[i]

                    # Number%
                    if (i + 1) < len(text_tokens) and text_tokens[i + 1] == '%':
                        text_tokens[i] = self.number_3digits(float(text_tokens[i]))
                        text_tokens[i: (i + 2)] = [''.join(text_tokens[i: (i + 2)])]
                        i += 1
                        continue

                    # Number percent/percentage -> Number%
                    elif (i + 1) < len(text_tokens) and \
                            (text_tokens[i + 1] == 'percent' or text_tokens[i + 1] == 'percentage'):
                        text_tokens[i] = self.number_3digits(float(text_tokens[i]))
                        text_tokens[i + 1] = '%'
                        text_tokens[i: (i + 2)] = [''.join(text_tokens[i: (i + 2)])]
                        i += 1
                        continue

                    # Other numbers- check ranges
                    text_tokens[i] = w = self.number_size(w, i, text_tokens)

                    # new rule: $Number will be merged to one term
                    if i > 0 and text_tokens[i - 1] == '$':
                        text_tokens[(i - 1): (i + 1)] = [''.join(text_tokens[(i - 1): (i + 1)])]
                        continue
            i += 1

        # stem terms if needed
        if self.stemming:
            for j, term in enumerate(text_tokens):
                if text_tokens[j][0] != '#' and text_tokens[j][0] != '@':
                    text_tokens[j] = self.stemmer.stem_term(term)
        text_tokens += tokenized_urls
        return text_tokens

    # cant change the function signature
    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]

        entity_list = dict(Counter(self.get_entity(full_text)))

        # Change the short url in text to the full url (if exist in url dictionary), and send to parse_sentence
        j = json.loads(url)
        text = full_text
        for short in j:
            if j[short] is not None:
                text = text.replace(short, j[short])
        tokenized_text = self.parse_sentence(text)
        tokenized_text = list(filter(('').__ne__, tokenized_text))

        doc_length = len(tokenized_text)  # after text operations.

        term_dict = dict(Counter(tokenized_text))

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, entity_list)
        return document

    def parse_query(self, query):
        list_tokens = self.get_entity(query)
        list_tokens += self.parse_sentence(query)
        dict_tokens = dict(Counter(list_tokens))
        return dict_tokens

