from ranker import Ranker
import utils
import numpy as np
# from nltk.corpus import wordnet
# from nltk.corpus import lin_thesaurus as thes

# Word2vec

# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        query_as_dict = self._parser.parse_query(query)
        query_as_list = self.get_list_words(query_as_dict)
        # query_as_list = self._parser.parse_sentence(query)
        relevant_docs = self._relevant_docs_from_posting(query_as_list)

        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        n_relevant = len(ranked_doc_ids)
        return n_relevant, ranked_doc_ids

    def get_list_words(self, query_as_dict):
        words_list = []
        for word in query_as_dict:
            for i in range(query_as_dict[word]):
                words_list.append(word)
        return words_list

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        que_vector = self.get_vector(query_as_list)
        relevant_docs = {}
        # for keywords
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term)
            for doc_id, amount in posting_list:
                df = relevant_docs.get(doc_id, 0)
                relevant_docs[doc_id] = df + 1
        docs = self._indexer.documents
        for doc_id, doc_list in docs.items():
            if doc_id in relevant_docs:
                words = doc_list
                doc_vector = self.get_vector(words)
                sim = self.cosine_similarity(doc_vector, que_vector)
                # if sim > 0.4:
                relevant_docs[doc_id] = sim + relevant_docs[doc_id]

        return relevant_docs

    def get_vector(self, tokens):
        words = [word.lower() for word in tokens if word.lower() in self._model.vocab]
        if len(words) >= 1:
            return np.mean(self._model[words], axis=0)
        else:
            return []

    def cosine_similarity(self, vector1, vector2):
        try:
            return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        except Exception:
            return 0
