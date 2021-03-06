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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name
        )
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
        test_data = {str(c.id): c.type for c in categories}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["categories"], test_data)

    def testGetQuestionsPaginated(self):
        response = self.client().get("/questions?page=1")
        data = json.loads(response.data)

        questions = Question.query.paginate(1, 10).items
        test_data = format_list(questions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["questions"], test_data)

    def testDeleteQuestion(self):
        test_id = Question.query.first().id
        response = self.client().delete(
            "/questions/" + str(test_id), method="DELETE"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(Question.query.get(test_id))

    def testCreateQuestion(self):
        payload = json.dumps({
            "question": "Test Question",
            "answer": "Ok",
            "category": "1",
            "difficulty": 1
        })
        response = self.client().post(
            "/questions", method="POST", content_type="application/json",
            data=payload
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"]["question"], "Test Question")
        self.assertEqual(data["question"]["answer"], "Ok")
        self.assertEqual(data["question"]["category"], "1")
        self.assertEqual(data["question"]["difficulty"], 1)

    def testSearchQuestions(self):
        test_question = Question.query.first().question
        payload = json.dumps({
            "searchTerm": test_question
        })
        response = self.client().post(
            "/questions/search", method="POST",
            content_type="application/json",
            data=payload
        )
        questions = json.loads(response.data)["questions"]
        question_list = [q["question"] for q in questions]
        self.assertEqual(response.status_code, 200)
        self.assertIn(test_question, question_list)

    def testGetQuestionsByCategory(self):
        test_question = Question.query.first()
        test_category_id = test_question.category
        test_questions = format_list(Question.query.filter_by(
            category=test_category_id
        ).all())
        response = self.client().get(
            "/categories/" + str(test_category_id) + "/questions", method="GET"
        )
        questions = json.loads(response.data)["questions"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_questions, questions)

    def testGetNextQuizQuestion(self):
        test_category = Category.query.first()
        test_questions = format_list(Question.query.filter_by(
            category=str(test_category.id)
        ).all())
        previous_questions = []
        for q in test_questions:
            response = self.client().post(
                "/quizzes",
                method="POST",
                content_type="application/json",
                data=json.dumps(
                    {
                        "previous_questions": previous_questions,
                        "quiz_category": {
                            "type": test_category.type,
                            "id": str(test_category.id)
                        }
                    }
                )
            )
            next_question = json.loads(response.data).get("question")
            self.assertEqual(response.status_code, 200)
            self.assertIn(next_question, test_questions)
            self.assertNotIn(next_question["id"], previous_questions)
            previous_questions.append(next_question["id"])

    def testErrorHandler400(self):
        payload = json.dumps({
            "term": "obama"
        })
        response = self.client().post(
            "/questions/search",
            method="POST",
            content_type="application/json",
            data=payload
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def testErrorHandler404(self):
        response = self.client().get("/questions?page=100", method="GET")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def testErrorHandler405(self):
        response = self.client().get("/questions/1", method="GET")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method not allowed")

    def testErrorHandler422(self):
        response = self.client().delete("/questions/1000", method="DELETE")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessible entity")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
