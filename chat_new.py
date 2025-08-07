from flask import Flask, request, jsonify
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

server_url = 'https://gisurat.com/govardhan/gi_chatbot/'

app = Flask(__name__)
SESSION_USERS = {}  # temporary session mapping {mobile: user_id}

# Vector store setup
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=GOOGLE_API_KEY
)

# If you need to load documents for the first time
# You can use this block once and then comment it out
if not os.path.exists("./vectorstore"):  # only create if doesn't exist
    # Sample FAQs (Replace these with your actual FAQ list)
    faqs = [
        Document(page_content="Govardhan Institute is located in Surat."),
        Document(page_content="Courses offered include Python, Java, Full Stack, Power BI, and Ethical Hacking."),
        Document(page_content="You can register for a course by contacting us on 9898576877."),
        Document(page_content="Yes, we provide certification after course completion."),
        Document(page_content="We also provide placement assistance.")
    ]

    
    # Split (optional for large docs)
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(faqs)

    # Create Chroma vectorstore
    vectorstore = Chroma.from_documents(docs, embedding=embeddings, persist_directory="./vectorstore")
    vectorstore.persist()

vectorstore = Chroma(persist_directory="./vectorstore", embedding_function=embeddings)
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY),
                                  retriever=retriever)
                                  

def is_valid_mobile(mobile):
    return re.match(r"^[6-9]\d{9}$", mobile) is not None
  

def get_user_id_from_php(mobile):
    try:
        res = requests.get(f"{server_url}/get_user.php?mobile={mobile}")
        return res.json().get("user_id")
    except Exception as e:
        print("Error fetching user:", e)
        return None  

# Endpoint to receive initial question
@app.route("/chat", methods=["GET"])
def chat1():
    return jsonify({
            "status": "need_user_info",
            "message": "Welcome! Before we continue, please share your name and mobile number."
    })
    


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    print(data)
    mobile = data.get("mobile")
    name = data.get("name")
    question = data.get("question")

    if not mobile:
        return jsonify({
            "status": "need_user_info",
            "message": "Please provide your mobile number to continue."
        }),400

    if not is_valid_mobile(mobile):
        return jsonify({"status": "error", "message": "Invalid mobile number."}), 400

    # If mobile already in session cache
    user_id = SESSION_USERS.get(mobile)
    
    #if not already cached, check from PHP
    if not user_id:
        # Check if user already exists in MySQL
        user_id = get_user_id_from_php(mobile)
        if not user_id:
            # If not found, require name to create user
            if not name or name.strip() == "":
                return jsonify({
                    "status": "need_name",
                    "message": "Please provide your name to continue."
                })
        try:
            # Save user to PHP API
            print("Query :",f"{server_url}/save_query.php")
            res = requests.post(f"{server_url}/save_user.php", data={
                "name": name.strip(),
                "mobile": mobile
            })

            user_id = res.json().get("user_id")
            if not user_id:
                return jsonify({"status": "error", "message": "User could not be saved."}), 500

            SESSION_USERS[mobile] = user_id
        except Exception as e:
            print("Error saving user:",e)
            return jsonify({"status":"error","message":"Server error while saving user details."}),500

        else:
            # For returning users
            SESSION_USERS[mobile] = user_id

    # Step 3: Run RAG
    answer = qa.run(question)  # using your RAG chain here

    # Step 4: Save Q&A in MySQL (via PHP)
    print("Query :",f"{server_url}/save_query.php")
    requests.post(f"{server_url}/save_query.php", data={
        "user_id": user_id,
        "question": question,
        "response": answer
    })

    return jsonify({
        "status": "success",
        "answer": answer
    })

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)