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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    
    def test_categories_not_found(self):
        res = self.client().get('/categories/100') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Resource not found"')

    def test_get_questions(self):
        res = self.client().get('/questions') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))
    '''
    def test_questions_not_found(self):
       res = self.client().get('/questions/100') 
       data = json.loads(res.data)
       self.assertEqual(res.status_code,404)
       self.assertEqual(data['success'], False)
       self.assertTrue(data['message'], 'Resource not found')
      
    '''    

    def test_post_questions_(self):
        res = self.client().post('/questions', json = {'question': 'test question', 'answer': 'test answer', 'category': '1', 'difficulty': '3'}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        
    
    def test_post_questions_error_422(self):
        json_data  = {'question': 'test question with no answer', 'category': '1','difficulty': '3'}
        res = self.client().post('/questions', json = json_data) 
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "Can't be processed")
        
    
    def test_delete_question(self):
        question= Question(question = 'test question', answer= 'test answer', category = '1', difficulty = '3')
        question.insert()
        questionId = question.id
        res = self.client().delete(f'/questions/{questionId}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(questionId))
        
        
    
    def test_delete_non_existing_question(self):
        res = self.client().delete('/questions/abc')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],   'Bad Request')
        
       
    def test_search_question(self):
        res = self.client().post('/questions/search', json = {'searchTerm': 'where'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
        

    def test_search_question_422(self):
        res = self.client().post('/questions/search', json = {'searchTerm': ''})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "Can't be processed")

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/2/questions')    
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['totalQuestions'])
        self.assertEqual(data['currentCategory'],'2')
   
    def test_get_questions_by_category_error_404(self):
        res = self.client().get('/categories/a200/questions')    
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'Resource not found')

    def test_play(self):
        res = self.client().post('quizzes', json = {'previous_questions': [], 'quiz_category': {'type' : 'History', 'id' : '4'}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_play_error_422(self):
        res = self.client().post('quizzes', json = {'quiz_category': {'type' : 'History', 'id' : ''}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "Can't be processed")
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()