"""
Document Parser with GROBID integration for enhanced PDF parsing
"""

import os
import json
import magic
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from config import Config


class DocumentParser:
    """Enhanced document parser using GROBID for PDF processing and fallback libraries for other formats"""
    
    def __init__(self, grobid_url: str = "http://localhost:8070"):
        """
        Initialize the document parser with GROBID client
        
        Args:
            grobid_url: URL of the GROBID service
        """
        self.grobid_url = grobid_url
        self.supported_types = Config.SUPPORTED_FILE_TYPES
        
    def validate_file(self, filepath: str) -> Tuple[bool, str, str]:
        """
        Validate if the file can be processed
        
        Args:
            filepath: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, skip_reason, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                return False, "file_not_found", "File does not exist"
            
            # Check file size
            file_size = os.path.getsize(filepath)
            max_size = Config.get_max_file_size_bytes()
            if file_size > max_size:
                return False, "file_too_large", f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum allowed size ({Config.get_max_file_size_mb()}MB)"
            
            # Check file type
            mime_type = magic.from_file(filepath, mime=True)
            if mime_type not in self.supported_types:
                return False, "unsupported_type", f"Unsupported file type: {mime_type}"
            
            # Additional PDF-specific validation
            if mime_type == 'application/pdf':
                # Check if PDF is corrupted or encrypted
                try:
                    import PyPDF2
                    with open(filepath, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        if len(pdf_reader.pages) == 0:
                            return False, "empty_pdf", "PDF file is empty"
                        if len(pdf_reader.pages) > Config.get_max_pages():
                            return False, "too_many_pages", f"PDF has {len(pdf_reader.pages)} pages, maximum allowed is {Config.get_max_pages()}"
                except Exception as e:
                    return False, "corrupt_pdf", f"PDF file appears to be corrupted: {str(e)}"
            
            return True, "", ""
            
        except Exception as e:
            return False, "validation_error", f"Error validating file: {str(e)}"
    
    def parse_document(self, filepath: str, metadata_options: List[str] = None, job_id: str = None) -> Dict[str, Any]:
        """
        Parse a document using GROBID for PDFs and appropriate libraries for other formats
        
        Args:
            filepath: Path to the document to parse
            metadata_options: List of metadata fields to extract
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing parsed document data
        """
        if metadata_options is None:
            metadata_options = ['title', 'author', 'topic']
        
        # Get file type
        mime_type = magic.from_file(filepath, mime=True)
        file_type = self.supported_types.get(mime_type, 'Unknown')
        
        # Parse based on file type
        if file_type == 'PDF':
            return self._parse_pdf_with_grobid(filepath, metadata_options, job_id)
        elif file_type == 'DOCX':
            return self._parse_docx(filepath, metadata_options, job_id)
        elif file_type == 'TXT':
            return self._parse_txt(filepath, metadata_options, job_id)
        elif file_type == 'HTML':
            return self._parse_html(filepath, metadata_options, job_id)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _parse_pdf_with_grobid(self, filepath: str, metadata_options: List[str], job_id: str = None) -> Dict[str, Any]:
        """
        Parse PDF using GROBID for enhanced extraction - only extract requested metadata
        
        Args:
            filepath: Path to the PDF file
            metadata_options: List of metadata fields to extract
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing parsed PDF data
        """
        try:
            # Use GROBID REST API to parse the PDF - only extract header metadata for speed
            with open(filepath, 'rb') as pdf_file:
                files = {'input': pdf_file}
                data = {
                    'generateIDs': '1',
                    'consolidateCitations': '0',  # Disable citation processing for speed
                    'includeRawCitations': '0',   # Disable raw citations for speed
                    'includeRawAffiliations': '0', # Disable affiliations for speed
                    'teiCoordinates': '0'         # Disable coordinates for speed
                }
                
                # Use full text endpoint but with optimized settings for faster processing
                response = requests.post(
                    f"{self.grobid_url}/api/processFulltextDocument",
                    files=files,
                    data=data,
                    timeout=30  # Reduced timeout
                )
                
                if response.status_code != 200:
                    print(f"GROBID API error: {response.status_code}")
                    return self._parse_pdf_fallback(filepath, metadata_options, job_id)
                
                # Extract only requested metadata from GROBID result
                parsed_data = self._extract_grobid_metadata_only(response.text, metadata_options)
                
                # Add common fields
                parsed_data.update({
                    'file_type': 'PDF',
                    'upload_date': datetime.now().isoformat(),
                    'job_id': job_id,
                    'parser': 'GROBID',
                    'file_size': os.path.getsize(filepath)
                })
                
                return parsed_data
            
        except Exception as e:
            print(f"GROBID parsing failed, falling back to PyPDF2: {str(e)}")
            return self._parse_pdf_fallback(filepath, metadata_options, job_id)
    
    def _extract_grobid_metadata_only(self, grobid_result: str, metadata_options: List[str]) -> Dict[str, Any]:
        """
        Extract only requested metadata from GROBID result (XML or BibTeX) for faster processing
        
        Args:
            grobid_result: XML or BibTeX result from GROBID
            metadata_options: List of metadata fields to extract
            
        Returns:
            Dictionary containing only requested metadata
        """
        try:
            # Initialize result dictionary with only requested fields
            result = {}
            
            # Check if result is BibTeX format (starts with @)
            if grobid_result.strip().startswith('@'):
                return self._extract_bibtex_metadata(grobid_result, metadata_options)
            
            # Otherwise, try XML parsing
            from xml.etree import ElementTree as ET
            
            root = ET.fromstring(grobid_result)
            
            # Extract title if requested
            if 'title' in metadata_options:
                title_elem = root.find('.//{http://www.tei-c.org/ns/1.0}titleStmt/{http://www.tei-c.org/ns/1.0}title')
                result['title'] = title_elem.text.strip() if title_elem is not None and title_elem.text else ''
            
            # Extract author if requested
            if 'author' in metadata_options:
                authors = []
                for author in root.findall('.//{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author'):
                    forename = author.find('.//{http://www.tei-c.org/ns/1.0}forename')
                    surname = author.find('.//{http://www.tei-c.org/ns/1.0}surname')
                    if forename is not None and surname is not None:
                        authors.append({
                            'first_name': forename.text.strip() if forename.text else '',
                            'last_name': surname.text.strip() if surname.text else '',
                            'full_name': f"{forename.text.strip()} {surname.text.strip()}".strip()
                        })
                    elif forename is not None:
                        authors.append({
                            'first_name': forename.text.strip() if forename.text else '',
                            'last_name': '',
                            'full_name': forename.text.strip()
                        })
                    elif surname is not None:
                        authors.append({
                            'first_name': '',
                            'last_name': surname.text.strip() if surname.text else '',
                            'full_name': surname.text.strip()
                        })
                result['author'] = authors
            
            # Extract abstract if requested
            if 'abstract' in metadata_options:
                abstract_elem = root.find('.//{http://www.tei-c.org/ns/1.0}profileDesc/{http://www.tei-c.org/ns/1.0}abstract')
                result['abstract'] = ''.join(abstract_elem.itertext()).strip() if abstract_elem is not None else ''
            
            # Extract published date if requested
            if 'published_date' in metadata_options:
                date_elem = root.find('.//{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}monogr/{http://www.tei-c.org/ns/1.0}imprint/{http://www.tei-c.org/ns/1.0}date')
                result['published_date'] = date_elem.text.strip() if date_elem is not None and date_elem.text else ''
            
            # Extract topic/keywords if requested
            if 'topic' in metadata_options:
                keywords = []
                for keyword in root.findall('.//{http://www.tei-c.org/ns/1.0}profileDesc/{http://www.tei-c.org/ns/1.0}textClass/{http://www.tei-c.org/ns/1.0}keywords/{http://www.tei-c.org/ns/1.0}term'):
                    if keyword.text:
                        keywords.append(keyword.text.strip())
                result['topic'] = ', '.join(keywords[:5]) if keywords else ''  # First 5 keywords as topic
            
            # Text field removed for faster parsing
            
            return result
            
        except Exception as e:
            print(f"Error extracting GROBID metadata: {str(e)}")
            return {field: '' for field in metadata_options}
    
    def _extract_bibtex_metadata(self, bibtex_result: str, metadata_options: List[str]) -> Dict[str, Any]:
        """
        Extract metadata from GROBID BibTeX result
        
        Args:
            bibtex_result: BibTeX result from GROBID
            metadata_options: List of metadata fields to extract
            
        Returns:
            Dictionary containing only requested metadata
        """
        result = {}
        
        # Simple BibTeX parsing
        lines = bibtex_result.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('title = {'):
                if 'title' in metadata_options:
                    result['title'] = line.split('{', 1)[1].rsplit('}', 1)[0]
            elif line.startswith('author = {'):
                if 'author' in metadata_options:
                    author_text = line.split('{', 1)[1].rsplit('}', 1)[0]
                    # Parse multiple authors separated by 'and'
                    authors = []
                    for author_part in author_text.split(' and '):
                        author_part = author_part.strip()
                        if author_part:
                            # Try to split into first and last name
                            name_parts = author_part.split(', ')
                            if len(name_parts) == 2:
                                # Last, First format
                                authors.append({
                                    'first_name': name_parts[1].strip(),
                                    'last_name': name_parts[0].strip(),
                                    'full_name': f"{name_parts[1].strip()} {name_parts[0].strip()}".strip()
                                })
                            else:
                                # First Last format or single name
                                name_parts = author_part.split(' ')
                                if len(name_parts) >= 2:
                                    authors.append({
                                        'first_name': ' '.join(name_parts[:-1]).strip(),
                                        'last_name': name_parts[-1].strip(),
                                        'full_name': author_part
                                    })
                                else:
                                    authors.append({
                                        'first_name': '',
                                        'last_name': author_part,
                                        'full_name': author_part
                                    })
                    result['author'] = authors
            elif line.startswith('year = {'):
                if 'published_date' in metadata_options:
                    result['published_date'] = line.split('{', 1)[1].rsplit('}', 1)[0]
            elif line.startswith('doi = {'):
                if 'topic' in metadata_options:
                    doi = line.split('{', 1)[1].rsplit('}', 1)[0]
                    result['topic'] = f"DOI: {doi}"
        
        # Set empty values for other requested fields
        for field in metadata_options:
            if field not in result:
                if field == 'author':
                    result[field] = []
                else:
                    result[field] = ''
        
        # Text field removed for faster parsing
        
        return result
    
    def _extract_grobid_data(self, grobid_result: str, metadata_options: List[str]) -> Dict[str, Any]:
        """
        Extract structured data from GROBID XML result
        
        Args:
            grobid_result: XML result from GROBID
            metadata_options: List of metadata fields to extract
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            from xml.etree import ElementTree as ET
            
            root = ET.fromstring(grobid_result)
            
            # Initialize result dictionary
            result = {
                'text': '',
                'title': '',
                'author': '',
                'abstract': '',
                'published_date': '',
                'topic': '',
                'keywords': [],
                'references': [],
                'sections': [],
                'full_text': ''
            }
            
            # Extract title
            title_elem = root.find('.//{http://www.tei-c.org/ns/1.0}titleStmt/{http://www.tei-c.org/ns/1.0}title')
            if title_elem is not None:
                result['title'] = title_elem.text.strip() if title_elem.text else ''
            
            # Extract authors
            authors = []
            for author in root.findall('.//{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author'):
                forename = author.find('.//{http://www.tei-c.org/ns/1.0}forename')
                surname = author.find('.//{http://www.tei-c.org/ns/1.0}surname')
                if forename is not None and surname is not None:
                    authors.append(f"{forename.text} {surname.text}")
            result['author'] = '; '.join(authors)
            
            # Extract abstract
            abstract_elem = root.find('.//{http://www.tei-c.org/ns/1.0}profileDesc/{http://www.tei-c.org/ns/1.0}abstract')
            if abstract_elem is not None:
                result['abstract'] = ''.join(abstract_elem.itertext()).strip()
            
            # Extract publication date
            date_elem = root.find('.//{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}monogr/{http://www.tei-c.org/ns/1.0}imprint/{http://www.tei-c.org/ns/1.0}date')
            if date_elem is not None:
                result['published_date'] = date_elem.text.strip() if date_elem.text else ''
            
            # Extract full text
            body_elem = root.find('.//{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}body')
            if body_elem is not None:
                full_text = ''.join(body_elem.itertext()).strip()
                result['full_text'] = full_text
                result['text'] = full_text  # For backward compatibility
                
                # Extract sections
                sections = []
                for div in body_elem.findall('.//{http://www.tei-c.org/ns/1.0}div'):
                    head = div.find('.//{http://www.tei-c.org/ns/1.0}head')
                    if head is not None:
                        section_title = head.text.strip() if head.text else ''
                        section_text = ''.join(div.itertext()).strip()
                        sections.append({
                            'title': section_title,
                            'text': section_text
                        })
                result['sections'] = sections
            
            # Extract references
            references = []
            for ref in root.findall('.//{http://www.tei-c.org/ns/1.0}listBibl/{http://www.tei-c.org/ns/1.0}biblStruct'):
                ref_text = ''.join(ref.itertext()).strip()
                if ref_text:
                    references.append(ref_text)
            result['references'] = references
            
            # Extract keywords
            keywords = []
            for keyword in root.findall('.//{http://www.tei-c.org/ns/1.0}profileDesc/{http://www.tei-c.org/ns/1.0}textClass/{http://www.tei-c.org/ns/1.0}keywords/{http://www.tei-c.org/ns/1.0}term'):
                if keyword.text:
                    keywords.append(keyword.text.strip())
            result['keywords'] = keywords
            
            # Set topic from keywords if available
            if keywords and 'topic' in metadata_options:
                result['topic'] = ', '.join(keywords[:5])  # First 5 keywords as topic
            
            return result
            
        except Exception as e:
            print(f"Error extracting GROBID data: {str(e)}")
            return {
                'text': '',
                'title': '',
                'author': '',
                'abstract': '',
                'published_date': '',
                'topic': '',
                'keywords': [],
                'references': [],
                'sections': [],
                'full_text': ''
            }
    
    def _parse_pdf_fallback(self, filepath: str, metadata_options: List[str], job_id: str = None) -> Dict[str, Any]:
        """
        Fallback PDF parsing using PyPDF2 - only extract requested metadata
        
        Args:
            filepath: Path to the PDF file
            metadata_options: List of metadata fields to extract
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing parsed PDF data
        """
        import PyPDF2
        
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Initialize result with only requested fields
            result = {
                'file_type': 'PDF',
                'upload_date': datetime.now().isoformat(),
                'job_id': job_id,
                'parser': 'PyPDF2',
                'file_size': os.path.getsize(filepath),
                'page_count': len(pdf_reader.pages)
            }
            
            # Extract metadata only if requested
            metadata = pdf_reader.metadata or {}
            
            if 'title' in metadata_options:
                result['title'] = metadata.get('/Title', '')
            
            if 'author' in metadata_options:
                author_text = metadata.get('/Author', '')
                if author_text:
                    # Parse multiple authors separated by ';' or ','
                    authors = []
                    for author_part in author_text.replace(';', ',').split(','):
                        author_part = author_part.strip()
                        if author_part:
                            # Try to split into first and last name
                            name_parts = author_part.split(' ')
                            if len(name_parts) >= 2:
                                authors.append({
                                    'first_name': ' '.join(name_parts[:-1]).strip(),
                                    'last_name': name_parts[-1].strip(),
                                    'full_name': author_part
                                })
                            else:
                                authors.append({
                                    'first_name': '',
                                    'last_name': author_part,
                                    'full_name': author_part
                                })
                    result['author'] = authors
                else:
                    result['author'] = []
            
            if 'published_date' in metadata_options:
                result['published_date'] = metadata.get('/CreationDate', '')
            
            # Set empty values for other requested fields
            for field in metadata_options:
                if field not in result:
                    if field == 'author':
                        result[field] = []
                    else:
                        result[field] = ''
            
            # Text field removed for faster parsing
            
            return result
    
    def _parse_docx(self, filepath: str, metadata_options: List[str], job_id: str = None) -> Dict[str, Any]:
        """
        Parse DOCX file using python-docx - only extract requested metadata
        
        Args:
            filepath: Path to the DOCX file
            metadata_options: List of metadata fields to extract
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing parsed DOCX data
        """
        from docx import Document
        
        doc = Document(filepath)
        
        # Initialize result with only requested fields
        result = {
            'file_type': 'DOCX',
            'upload_date': datetime.now().isoformat(),
            'job_id': job_id,
            'parser': 'python-docx',
            'file_size': os.path.getsize(filepath)
        }
        
        # Extract metadata only if requested
        core_props = doc.core_properties
        
        if 'title' in metadata_options:
            result['title'] = core_props.title or ''
        
        if 'author' in metadata_options:
            author_text = core_props.author or ''
            if author_text:
                # Parse multiple authors separated by ';' or ','
                authors = []
                for author_part in author_text.replace(';', ',').split(','):
                    author_part = author_part.strip()
                    if author_part:
                        # Try to split into first and last name
                        name_parts = author_part.split(' ')
                        if len(name_parts) >= 2:
                            authors.append({
                                'first_name': ' '.join(name_parts[:-1]).strip(),
                                'last_name': name_parts[-1].strip(),
                                'full_name': author_part
                            })
                        else:
                            authors.append({
                                'first_name': '',
                                'last_name': author_part,
                                'full_name': author_part
                            })
                result['author'] = authors
            else:
                result['author'] = []
        
        if 'published_date' in metadata_options:
            result['published_date'] = str(core_props.created) if core_props.created else ''
        
        # Set empty values for other requested fields
        for field in metadata_options:
            if field not in result:
                if field == 'author':
                    result[field] = []
                else:
                    result[field] = ''
        
        # Text field removed for faster parsing
        
        return result
    
    def _parse_txt(self, filepath: str, metadata_options: List[str], job_id: str = None) -> Dict[str, Any]:
        """
        Parse TXT file - only extract requested metadata
        
        Args:
            filepath: Path to the TXT file
            metadata_options: List of metadata fields to extract
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing parsed TXT data
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Initialize result with only requested fields
        result = {
            'file_type': 'TXT',
            'upload_date': datetime.now().isoformat(),
            'job_id': job_id,
            'parser': 'built-in',
            'file_size': os.path.getsize(filepath)
        }
        
        # Extract title if requested (use filename)
        if 'title' in metadata_options:
            result['title'] = os.path.basename(filepath)
        
        # Set empty values for other requested fields
        for field in metadata_options:
            if field not in result:
                if field == 'author':
                    result[field] = []
                else:
                    result[field] = ''
        
        # Text field removed for faster parsing
        
        return result
    
    def _parse_html(self, filepath: str, metadata_options: List[str], job_id: str = None) -> Dict[str, Any]:
        """
        Parse HTML file - only extract requested metadata
        
        Args:
            filepath: Path to the HTML file
            metadata_options: List of metadata fields to extract
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing parsed HTML data
        """
        from bs4 import BeautifulSoup
        
        with open(filepath, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize result with only requested fields
        result = {
            'file_type': 'HTML',
            'upload_date': datetime.now().isoformat(),
            'job_id': job_id,
            'parser': 'BeautifulSoup',
            'file_size': os.path.getsize(filepath)
        }
        
        # Extract title if requested
        if 'title' in metadata_options:
            title = soup.find('title')
            result['title'] = title.text.strip() if title else ''
        
        # Set empty values for other requested fields
        for field in metadata_options:
            if field not in result:
                if field == 'author':
                    result[field] = []
                else:
                    result[field] = ''
        
        # Text field removed for faster parsing
        
        return result
    
    def is_grobid_available(self) -> bool:
        """
        Check if GROBID service is available
        
        Returns:
            True if GROBID is available, False otherwise
        """
        try:
            response = requests.get(f"{self.grobid_url}/api/isalive", timeout=5)
            return response.status_code == 200
        except:
            return False
