"""
Configuration settings for DocuSearch application
"""

import os

class Config:
    """Application configuration class"""
    
    # File processing limits
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 50))  # Default 50MB
    MAX_PAGES_PER_DOCUMENT = int(os.getenv('MAX_PAGES_PER_DOCUMENT', 500))  # Default 500 pages
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    PARSED_DOCUMENTS_FOLDER = 'parsed_documents'
    JOB_RESULTS_FOLDER = 'job_results'
    
    # Flask settings
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    
    # Search settings
    SEARCH_RESULTS_LIMIT = 50
    
    # Supported file types
    SUPPORTED_FILE_TYPES = {
        'application/pdf': 'PDF',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
        'text/plain': 'TXT',
        'text/html': 'HTML'
    }
    
    # Metadata extraction options
    AVAILABLE_METADATA_OPTIONS = [
        'title',
        'author', 
        'published_date',
        'topic',
        'abstract'
    ]
    
    @classmethod
    def get_max_file_size_bytes(cls):
        """Get maximum file size in bytes"""
        return cls.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @classmethod
    def get_max_file_size_mb(cls):
        """Get maximum file size in MB"""
        return cls.MAX_FILE_SIZE_MB
    
    @classmethod
    def get_max_pages(cls):
        """Get maximum pages per document"""
        return cls.MAX_PAGES_PER_DOCUMENT

