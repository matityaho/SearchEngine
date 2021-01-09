from ranker import Ranker
# import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet
import numpy as np
import math

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
        relevant_docs = self._relevant_docs_from_posting(query_as_dict)

        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        n_relevant = len(ranked_doc_ids)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        n = len(self._indexer.documents.keys())
        IDFi = self.IDFi(query_as_list, self._indexer.inverted_idx, n)
        Wiq = self.Wiq(query_as_list, IDFi)
        relevant_docs = {}
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term)
            for doc_id, amount, tf in posting_list:
                df = relevant_docs.get(doc_id, 0)
                relevant_docs[doc_id] = df + 1
        for doc_id in relevant_docs.keys():
            doc_terms = self._indexer.documents[doc_id][0]
            Wij = self.Wij(doc_terms, query_as_list, self.IDFi(doc_terms, self._indexer.inverted_idx, n))
            cos = self.cosine_similarity(Wij, Wiq)
            # relevant_docs[doc_id] = cos
            relevant_docs[doc_id] = cos + relevant_docs[doc_id]
        # print(relevant_docs)
        return relevant_docs


    def cosine_similarity(self, Wij, Wiq):
        try:
            return np.dot(Wij, Wiq) / (np.linalg.norm(Wij) * np.linalg.norm(Wiq))
        except Exception:
            return 0


    def Wij(self, doc_term_tf, query, IDFi):
        d = sum(doc_term_tf.values())
        list_wij = []
        for term in query:
            if term in doc_term_tf:
                tf = doc_term_tf[term]/d
                idf = IDFi[term]
                # Wij = TFij * IDFi
                list_wij.append(tf * idf)
            # if term.upper() in doc_term_tf:
            #     tf = doc_term_tf[term.upper()]
            #     idf = IDFi[term.upper()]
            #     # Wij = TFij * IDFi
            #     list_wij.append(tf * idf)
            else:
                list_wij.append(0)
        return list_wij

    def Wiq(self, query, IDFi):
        d = sum(query.values())
        list_wiq = []
        for term in query:
            tf = query[term] / d
            idf = IDFi[term]
            # Wiq = TFiq * IDFi
            list_wiq.append(tf * idf)
        return list_wiq

    def IDFi(self, doc, inverted_index, n):
        list_idf = {}
        for term in doc:
            # IDFi = log2(N / DFi)
            if term not in inverted_index:
                list_idf[term] = 0
            # elif term.lower() in inverted_index:
            #     list_idf[term] = math.log2(n / inverted_index[term.lower()])
            else:
                list_idf[term] = math.log2(n / inverted_index[term])
        return list_idf