import utils
from sortedcontainers import SortedDict

# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = config
        self.entityDict = {}
        self.documents = {}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        values = document_dictionary.values()
        if len(values) == 0:
            max_tf = 0
            doc_size = 1
        else:
            max_tf = max(values)
            doc_size = sum(values)

        terms = document_dictionary.copy().keys()
        size_terms = len(terms)
        # Save doc data, format: {tweet id: (words dictionary(word: amount), max_tf, size_terms)
        self.documents[document.tweet_id] = (self.get_words(document_dictionary), max_tf, size_terms)

        # Go over each term in the doc
        for term in terms:
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    self.postingDict[term] = []
                else:
                    self.inverted_idx[term] += 1

                term_repeats_doc = document_dictionary[term]
                tf = term_repeats_doc / doc_size
                self.postingDict[term].append((document.tweet_id, term_repeats_doc, tf))

            except:
                print('problem with the following key {}'.format(term[0]))
        for term in document.entity_list.keys():
            amount = document.entity_list[term]
            if term not in self.entityDict:
                self.entityDict[term] = [(document.tweet_id, amount, amount/doc_size)]
            else:
                self.entityDict[term].append((document.tweet_id, amount, amount/doc_size))

    def after_indexing(self):
        # checks the rule for upper/lowercase
        print(len(self.inverted_idx.keys()))
        terms = self.inverted_idx.copy().keys()
        for term in terms:
            if term.isupper() and (term.lower() in self.inverted_idx.keys()):
                self.inverted_idx[term.lower()] += self.inverted_idx[term]
                del self.inverted_idx[term]
                self.postingDict[term.lower()].extend(self.postingDict[term])
                del self.postingDict[term]
        print(len(self.inverted_idx.keys()))
        # checks the rule for entities
        for entity, entityDocs in self.entityDict.items():
            if len(entityDocs) >= 2:
                self.inverted_idx[entity] = len(entityDocs)
                self.postingDict[entity] = entityDocs

        del self.entityDict


        # print(SortedDict(self.inverted_idx))
        # print(SortedDict(self.postingDict))
        print(len(self.inverted_idx.keys()))
        # print(len(self.postingDict.keys()))

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        listObj = utils.load_list(fn)
        self.inverted_idx = listObj[0]
        self.postingDict = listObj[1]
        self.documents = listObj[2]

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.save_list([self.inverted_idx, self.postingDict, self.documents], fn)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def get_words(self, dict):
        words = []
        for term, amount in dict.items():
            if amount > 1:
                for i in range(amount):
                    words.append(term)
            else:
                words.append(term)
        return words
