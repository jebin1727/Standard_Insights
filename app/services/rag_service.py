from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SchemaRetriever:
    def __init__(self, snippets):
        self.snippets = snippets
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.corpus = [s['content'] for s in snippets]
        if self.corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        else:
            self.tfidf_matrix = None

    def retrieve(self, query, k=3):
        if self.tfidf_matrix is None or not self.corpus:
            return ""
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        selected_snippets = [self.corpus[i] for i in top_indices if similarities[i] > 0]
        
        # If no similarity found by TF-IDF, return all (or top k) if small
        if not selected_snippets:
            # Fallback to simple keyword check or just return top k
            return "\n\n".join(self.corpus[:k])
            
        return "\n\n".join(selected_snippets)
