# ==== backend/utils/preprocessing.py ====
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

# Download necessary NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except nltk.downloader.DownloadError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('corpora/omw-1.4') # For WordNetLemmatizer
except nltk.downloader.DownloadError:
    nltk.download('omw-1.4', quiet=True)

class TextPreprocessor:
    """
    A utility class for preprocessing text data, typically for ML models.
    Includes lowercasing, punctuation removal, stop word removal, and lemmatization.
    """
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess(self, text: str) -> str:
        """
        Applies a series of preprocessing steps to the input text.
        
        Args:
            text (str): The input text to preprocess.
            
        Returns:
            str: The processed text.
        """
        # 1. Lowercasing
        text = text.lower()

        # 2. Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # 3. Remove numbers (optional, depending on use case)
        text = re.sub(r'\d+', '', text)

        # 4. Tokenization
        tokens = word_tokenize(text)

        # 5. Remove stop words and lemmatize
        processed_tokens = []
        for word in tokens:
            if word not in self.stop_words:
                lemmatized_word = self.lemmatizer.lemmatize(word)
                processed_tokens.append(lemmatized_word)

        # 6. Join tokens back into a string
        return " ".join(processed_tokens)

# Example Usage (for testing/debugging)
if __name__ == "__main__":
    preprocessor = TextPreprocessor()
    sample_text = "The user reported that the application is crashing frequently (Error 500) after the latest update on May 1st, 2023. This is a critical issue."
    
    processed_text = preprocessor.preprocess(sample_text)
    print("Original text:", sample_text)
    print("Processed text:", processed_text)
    
    sample_text_2 = "Network connectivity issues affecting multiple users in building 3. Cannot access shared drives."
    processed_text_2 = preprocessor.preprocess(sample_text_2)
    print("\nOriginal text 2:", sample_text_2)
    print("Processed text 2:", processed_text_2)