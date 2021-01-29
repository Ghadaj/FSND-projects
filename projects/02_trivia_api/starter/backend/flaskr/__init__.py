import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category
import random



QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request 
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headets', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headets', 'GET, POST,PATCH, DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods= ['GET'])
  def get_categories():
    categories = Category.query.order_by('id').all()
    if categories is None:
      abort(404)
    return jsonify ({
      'success' : True,
      'categories' : {category.id:category.type for category in categories}
    })
   
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods = ['GET', 'POST'])
  def get_post_questions():
    if request.method == 'GET': 
      questions = Question.query.all()
      page = request.args.get('page',1,type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      formatted_questions = [q.format() for q in questions]
      categories = Category.query.order_by('id').all()
      formatted_categories = {category.id:category.type for category in categories}
      if questions is None:
        abort(404)
      return jsonify ({
        'success': True,
        'questions' : formatted_questions[start:end],
        'total_questions' : len(formatted_questions),
        'categories' :     formatted_categories,
        'current_category' : None 
      })
    elif request.method == 'POST':

      posted_info= request.get_json()
      if ('question' not in posted_info or 'answer' not in posted_info or 'category' not in posted_info or 'difficulty' not in posted_info):
          abort(422)
      posted_question = posted_info.get('question')
      posted_answer = posted_info.get('answer')
      posted_difficulty = posted_info.get('difficulty')
      posted_category = posted_info.get('category')

      try:
  
        newQuestion = Question(question = posted_question,answer = posted_answer, difficulty = posted_difficulty, category = posted_category)
        newQuestion.insert()
        return jsonify({
          'success' : True,
          'created' : newQuestion.id
        })
      except:
        abort(400)  
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      Question.query.get(question_id).delete()
      return jsonify ({
        'success': True,
        'deleted': question_id
      })

    except:
      abort(400)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods = ['POST'])
  def search_questions():

    try:
      search_term = request.get_json().get('searchTerm', '')
      if search_term == '':
        abort()
      searchTerm= '%'+search_term+'%'
      result=Question.query.filter(Question.question.ilike(searchTerm)).all()
      formatted_result =  [q.format() for q in result]
      return jsonify ({
        'success' : True,
        'questions': formatted_result,
        'total_questions' : len(formatted_result),
        'current_category' : None
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route ('/categories/<category_id>/questions' , methods = ['GET'])
  def get_questions_by_category (category_id):
    try:
      result = Question.query.filter(Question.category == category_id).all()
      formatted_result =  [q.format() for q in result]
      return jsonify ({
        'success': True,
        'questions': formatted_result,
        'totalQuestions': len(formatted_result),
        'currentCategory': category_id
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods = ['POST'])
  def play():

    try:
      json = request.get_json()
      previous_questions = json.get('previous_questions')
      quiz_category = json.get('quiz_category') 
      if quiz_category['type'] == 'click':
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.category == quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()
      if len(questions) > 0:
        next_question = random.choice(questions).format()
      else:
        next_question = None
      return jsonify ({
        'success': True,
        'question': next_question
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def error_400(e):
    return jsonify({
      'success': False,
      'error': 400,
      'message': "Bad Request"
    }),400

  @app.errorhandler(404)
  def error_404(e):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "Resource not found"
    }),404

  @app.errorhandler(422)
  def error_422(e):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "Can not be processed"
    }),422
  
  return app
    