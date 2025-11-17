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
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001')

    # Users (can be extended)
    USERS = ['Ofek', 'Shachar']

    # WhatsApp Integration
    WHATSAPP_GROUP_NAME = os.getenv('WHATSAPP_GROUP_NAME', 'Task Manager')
    WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'False').lower() == 'true'
