import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selected):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  results = [result.format() for result in selected]
  current_selection = results[start:end]

  return current_selection

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  DONE @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS(app)
  CORS(app, resources={r"/*": {"origins": "*"}})
  # cors = CORS(app, resources={r'*': {'origins': '*'}})

  '''
  DONE @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  DONE @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    selection = Category.query.order_by(Category.type).all()
    categs = {categ.id: categ.type for categ in selection}
    
    if len(selection) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'categories': categs,
      'total_categories': len(selection)

    })





  '''
  DONE @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  DONE TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      selection = Question.query.order_by(Question.id).all()
      paginated_questions = paginate(request, selection)
      categories = Category.query.order_by(Category.id).all()

  # My TODO: i don't know if the categories should return a number
  # Maybe the frontend will give hints
      if len(paginated_questions) == 0:
        abort(404)

      full_list = [c.type for c in categories]


      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'categories': full_list,
        'current_category': categories[0].type,
        'total_questions': len(selection)
      })

    except:
      abort(422)




  '''
  DONE @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  todo>> TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  # MyTodo: File a bug about getQuestions() function when the last question delete removes a page
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(selection)
      })
    
    except:
      abort(422)

  '''
  DONE @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  todo>> TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    if not all([new_question, new_answer, new_category, new_difficulty]):
      abort(400)

    try:
      q = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      q.insert()
      selection = Question.query.order_by(Question.id).all()
      paginated_questions = paginate(request, selection)

      return jsonify({
        'success': True,
        'created': q.id,

      })

    except:
      abort(422)


  '''
  DONE @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  todo>> TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def question_search():
    # use try and except pattern. Try None instead of blank
    search_term = request.json.get('searchTerm', '')
    selection = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).order_by(Question.question).all()
    paginated_results = paginate(request, selection)

    return jsonify({
      'success': True,
      'questions': paginated_results,
      'total_matches': len(selection)

    })



  '''
  DONE @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:categ_id>/questions', methods=['GET'])
  def qs_by_categories(categ_id):
# Had to increment by one because React indexes are zero based:
# my tod: use try and except pattern
    categ_id = categ_id + 1 
    selection = Question.query.filter(Question.category == str(categ_id)).order_by(Question.id).all()
    paginated_questions = paginate(request, selection)

    if len(paginated_questions) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(selection),
      'current_category': Category.query.get(categ_id).format()
    })





  '''
  DONE @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
  
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)
    try:
      if quiz_category['id'] == 0:
        selection = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        selection = Question.query.filter(Question.category == quiz_category['id'],
                                                  Question.id.notin_(previous_questions)).all()
      questions = [q.format() for q in selection]
      if len(questions) != 0:
        random_question = random.choice(questions)
        return jsonify({
            'success:': True,
            'question': random_question
        })
      else:
        return jsonify({
          'question': False
        })
      

    except:
      abort(422)



  '''
  DONE @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable. I cannot figure out what you mean.'
    }), 422

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    }), 405  

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Server Error. We crashed.'
    }), 400
    
  return app

    