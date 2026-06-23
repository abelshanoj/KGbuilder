import re
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def normalize_entity(entity: str) -> str:
    entity = entity.lower().strip()
    entity = re.sub(r'[^a-z0-9\s]', '', entity)  # remove punctuation
    entity = lemmatizer.lemmatize(entity)        # singularize
    return entity