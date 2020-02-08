import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, format_list


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def testGetCategories(self):
        response = self.client().get("/categories")
        data = json.loads(response.data)

        categories = Category.query.all()
        test_data = format_list(categories)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, test_data)

    def testGetQuestionsPaginated(self):
        response = self.client().get("/questions?page=1")
        data = json.loads(response.data)

        questions = Question.query.paginate(1,10).items
        test_data = format_list(questions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["questions"], test_data)

    def testDeleteQuestion(self):
        test_id = Question.query.first().id
        response = self.client().delete("/questions/" + str(test_id), method="DELETE")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(Question.query.get(test_id))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()