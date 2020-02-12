# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

If you want to use a virtual environment, the Pipfile provided will cover you.

```bash
pipenv install
pipenv shell
```

This will install all of the required packages we selected within the `requirements.txt` and `Pipfile`files.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, initialize your database using the following

```bash
createdb trivia
```

Once created, run the migration script to create the correct database schemae as follows

```bash
flask db upgrade
```

Restore the database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## Endpoints

- GET '/categories'
- GET '/categories/id/questions'
- GET '/questions'
- POST '/questions'
- DELETE '/questions/id'
- POST '/questions/search'
- POST '/quizzes'

### GET '/categories'

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs.

```json
{
  "1" : "Science",
  "2" : "Art",
  "3" : "Geography",
  "4" : "History",
  "5" : "Entertainment",
  "6" : "Sports"
}
```

### GET '/categories/id/questions'

- Fetches a list of questions which belong to the requested category
- Request Arguments: Category ID
- Returns: An object with three keys -- current category, questions and total questions, that contains the requested category ID, a list of questions belonging to that category, and the total number of questions in the database as values respectively

```json
{
  "current_category": 1, 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ], 
  "total_questions": 20
}
```

### GET '/questions?page=1'

- Fetches a list of all questions in the database
- Request Arguments: None
- Request Parameters: page
- Returns: An object with four keys -- categories, current category ID, questions and total questions that contains a dictionary of all categories, the current category (not used by frontend, defaulting to ""), a list of all questions in the database, and the total number of questions respectively; all results pertain to the page number provided in the request paramter `page`

```json
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": "", 
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
  ], 
  "total_questions": 20
}
```

### POST '/questions'

- Creates a new question
- Request Body: JSON payload containing keys for Question (string), Answer (string), Difficulty (int), Category (int). Difficulty is ranked on a scale of 1-5 from easiest to hardest
- Returns: A response object with two keys -- success, which indicates the status of the request; and question, which returns the created question object if successful

#### Input

```json
{
  "question": "What is President Obama's first name?",
  "answer": "Barack",
  "difficulty": "1",
  "category": "4"
}
```

#### Response

```json
{
  "success": true,
  "question": {
    "id": 1,
    "question": "What is President Obama's first name?",
    "answer": "Barack",
    "difficulty": "1",
    "category": "4"
  }
}
```

### DELETE '/questions/id'

- Deletes a questions by its given ID
- Request Arguments: Question ID
- Returns: An object with a single key, success, indicating the status of the request

```json
{
  "success": true,
}
```

### POST '/questions/search'

- Searches for questions based on the provided searchTerm keyword
- Request Body: JSON payload containing key for searchTerm (string)
- Returns: An object with three keys -- current category ID, questions and total questions that contains the current category (not used by frontend, defaulting to ""), a list of all questions matching the provided searchTerm keyword, and the total number of questions respectively

#### Input

```json
{
  "searchTerm": "Obama"
}
```

#### Response

```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is President Obama's first name?",
      "answer": "Barack",
      "difficulty": "1",
      "category": "4"
    }
  ],
  "currentCategory": "",
  "totalQuestions": 20
}
```

### POST '/quizzes'

- Retrieves a random question based on the current category and a list of IDs of questions which have already been played within the same session
- Request Body: JSON payload containing two keys -- current category ID (int) and a list of question IDs ([int])
- Returns: A question object, or `null` if all questions have been asked within the maximum playable limit

#### Input

```json
{
  "previous_questions": [1,2,3,4],
  "quiz_category": 4
}
```

#### Response

```json
{
  "question": {
    "id": 5,
    "question": "What is President Obama's first name?",
    "answer": "Barack",
    "difficulty": "1",
    "category": "4"
  }
}
```

## Testing

To run the tests, run

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python3 test_flaskr.py
```
