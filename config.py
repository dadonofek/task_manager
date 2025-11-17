"""Configuration for the task manager application."""
import os

class Config:
    """Application configuration."""

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'tasks.db')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Application
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

    # Users (can be extended)
    USERS = ['Ofek', 'Wife']
