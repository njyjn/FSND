import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category, format_list, db

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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=["GET"])
  @cross_origin()
  def get_categories():
    categories = Category.query.all()
    result = ({
      "categories": {c.id:c.type for c in categories}
    })
    return jsonify(result)

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
  @app.route('/questions', methods=["GET"])
  @cross_origin()
  def get_questions_paginated():
    page = request.args.get('page', 1, type=int)
    question_query = Question.query.paginate(page, QUESTIONS_PER_PAGE)
    questions_list = format_list(question_query.items)

    categories = Category.query.all()

    result = {
      "questions": questions_list,
      "total_questions": question_query.total,
      "current_category": "",
      "categories": {c.id:c.type for c in categories}
    }

    return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  @cross_origin()
  def delete_questions(question_id):
    try:
      question = Question.query.get(question_id)
      db.session.delete(question)
      db.session.commit()

      result = {
        "success": True,
      }
    except:
      db.session.rollback()
      print(sys.exc_info)
      abort(500)
    finally:
      db.session.close()

    return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=["POST"])
  @cross_origin()
  def add_questions():
    payload = request.get_json()
    try:
      question = Question(
        question=payload.get("question"),
        answer=payload.get("answer"),
        category=payload.get("category"),
        difficulty=payload.get("difficulty")
      )
      db.session.add(question)
      db.session.commit()

      result = {
        "success": True,
        "question": question.format()
      }
    except:
      db.session.rollback()
      print(sys.exc_info)
      abort(500)
    finally:
      db.session.close()

    return jsonify(result)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


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

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def method_not_allowed(error):
    return jsonify({
          "success": False,
          "error": 422,
          "message": "Method not allowed"
        }), 404

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal server error"
        }), 500


  
  return app

    