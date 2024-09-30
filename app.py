import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os
import jsonpickle
from dotenv import load_dotenv

import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
import pytesseract
from PIL import Image
import pdf2image

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not os.path.exists('static/uploads'):
	os.makedirs('static/uploads/', exist_ok=True)

UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__, static_url_path='/static')
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.environ["OPENAI_API_KEY"] = api_key

@app.route("/")
def doc_read():
    return render_template('doc_read.html')

@app.route('/', methods=['POST'])
def upload_pdf():
	collection = request.form.get('collection')
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No pdf selected for uploading')
		return redirect(request.url)
	else:
		filename = secure_filename(file.filename)
		if not os.path.exists('static/uploads/'):
			os.makedirs('static/uploads/', exist_ok=True)

		file.save(os.path.join('static/uploads/', filename))
		flash('pdf successfully uploaded')
		return render_template('doc_read.html', filename=filename, collection=collection)

@app.route('/uploaded_files', methods=['GET', 'POST'])
def uploaded_files():
    pdf_list = 'static/uploads/'
    if os.path.exists('static/uploads'):
        allfiles = os.listdir(pdf_list)
        files = [ fname for fname in allfiles ]
        return jsonpickle.encode(files)

@app.route('/remove_file', methods=['GET', 'POST'])
def remove_file():
    pdf_list = 'static/uploads/'
    if os.path.exists('static/uploads'):
        for parent, dirnames, filenames in os.walk(pdf_list):
            for fn in filenames:
                if fn.lower().endswith('.pdf'):
                    os.remove(os.path.join(parent, fn))
        allfiles = os.listdir(pdf_list)
        files = [ fname for fname in allfiles ]
        return jsonpickle.encode(files)
    
@app.route('/get_response', methods=['GET', 'POST'])
def get_response():
    path = 'static/uploads/'
    pdf_files = []
    for file in os.listdir(path):
       pdf_files.append(path + file)
    text_data = [get_pdf_content([file]) for file in pdf_files]
    chunks = [get_chunks(text) for text in text_data]
    vector_embeddings = [get_embeddings(chunk) for chunk in chunks]
    conversation = start_conversation(vector_embeddings[0])
    
    json_body = request.get_json()
    query = json_body['prompt']
    response = conversation.invoke(query)
    return response['answer']
    
# load the PDFs & extract the text
def get_pdf_content(documents):
    raw_text = ""
    for document in documents:
        pdf_reader = PyPDF2.PdfReader(document)
        for page in pdf_reader.pages:
            text = page.extract_text()
            raw_text += text
            
            # Extract text from diagrams using OCR
            # images = pdf2image.convert_from_path(document, dpi=200)
            # for img in images:
            #     text_from_image = pytesseract.image_to_string(img)
            #     raw_text += text_from_image
            #     print("raw_text========>",raw_text)
    return raw_text

# chunk the text into smaller pieces
def get_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    text_chunks = text_splitter.split_text(text)
    return text_chunks

# create embeddings of text chunks & store in vector database
def get_embeddings(chunks):
    embeddings = OpenAIEmbeddings()
    vector_storage = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vector_storage

# function to generate a response to a user query
def start_conversation(vector_embeddings):
    llm = ChatOpenAI(api_key=api_key, temperature=0.7)
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )
    conversation = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_embeddings.as_retriever(),
        memory=memory
    )
    return conversation

if __name__ == '__main__':
    app.run(port=8080, debug=True)
