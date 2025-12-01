import faiss
import numpy as np
import os

class FaissService:
    def __init__(self, dim, index_path="faiss.index"):
        self.dim = dim
        self.index_path = index_path
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            self.index = faiss.IndexFlatIP(dim)
        self.ntotal = self.index.ntotal

    def add_vector(self, vector):
        vector = vector.reshape(1, -1).astype(np.float32)
        return self.index.add(vector)

    def search_vector(self, vector, k=5):
        vector = vector.reshape(1, -1).astype(np.float32)
        scores, ids = self.index.search(vector, k)
        return ids[0], scores[0]

    def save(self):
        faiss.write_index(self.index, self.index_path)