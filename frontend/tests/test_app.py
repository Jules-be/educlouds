from flask import Flask 
import unittest
from flask_sqlalchemy import SQLAlchemy 
import sys
import os 

sys.path.append('/Users/abdoulabdillahi/Desktop/CSC890/Abdoul/educlouds/frontend')

from src import __init__

# Assuming __init__ is the class name and create_app is a method
app_initializer = __init__.__init__()  # This is assuming the class is named __init__ and needs instantiation
app = app_initializer.create_app()

# # Adjust the following import according to your environment setup
# from src import __init__ create_app

class TestCreateApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()  # This will close and remove the test database if necessary 
    
    def test_app_creation(self):
        self.assertIsInstance(self.app, Flask)
        
    def test_app_config(self):
        self.assertEqual(self.app.config['SECRET_KEY'], 'Abdoul')
        self.assertIn('sqlite:///', self.app.config['SQLALCHEMY_DATABASE_URI'])
    
    def test_blueprint_registration(self):
        blueprints = [bp.name for bp in self.app.blueprints.values()]
        self.assertIn('views', blueprints)
        self.assertIn('auth', blueprints)
    
    def test_login_manager(self):
        self.assertTrue(hasattr(self.app, 'login_manager'))

if __name__ == "__main__":
    unittest.main()
