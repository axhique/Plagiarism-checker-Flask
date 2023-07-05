import os
from flask import *
import re
import textract
import string
import docx2txt
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile


app=Flask(__name__)
def read_file(filename):
    """
    Read the contents of a file and return as a string
    """
    file_extension = os.path.splitext(filename)[1]
    if file_extension == ".docx":
        text = docx2txt.process(filename)

    elif file_extension == ".doc":
        docx_filename = filename + "x"
        try:
            doc = Document(filename)
            doc.save(docx_filename)
            text = docx2txt.process(docx_filename)
            os.remove(docx_filename)  
        except Exception as e:
            return f"Error converting .doc to .docx: {e}"
        

    elif file_extension == ".pdf":
        with open(filename, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                text += page.extract_text()
                
    elif file_extension  == ".txt":
        with open(filename, 'r') as file:
            text = file.read()

    else:
        return"Unsupported file format"

    return text


stop_words = set(['a', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before', 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give', 'given', 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing', 'now', 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once', 'one', 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right', 'right', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'year', 'years', 'yet', 'you', 'young', 'younger', 'youngest', 'your', 'yours', 'z'])


def preprocess_text(text):
    """
    Preprocess text by removing punctuations, converting to lowercase, removing whitespace, and removing stopwords
    """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    filtered_tokens = []
    for i in tokens:
        if i not in stop_words:
            filtered_tokens.append(i)
    text = ' '.join(filtered_tokens)
    return text

@app.route('/')
def thome():
    return render_template('home.html')

@app.route('/file')
def home():
    return render_template('index.html')

@app.route('/folder')
def index():
    return render_template('index2.html')

@app.route('/result', methods=['POST'])
def result():
    file1 = request.files['file1']
    file2 = request.files['file2']
    # Save uploaded files to a temporary directory
    temp_dir1 = tempfile.TemporaryDirectory()
    file1_path = os.path.join(temp_dir1.name, file1.filename)
    file2_path = os.path.join(temp_dir1.name, file2.filename)
    file1.save(file1_path)
    file2.save(file2_path)
    
    text1 = read_file(file1_path)
    text2 = read_file(file2_path)
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    
    
    vectorizer = TfidfVectorizer()
    
    X = vectorizer.fit_transform([text1, text2]).toarray()
    similarity = cosine_similarity(X[0].reshape(1,-1), X[1].reshape(1,-1))[0][0]
    percentage_similarity = round(similarity * 100, 2)
    return render_template('result.html', percentage_similarity=percentage_similarity)



@app.route('/result2', methods=['POST','GET'])
def upload():
   
    file = request.files['file']
    folder = request.files.getlist('folder')
    
    temp_file=tempfile.TemporaryDirectory()
    temp_dir= tempfile.TemporaryDirectory()
    
    file_path = os.path.join(temp_file.name, file.filename)
    file.save(file_path)
    path,qwery_filename=os.path.split(file_path)
    
    folder_paths = []
    for f in folder:
        folder_path = os.path.join(temp_dir.name, f.filename)
        f.save(folder_path)
        folder_paths.append(folder_path)

    query_file_text = read_file(file_path)
    query_file_text = preprocess_text(query_file_text)

    similarity_dict = {}
    for filename in folder_paths:
            if filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.doc') or filename.endswith('.txt'):
            
                file_text = read_file(filename)
                file_text = preprocess_text(file_text)
                vectorizer = TfidfVectorizer().fit_transform([query_file_text, file_text])
                vectors = vectorizer.toarray()
                similarity = cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))[0][0]
                f,name=os.path.split(filename)
                similarity_dict[name] = round(similarity * 100, 2)

    for folder_path in folder_paths:
        os.remove(folder_path)
    return render_template('result2.html', similarity_dict=similarity_dict)

if __name__ == '__main__':
    app.run(debug=True,port=5000)


