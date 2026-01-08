import PyPDF2
import re
from typing import List, Dict
from io import BytesIO


class PDFProcessor:
    """Process PDF files: extract text, chunk into paragraphs, and prepare for embedding"""
    
    def __init__(self, min_chunk_size: int = 100, max_chunk_size: int = 1000):
        """
        Initialize PDF processor
        
        Args:
            min_chunk_size: Minimum characters per chunk
            max_chunk_size: Maximum characters per chunk
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
    
    def extract_text_from_pdf(self, file_bytes: bytes, filename: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF file page by page
        
        Args:
            file_bytes: PDF file content as bytes
            filename: Original filename
            
        Returns:
            List of dicts with page number and text content
        """
        pdf_file = BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        pages_data = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            if text.strip():  # Only include pages with text
                pages_data.append({
                    'page_number': page_num,
                    'text': text,
                    'filename': filename
                })
        
        return pages_data
    
    def chunk_text_by_paragraphs(self, text: str, page_number: int, filename: str) -> List[Dict[str, any]]:
        """
        Split text into paragraph-based chunks
        
        Args:
            text: Text content to chunk
            page_number: Source page number
            filename: Source filename
            
        Returns:
            List of chunk dictionaries with metadata
        """
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds max size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > self.max_chunk_size:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk)
                current_chunk = para
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add remaining chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk)
        
        # Create chunk objects with metadata
        chunk_objects = []
        for idx, chunk_text in enumerate(chunks, start=1):
            chunk_objects.append({
                'text': chunk_text,
                'metadata': {
                    'filename': filename,
                    'page_number': page_number,
                    'chunk_index': idx,
                    'chunk_size': len(chunk_text)
                }
            })
        
        return chunk_objects
    
    def process_pdf(self, file_bytes: bytes, filename: str) -> Dict[str, any]:
        """
        Main processing pipeline: extract text and create chunks
        
        Args:
            file_bytes: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with chunks and statistics
        """
        # Extract text from all pages
        pages_data = self.extract_text_from_pdf(file_bytes, filename)
        
        if not pages_data:
            return {
                'success': False,
                'error': 'No text content found in PDF',
                'chunks': [],
                'stats': {}
            }
        
        # Process each page into chunks
        all_chunks = []
        for page_data in pages_data:
            page_chunks = self.chunk_text_by_paragraphs(
                text=page_data['text'],
                page_number=page_data['page_number'],
                filename=filename
            )
            all_chunks.extend(page_chunks)
        
        # Calculate statistics
        stats = {
            'total_pages': len(pages_data),
            'total_chunks': len(all_chunks),
            'filename': filename,
            'avg_chunk_size': sum(c['metadata']['chunk_size'] for c in all_chunks) // len(all_chunks) if all_chunks else 0
        }
        
        return {
            'success': True,
            'chunks': all_chunks,
            'stats': stats
        }


def process_pdf_file(file_bytes: bytes, filename: str) -> Dict[str, any]:
    """
    Convenience function to process a PDF file
    
    Args:
        file_bytes: PDF file content as bytes
        filename: Original filename
        
    Returns:
        Processing results with chunks and statistics
    """
    processor = PDFProcessor()
    return processor.process_pdf(file_bytes, filename)
