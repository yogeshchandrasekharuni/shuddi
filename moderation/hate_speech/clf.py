import torch
import numpy as np
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
import wordninja
from nltk.corpus import stopwords
import re
from bs4 import BeautifulSoup
import lxml
import html5lib
import pickle
import string
from pdb import set_trace
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec
from gensim.test.utils import common_texts
from wordcloud import WordCloud
from nltk.tokenize import word_tokenize
from gensim.models import KeyedVectors
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils import shuffle
from typing import List, Tuple
from moderation.hate_speech.core import MLP

PATH = 'moderation/hate_speech/'


class Preprocesser():
    '''
    Pre-processes the message
    '''
    def __init__(
        self,
        word_scores: dict = None, # stores the TF-IDF value of all the words stored in the training dataset,
        scaler: StandardScaler() = None, # to scale our newly engineered features
        dimension: int = 300,
        dependencies_path: str = None
    ):
        self.dimension = dimension
        
        if word_scores and scaler:
            self.word_scores = word_scores
            self.scaler = scaler
            
        elif dependencies_path:
            with open(dependencies_path, 'rb') as save_file:
                self.word_scores, self.scaler = pickle.load(save_file)
        
        self.w2v_model = KeyedVectors.load_word2vec_format(
            PATH + 'data/GoogleNews-vectors-negative300.bin', binary=True
        ) # load the pretrained w2v model
        
        
    def preprocess_text(self, text):

        def remove_special_chars_and_numbers(text):
            '''
            Returns text without any special characters and numbers
            '''
            return text.translate(str.maketrans('', '', string.punctuation)).translate(str.maketrans('', '', string.digits))

        def remove_stopwords(text):
            '''
            Removes stopwords from text
            '''
            new_text = list()
            stop_words = set(stopwords.words('english')) 
            for word in text.split():
                if word not in stop_words:
                    new_text.append(word)
            return ' '.join(new_text)

        def remove_html_tags(text):
            '''
            Removes html tags from the text
            '''
            return BeautifulSoup(str(text), 'html.parser').get_text()

        def remove_non_english_words(text):
            '''
            Removes all non-english words in the text
            '''
            pattern = r'[^\x00-\x7f]'
            new_text = ''
            for element_index, element in enumerate(text):
                if not re.search(pattern, element):
                    new_text = new_text + element
            return new_text

        def do_lemmatization(text):
            lemma = WordNetLemmatizer()
            return lemma.lemmatize(text)

        def convert_lower_case(text):
            return text.lower()

        def remove_single_alphabets(text):
            new_text = list()
            for word in text.split():
                if len(word) == 1:
                    if word.isalpha():
                        continue
                new_text.append(word)
            return ' '.join(new_text)

        text = remove_html_tags(text)
        text = remove_special_chars_and_numbers(text)
        text = remove_stopwords(text)
        text = remove_non_english_words(text)
        text = convert_lower_case(text)
        text = do_lemmatization(text)
        text = remove_single_alphabets(text)
        
        return text
        
    
    
    def get_avg_word_length(
        self,
        text: str
    ) -> float:
        try:
            return sum([len(word) for word in text.split()]) / len(text.split())
        except ZeroDivisionError:
            return 0
    
    def get_message_length(
        self,
        text: str
    ) -> int:
        
        return len(text)
    
    
    def get_w2v_embeddings(
        self,
        message: str
    ) -> np.ndarray:
        
        embedding = list()
        
        message = word_tokenize(message)
        
        for word in message:
            try:
                embedding.append(self.word_scores[word] * self.w2v_model[word])
            except KeyError:
                try:
                    for split_word in wordninja.split(word):
                        embedding.append(self.word_scores[word] * self.w2v_model[split_word])
                except KeyError:
                    pass # the particular word was not a part of the vocab and was skipped

        return np.array(embedding)
    
    def get_averaged_embeddings(
        self,
        embedded_message: np.ndarray
    ) ->  np.ndarray:
        
        if len(embedded_message) == 0:
            return np.array([np.inf] * 300)
        
        return np.mean(embedded_message, axis=0)
    
    
    def preprocess(
        self,
        message: str
    ) -> np.ndarray:
        
        message = self.preprocess_text(message)
        avg_word_len = self.get_avg_word_length(message)
        message_len = self.get_message_length(message)
        
        embedded_message = self.get_averaged_embeddings(
            self.get_w2v_embeddings(message)
        )
        
        embedded_message = np.append(
            embedded_message,
            self.scaler.transform([
                [
                    avg_word_len,
                    message_len
                ]
            ])
        )
        
        return embedded_message
    
    
class HateSpeechClassifier():
    '''
    Implements our neural network
    '''
    def __init__(
        self,
        clf: MLP,
        pp: Preprocesser
        
    ) -> None:
        
        self.clf = clf
        self.pp = pp
        
    def get_model_output(
        self,
        message: str
    ) -> torch.Tensor:
        
        message = self.pp.preprocess(message)
        return torch.round(
            torch.sigmoid(
                self.clf(
                    torch.Tensor([
                        message
                    ])
                )
            )
        ).squeeze(1).detach().cpu().numpy()
        
        
    def predict(
        self,
        message: str
    ) -> bool:
        
        return bool(self.get_model_output(message))


if __name__ == '__main__':
    
    mlp = MLP()
    MODEL_PATH = PATH + 'data/mlp_model_state_dict.pth'
    pp = Preprocesser(dependencies_path = PATH + 'data/dependencies_24_4.pickle')
    mlp.load_state_dict(torch.load(MODEL_PATH))
    mlp.eval()

    clf = HateSpeechClassifier(clf = mlp, pp = pp)
    clf.predict('love you')