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

        terms = document_dictionary.copy().keys()
        # Save doc data, format: {tweet id: [words]}
        self.documents[document.tweet_id] = self.get_words(document_dictionary)

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
                self.postingDict[term].append((document.tweet_id, term_repeats_doc))

            except:
                print('problem with the following key {}'.format(term[0]))
        for term in document.entity_list.keys():
            amount = document.entity_list[term]
            if term not in self.entityDict:
                self.entityDict[term] = [(document.tweet_id, amount)]
            else:
                self.entityDict[term].append((document.tweet_id, amount))

    def after_indexing(self):
        # checks the rule for upper/lowercase
        # print(len(self.inverted_idx.keys()))
        terms = self.inverted_idx.copy().keys()
        for term in terms:
            if term.isupper() and (term.lower() in self.inverted_idx.keys()):
                self.inverted_idx[term.lower()] += self.inverted_idx[term]
                del self.inverted_idx[term]
                self.postingDict[term.lower()].extend(self.postingDict[term])
                del self.postingDict[term]
        # print(len(self.inverted_idx.keys()))
        # checks the rule for entities
        for entity, entityDocs in self.entityDict.items():
            if len(entityDocs) >= 2:
                self.inverted_idx[entity] = len(entityDocs)
                self.postingDict[entity] = entityDocs

        del self.entityDict


        # sort = SortedDict(self.inverted_idx)
        # print()
        # print(SortedDict(self.postingDict))
        print(self.inverted_idx['fauci'])
        print(self.inverted_idx['flu'])
        print(self.postingDict['fauci'])
        print(self.documents['1286426604818833408'])

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
