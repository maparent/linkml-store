from typing import Callable, Optional, Dict, Any, List, Tuple

import numpy as np
from pydantic import BaseModel

INDEX_ITEM = np.ndarray


def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    return dot_product / (norm1 * norm2)


class Index(BaseModel):
    """
    An index operates on a collection in order to search for objects.
    """

    name: Optional[str] = None
    index_function: Optional[Callable] = None
    distance_function: Optional[Callable] = None
    index_attributes: Optional[str] = None
    text_template: Optional[str] = None
    filter_nulls: Optional[bool] = True
    vector_default_length: Optional[int] = 1000
    index_field: Optional[str] = "__index__"

    def object_to_vector(self, obj: Dict[str, Any]) -> INDEX_ITEM:
        """
        Convert an object to an indexable object

        :param obj:
        :return:
        """
        return self.text_to_vector(self.object_to_text(obj))

    def objects_to_vectors(self, objs: List[Dict[str, Any]]) -> List[INDEX_ITEM]:
        """
        Convert a list of objects to indexable objects

        :param objs:
        :return:
        """
        return [self.object_to_vector(obj) for obj in objs]

    def texts_to_vectors(self, texts: List[str]) -> List[INDEX_ITEM]:
        """
        Convert a list of texts to indexable objects

        :param texts:
        :return:
        """
        return [self.text_to_vector(text) for text in texts]

    def text_to_vector(self, text: str) -> INDEX_ITEM:
        """
        Convert a text to an indexable object

        :param text:
        :return:
        """
        raise NotImplementedError

    def object_to_text(self, obj: Dict[str, Any]) -> str:
        """
        Create a text from an object suitable for indexing.
        """
        if self.index_attributes:
            obj = {k: v for k, v in obj.items() if k in self.index_attributes}
        if self.filter_nulls:
            obj = {k: v for k, v in obj.items() if v is not None}
        if self.text_template:
            return self.text_template.format(**obj)
        return str(obj)

    def search(self, query: str, vectors: List[Tuple[str, INDEX_ITEM]], limit: Optional[int] = None) -> List[Tuple[float, str]]:
        """
        Search the index for a query string

        :param query: The query string to search for
        :param vectors: A list of indexed items, where each item is a tuple of (id, vector)
        :param limit: The maximum number of results to return (optional)
        :return: A list of item IDs that match the query
        """
        import numpy as np

        # Convert the query string to a vector
        query_vector = self.text_to_vector(query)

        distances = []

        # Iterate over each indexed item
        for item_id, item_vector in vectors:
            # Calculate the Euclidean distance between the query vector and the item vector
            #distance = 1-np.linalg.norm(query_vector - item_vector)
            distance = cosine_similarity(query_vector, item_vector)
            distances.append((distance, item_id))

        # Sort the distances in ascending order
        distances.sort(key=lambda x: -x[0])

        # Limit the number of results if specified
        if limit is not None:
            distances = distances[:limit]

        return distances





