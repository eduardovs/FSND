import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:sqledu123@{}/{}".format('localhost:5433', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Whats the capital of Argentina?',
            'answer': 'Buenos Aires',
            'category': 3,
            'difficulty': 2
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']) <= 10)
        self.assertTrue(data['categories'])

    def test_bad_pagination(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)     

    # def test_delete_questions(self):
    #     res = self.client().delete('/questions/5')
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted'])
    #     self.assertTrue(data['total_questions'])

    # def test_create_questions(self):
    #     res = self.client().post('/questions', json=self.new_question)
    #     data = json.loads(res.data)
        
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created'])

    def test_question_search(self):
        res = self.client().post('/questions/search', json={'searchTearm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_matches'])

    def test_qs_by_categories(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category']['type'], 'History')

    def test_qs_by_categories_404(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 404)

    def test_play_quiz(self):
        res = self.client().post('/quizzes', 
            json={'quiz_category': {'id': 4},
                    'previous_question': []
                    })
        data = json.loads(res.data)        

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_play_quiz_422(self):
        res = self.client().post('/quizzes', 
            json={'previous_question': []
                    })
        data = json.loads(res.data)        

        self.assertEqual(res.status_code, 422)



    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

# simple test to be removed
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()