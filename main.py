# from ast import Return
# from colorama import Cursor
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
import os
# from flask_mysqldb import MySQL
# from wtforms import Form,StringField,TextAreaField,PasswordField,validators
# from passlib.hash import sha256_crypt
# from functools import wraps

#login decorator
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if "logged_in" in session:
#             return f(*args, **kwargs)
#         else:
#             flash("Please login to view this page","danger")
#             return redirect(url_for("login"))

#     return decorated_function
# #user registration form
# class RegisterForm(Form):
#     name = StringField("Name", validators = [validators.Length(min = 3, max = 25)])
#     username = StringField("Username", validators = [validators.Length(min = 3, max = 35)])
#     email = StringField("email", validators = [validators.Email(message = "please enter a valid email address")])
#     password = PasswordField("Password",validators = [validators.DataRequired("plase enter a password"),
#      validators.EqualTo(fieldname = "confirm",message = "your password does not match")])
#     confirm = PasswordField("verify password")

# class LoginForm(Form):
#     username = StringField("Username")
#     password = PasswordField("Password")

app = Flask(__name__)
app.secret_key = "blog"

# app.config["MYSQL_HOST"] ="localhost"
# app.config["MYSQL_USER"] ="root"
# app.config["MYSQL_PASSWORD"] =""
# app.config["MYSQL_DB"] ="blog"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# mysql = MySQL(app)

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/korean_income_tax/", methods = ['POST', 'GET'])
def korean_income_tax():
    import vertexai
    from vertexai.language_models import CodeChatModel

    q = ''
    if request.method == 'GET':
        q = request.args.get('q')
    else:
        q = request.form.get('q')
        
    v = {}
    if q == None:
        v = { 'q': """과세표준과 기본 세율이 아래와 같고 퇴직연금과 급여공제가 없는 경우,  연봉 1억 받는 직장인의 소득세를 계산해줘.
1,400만원 이하	과세표준의 6%
1,400만원 초과~5,000만원 이하	84만원 + (1,400만원 초과금액의 15%)
5,000만원 초과~8,800만원 이하	624만원 + (5,000만원 초과금액의 24%)
8,800만원 초과~1억5천만원 이하	1,536만원 + (8,800만원 초과금액의 35%)
1억5천만원 초과~3억원 이하	3,706만원 + (1억5천만원 초과금액의 38%)
3억원 초과~5억원 이하	9,406만원 + (3억원 초과금액의 40%)
5억원 초과~10억원 이하	17,406만원 + (5억원 초과금액의 42%)
10억원 초과	38,406만원 + (10억원 초과금액의 45%)"""
        }
    else:        
        vertexai.init()#project=os.getenv('project_id'), location=os.getenv('region'))
        chat_model = CodeChatModel.from_pretrained("codechat-bison")
        chat = chat_model.start_chat()
        parameters = {
            "candidate_count": 1,
            "max_output_tokens": 1024,
            "temperature": 0.5
        }
        
        response = chat.send_message(q, **parameters)
        v = { "q": q, "a": response.text }
    # safety_settings={
    #         generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #         generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #         generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #         generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #     }
    
    return render_template("korean_income_tax.html", v = v)


@app.route("/plagiarism_detector", methods = ['POST', 'GET'])
def plagiarism_detector():
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts.chat import (
        ChatPromptTemplate,
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )

    q = ''
    if request.method == 'GET':
        q = request.args.get('q')
    else:
        q = request.form.get('q')
        
    v = {}
    chat = ChatOpenAI(api_key=os.getenv('openai_api_key'))
    if q == None:
        q = """Plastic pollution is currently the most widespread problem affecting the marine environment. It threatens ocean health, human health, coastal tourism, and also contributes to climate change.

Write a recommendation/proposal to your local council, suggesting ways we can reduce plastic waste and reduce pollution."""
    
    messages = [
        SystemMessage(
            content="You are a helpful assistant that answers given question."
        ),
        HumanMessage(
            content=q
        )
    ]
    response = chat.invoke(messages)
    ai_answer = response.content
    
    if request.method == 'GET':
    
        v = { 'q': q, "student_answer": ai_answer }
    else:  
        splitter ='\n'
        student_answer = request.form.get('student_answer')
        student_answer_sentences = [item.strip() for item in student_answer.split(splitter) if item.strip() != '']
        total_student_answer_sentence_count = len(student_answer_sentences)

        ai_answer_sentences = [item.strip() for item in ai_answer.split(splitter)]
        plagiarism_sentences = []
        # total_ai_answer_sentence_count = len(ai_answer_sentences)
        for i in student_answer_sentences:
            if i in ai_answer_sentences:
                plagiarism_sentences.append(i) 
        plagiarism_count = len(plagiarism_sentences)

        v = { "q": q, 
             "student_answer": student_answer, 
             "ai_answer": ai_answer, 
             "plagiarism_sentences": plagiarism_sentences,
             "plagiarism_count": plagiarism_count, 
             "total_student_answer_sentence_count": total_student_answer_sentence_count,
             "plagiarism_rate": (int) (plagiarism_count / total_student_answer_sentence_count * 100)
              }

    # safety_settings={
    #         generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #         generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #         generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #         generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    #     }
    
    return render_template("plagiarism_detector.html", v = v)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":    app.run(debug=True)


# @app.route("/vertex_streamlit/")
# def vertex_streamlit(q):
#     import streamlit as st
#     import google.generativeai as genai
#     import time
#     import random

#     st.set_page_config(
#         page_title="Chat with Gemini Pro",
#         page_icon="🔥"
#     )

#     st.title("Chat with Gemini Pro")
#     st.caption("A Chatbot Powered by Google Gemini Pro")

#     if "app_key" not in st.session_state:
#         app_key = st.text_input("Please enter your Gemini API Key", type='password')
#         # AIzaSyCkUm7WtmBQV5cTuMmIjFrneNsx9d1Dtes
#         if app_key:
#             st.session_state.app_key = app_key

#     if "history" not in st.session_state:
#         st.session_state.history = []

#     try:
#         genai.configure(api_key = st.session_state.app_key)
#     except AttributeError as e:
#         st.warning("Please Put Your Gemini API Key First")

#     model = genai.GenerativeModel("gemini-pro")
#     chat = model.start_chat(history = st.session_state.history)

#     with st.sidebar:
#         if st.button("Clear Chat Window", use_container_width=True, type="primary"):
#             st.session_state.history = []
#             st.rerun()

#     for message in chat.history:
#         role ="assistant" if message.role == 'model' else message.role
#         with st.chat_message(role):
#             st.markdown(message.parts[0].text)

#     if "app_key" in st.session_state:
#         if prompt := st.chat_input(""):
#             prompt = prompt.replace('\n', ' \n')
#             with st.chat_message("user"):
#                 st.markdown(prompt)
#             with st.chat_message("assistant"):
#                 message_placeholder = st.empty()
#                 message_placeholder.markdown("Thinking...")
#                 try:
#                     full_response = ""
#                     for chunk in chat.send_message(prompt, stream=True):
#                         word_count = 0
#                         random_int = random.randint(5,10)
#                         for word in chunk.text:
#                             full_response+=word
#                             word_count+=1
#                             if word_count == random_int:
#                                 time.sleep(0.05)
#                                 message_placeholder.markdown(full_response + "_")
#                                 word_count = 0
#                                 random_int = random.randint(5,10)
#                     message_placeholder.markdown(full_response)
#                 except genai.types.generation_types.BlockedPromptException as e:
#                     st.exception(e)
#                 except Exception as e:
#                     st.exception(e)
#                 st.session_state.history = chat.history



# @app.route("/vertex_chat/<string:q>")
# def vertex_chat(q):
#     # https://cloud.google.com/vertex-ai/generative-ai/docs/chat/test-chat-prompts#chat-query-python_vertex_ai_sdk
#     from vertexai.language_models import ChatModel, InputOutputTextPair
#     chat_model = ChatModel.from_pretrained("chat-bison@001")

#     if q == "":
#         q = "How many planets are there in the solar system?"

#     temperature: float = 0.2
#     parameters = {
#         "temperature": temperature,  # Temperature controls the degree of randomness in token selection.
#         "max_output_tokens": 256,  # Token limit determines the maximum amount of text output.
#         "top_p": 0.95,  # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
#         "top_k": 40,  # A top_k of 1 means the selected token is the most probable among all tokens.
#     }

#     chat = chat_model.start_chat(
#         context="My name is Miles. You are an astronomer, knowledgeable about the solar system.",
#         examples=[
#             InputOutputTextPair(
#                 input_text="How many moons does Mars have?",
#                 output_text="The planet Mars has two moons, Phobos and Deimos.",
#             ),
#         ],
#     )

#     # response = chat.send_message(
#     #     q, **parameters
#     # )
#     # print(f"Response from Model: {response.text}")
#     # v = {
#     #     "q": q,
#     #     "text": to_markdown(response.text)
#     # }
#     # return render_template("vertex_chat.html", v = v)

#     responses = chat.send_message_streaming(
#         message="How many planets are there in the solar system?", **parameters)
#     for response in responses:
#         print(response)

#     v = {
#         "q": q,
#         "text": "aaaa"
#     }
#     return render_template("vertex_chat.html", v = v)

# def to_markdown(text):
#     import textwrap
#     from IPython.display import Markdown
#     text = text.replace('*', '  *')
#     return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# @app.route("/vertex_ai/<string:q>")
# def vertext_ai(q):

#     #
#     import vertexai
#     from vertexai.preview.generative_models import GenerativeModel, Part
#     import vertexai.preview.generative_models as generative_models
#     import markdown
#     from render_html import render_in_browser as ren
#     import html

#     if q == "":
#         q = "What makes our life happy?"

#     vertexai.init(project="angular-axle-415015", location="us-central1")
#     model = GenerativeModel("gemini-1.0-pro-001")
#     responses = model.generate_content(
#         q,
#         generation_config={
#             "max_output_tokens": 2048,
#             "temperature": 0.9,
#             "top_p": 1
#         },
#         safety_settings={
#                 generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#                 generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#                 generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#                 generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         }
#     # stream=True,
#     )

#     # for response in responses:
#     #     print(response.text, end="")

#     # markdown.markdown(v.response, output_format='html')
#     # v = { "q": q, "response": markdown.markdown(responses.text, output_format='html') }
#     v = { "q": q, "response": responses.text }
#     return render_template("vertex_ai.html", v = v)
#     # return ren(markdown.markdown(responses.text, output_format='html'))

# #article site
# @app.route("/articles")
# def articles():
#     cursor = mysql.connection.cursor()
#     query = "Select * From articles"
#     result = cursor.execute(query)
#     if result > 0 :
#         articles = cursor.fetchall()
#         return render_template("articles.html",articles = articles)
#     else:
#         return render_template("articles.html")

# @app.route("/dashboard")
# @login_required
# def dashboard():
#     cursor = mysql.connection.cursor()
#     query = "Select * From articles where author = %s"
#     result = cursor.execute(query,(session["username"],))
#     if result > 0 :
#         articles = cursor.fetchall()
#         return render_template("dashboard.html",articles = articles)
#     else:
#         return render_template("dashboard.html")

# #register
# @app.route("/register",methods = ["GET","POST"])
# def register():
#     form = RegisterForm(request.form)
#     if request.method == "POST" and form.validate():
#         name = form.name.data
#         username = form.username.data
#         email = form.email.data
#         password = sha256_crypt.encrypt(form.password.data)

#         cursor = mysql.connection.cursor()

#         query = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
#         cursor.execute(query,(name,email,username,password))
#         mysql.connection.commit()

#         cursor.close()

#         flash("You have successfully registered","success")

#         return redirect(url_for("login"))
#     else:
#         return render_template("register.html", form=form)




# #login
# @app.route("/login",methods = ["GET","POST"])
# def login():
#     form = LoginForm(request.form)
#     if request.method == "POST":
#         username = form.username.data
#         password_entered = form.password.data

#         cursor = mysql.connection.cursor()
#         query = "Select * From users where username = %s"
#         result = cursor.execute(query,(username,))
#         if result > 0 :
#             data = cursor.fetchone()
#             real_password = data["password"]
#             if sha256_crypt.verify(password_entered,real_password):
#                 flash("You have sign in successfully","success")

#                 session["logged_in"] = True
#                 session["username"] = username

#                 return redirect(url_for("index"))
#             else:
#                 flash("you entered your password incorrectly","danger")
#                 return redirect(url_for("login"))

#         else:
#             flash("there is no such user","danger")
#             return redirect(url_for("login"))


#     return render_template("login.html",form = form)

# #Detail page
# @app.route("/article/<string:id>")
# def article(id):
#     cursor = mysql.connection.cursor()
#     query = "Select * from articles where id = %s "
#     result = cursor.execute(query,(id,))
#     if result > 0:
#         article = cursor.fetchone()
#         return render_template("article.html", article = article)
#     else:
#         return render_template("article.html")

# #logout
# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("You have logout successfully","success")
#     return redirect(url_for("index"))

# #add article
# @app.route("/addarticle",methods = ["GET","POST"])
# def addarticle():
#     form = ArticleForm(request.form)
#     if request.method == "POST" and form.validate():
#         title = form.title.data
#         content = form.content.data

#         cursor = mysql.connection.cursor()
#         query = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"
#         cursor.execute(query,(title,session["username"],content))

#         mysql.connection.commit()
#         cursor.close()
#         flash("article successfully added","success")
#         return redirect(url_for("dashboard"))

#     return render_template("addarticle.html",form = form)

# #delete article
# @app.route("/delete/<string:id>")
# @login_required
# def delete(id):
#     cursor = mysql.connection.cursor()
#     query = "Select * from articles where author = %s and id = %s"
#     result = cursor.execute(query,(session["username"],id))
#     if result > 0:
#         query2 = "Delete from articles where id = %s"
#         cursor.execute(query2,(id,))
#         mysql.connection.commit()
#         return redirect(url_for("dashboard"))
#     else:
#         flash(" There is no such article or you are not authorized for this action")
#         return redirect(url_for("index"))

# #article update
# @app.route("/edit/<string:id>",methods = ["GET","POST"])
# @login_required
# def update(id):
#     if request.method == "GET":
#         cursor = mysql.connection.cursor()

#         query = "Select * From articles where id = %s and author= %s"
#         result = cursor.execute(query,(id,session["username"]))
#         if result == 0:
#             flash("There is no such article or you are not authorized for this action","danger")
#             return redirect(url_for("index"))
#         else:
#             article = cursor.fetchone()
#             form = ArticleForm()
#             form.title.data = article["title"]
#             form.content.data = article ["content"]
#             return render_template("update.html",form = form)

# #post request
#     else:
#         form = ArticleForm(request.form)
#         newTitle = form.title.data
#         newContent = form.content.data
#         query2 = "Update articles Set title = %s, content = %s where id = %s"
#         cursor = mysql.connection.cursor()
#         cursor.execute(query2,(newTitle,newContent,id))
#         mysql.connection.commit()
#         flash("Article is updated successfully!","success")
#         return redirect(url_for("dashboard"))


# #search url
# @app.route("/search",methods = ["GET","POST"])
# def search():
#     if request.method == "GET":
#         return redirect(url_for("index"))
#     else:
#         keyword = request.form.get("keyword")
#         cursor = mysql.connection.cursor()
#         query = "Select * From articles where title like '%" + keyword +"%'"
#         result = cursor.execute(query)
#         if result == 0:
#             flash("No article found matching the search term","warning")
#             return redirect(url_for("articles"))
#         else :
#             articles = cursor.fetchall()
#             return render_template("articles.html",articles = articles)
#  #article form
# class ArticleForm(Form):
#     title = StringField("Title of article",validators=[validators.length(min = 5, max = 100)])
#     content = TextAreaField("Content of Article",validators=[validators.length(min = 10)])
