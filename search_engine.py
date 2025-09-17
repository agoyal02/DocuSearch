import json
import os
import re
from collections import defaultdict
from datetime import datetime

class SearchEngine:
    def __init__(self):
        self.index = defaultdict(list)  # term -> list of (document_id, positions)
        self.documents = {}  # document_id -> document metadata
        self.document_count = 0
    
    def index_document(self, document_content, filename):
        """Index a document for search using metadata fields"""
        doc_id = f"doc_{self.document_count}"
        self.document_count += 1
        
        # Store document metadata
        self.documents[doc_id] = {
            'filename': filename,
            'title': document_content.get('title', 'Untitled'),
            'file_type': document_content.get('file_type', 'Unknown'),
            'upload_date': document_content.get('upload_date', ''),
            'author': document_content.get('author', []),
            'topic': document_content.get('topic', ''),
            'abstract': document_content.get('abstract', ''),
            'published_date': document_content.get('published_date', '')
        }
        
        # Create searchable text from metadata fields
        searchable_text = self._create_searchable_text(document_content)
        if searchable_text:
            terms = self._tokenize(searchable_text)
            for position, term in enumerate(terms):
                self.index[term].append((doc_id, position))
    
    def search(self, query, limit=10):
        """Search for documents containing the query terms"""
        query_terms = self._tokenize(query.lower())
        if not query_terms:
            return []
        
        # Calculate relevance scores
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.index:
                for doc_id, position in self.index[term]:
                    # Simple scoring: term frequency + position bonus
                    doc_scores[doc_id] += 1.0
                    # Bonus for terms appearing earlier in document
                    if position < 100:
                        doc_scores[doc_id] += 0.5
        
        # Sort by score and return results
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:limit]:
            doc_info = self.documents[doc_id].copy()
            doc_info['score'] = score
            doc_info['doc_id'] = doc_id
            
            # Create snippet from metadata fields
            searchable_text = self._create_searchable_text_from_doc(doc_info)
            snippet = self._extract_snippet(searchable_text, query_terms)
            doc_info['snippet'] = snippet
            
            results.append(doc_info)
        
        return results
    
    def _create_searchable_text(self, document_content):
        """Create searchable text from metadata fields"""
        searchable_parts = []
        
        # Add title
        if document_content.get('title'):
            searchable_parts.append(document_content['title'])
        
        # Add authors (handle both array and string formats)
        author = document_content.get('author', [])
        if isinstance(author, list):
            for author_item in author:
                if isinstance(author_item, dict):
                    # New format: array of dictionaries
                    if 'name' in author_item and author_item['name'] != 'Not found':
                        searchable_parts.append(author_item['name'])
                else:
                    # Old format: array of strings
                    if author_item and author_item != 'Not found':
                        searchable_parts.append(author_item)
        elif author and author != 'Not found':
            searchable_parts.append(author)
        
        # Add topic
        if document_content.get('topic') and document_content['topic'] != 'Not found':
            searchable_parts.append(document_content['topic'])
        
        # Add abstract (check both direct field and metadata dict)
        abstract = document_content.get('abstract')
        if not abstract and 'metadata' in document_content:
            abstract = document_content['metadata'].get('abstract')
        if abstract and abstract != 'Not found':
            searchable_parts.append(abstract)
        
        # Add published date
        if document_content.get('published_date') and document_content['published_date'] != 'Not found':
            searchable_parts.append(document_content['published_date'])
        
        return ' '.join(searchable_parts)
    
    def _create_searchable_text_from_doc(self, doc_info):
        """Create searchable text from stored document info"""
        searchable_parts = []
        
        # Add title
        if doc_info.get('title'):
            searchable_parts.append(doc_info['title'])
        
        # Add authors (handle both array and string formats)
        author = doc_info.get('author', [])
        if isinstance(author, list):
            for author_item in author:
                if isinstance(author_item, dict):
                    # New format: array of dictionaries
                    if 'name' in author_item and author_item['name'] != 'Not found':
                        searchable_parts.append(author_item['name'])
                else:
                    # Old format: array of strings
                    if author_item and author_item != 'Not found':
                        searchable_parts.append(author_item)
        elif author and author != 'Not found':
            searchable_parts.append(author)
        
        # Add topic
        if doc_info.get('topic') and doc_info['topic'] != 'Not found':
            searchable_parts.append(doc_info['topic'])
        
        # Add abstract (check both direct field and metadata dict)
        abstract = doc_info.get('abstract')
        if not abstract and 'metadata' in doc_info:
            abstract = doc_info['metadata'].get('abstract')
        if abstract and abstract != 'Not found':
            searchable_parts.append(abstract)
        
        # Add published date
        if doc_info.get('published_date') and doc_info['published_date'] != 'Not found':
            searchable_parts.append(doc_info['published_date'])
        
        return ' '.join(searchable_parts)
    
    def _tokenize(self, text):
        """Simple tokenization - split on whitespace and punctuation"""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Split on whitespace and filter out empty strings
        return [word for word in text.split() if word]
    
    def _extract_snippet(self, text, query_terms, snippet_length=200):
        """Extract a snippet of text containing query terms"""
        text_lower = text.lower()
        
        # Find the first occurrence of any query term
        best_position = -1
        for term in query_terms:
            pos = text_lower.find(term)
            if pos != -1 and (best_position == -1 or pos < best_position):
                best_position = pos
        
        if best_position == -1:
            # No query terms found, return beginning of text
            return text[:snippet_length] + "..." if len(text) > snippet_length else text
        
        # Extract snippet around the found position
        start = max(0, best_position - snippet_length // 2)
        end = min(len(text), start + snippet_length)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def get_document_count(self):
        """Get total number of indexed documents"""
        return len(self.documents)
    
    def get_index_stats(self):
        """Get search index statistics"""
        return {
            'total_documents': len(self.documents),
            'total_terms': len(self.index),
            'average_terms_per_doc': sum(len(positions) for positions in self.index.values()) / len(self.documents) if self.documents else 0
        }
