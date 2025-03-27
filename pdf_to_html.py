#!/usr/bin/env python3

import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTLine, LTRect
from bs4 import BeautifulSoup
import re

def extract_text_from_pdf(pdf_path):
    """Extract text and layout information from PDF."""
    text_content = []
    try:
        for page_layout in extract_pages(pdf_path):
            page_text = []
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if text:
                        # Get the position and size of the text
                        x, y = element.x0, element.y0
                        width, height = element.width, element.height
                        page_text.append({
                            'text': text,
                            'x': x,
                            'y': y,
                            'width': width,
                            'height': height
                        })
            if page_text:  # Only append if we found text on the page
                print(f"Found {len(page_text)} text blocks on page {len(text_content) + 1}")
                text_content.append(page_text)
            else:
                print(f"Warning: No text found on page {len(text_content) + 1}")
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise
    return text_content

def create_html_from_text(text_content):
    """Convert extracted text to HTML using BeautifulSoup."""
    try:
        soup = BeautifulSoup('', 'html.parser')
        
        # Create basic HTML structure
        html = soup.new_tag('html')
        head = soup.new_tag('head')
        meta = soup.new_tag('meta')
        meta['charset'] = 'utf-8'
        head.append(meta)
        
        title = soup.new_tag('title')
        title.string = 'Converted PDF'
        head.append(title)
        html.append(head)
        
        body = soup.new_tag('body')
        html.append(body)
        
        # Add CSS for basic styling
        style = soup.new_tag('style')
        style.string = """
            .page { margin-bottom: 2em; padding: 1em; border-bottom: 1px solid #ccc; }
            .text-block { margin: 0.5em 0; }
            .header { font-weight: bold; font-size: 1.2em; }
            .footer { font-size: 0.8em; color: #666; }
        """
        head.append(style)
        
        # Process each page
        for page_num, page in enumerate(text_content, 1):
            print(f"Processing page {page_num} with {len(page)} text blocks")
            page_div = soup.new_tag('div', attrs={'class': 'page'})
            page_div.append(soup.new_tag('h2', string=f'Page {page_num}'))
            
            # Sort text blocks by y-coordinate (top to bottom)
            sorted_blocks = sorted(page, key=lambda x: -x['y'])
            
            for block in sorted_blocks:
                text_block = soup.new_tag('div', attrs={'class': 'text-block'})
                text = block['text']
                
                # Basic formatting rules
                if len(text) < 50 and text.isupper():
                    text_block['class'] = 'header'
                elif len(text) < 30 and text.isdigit():
                    text_block['class'] = 'footer'
                
                text_block.string = text
                page_div.append(text_block)
            
            body.append(page_div)
        
        soup.append(html)
        result = soup.prettify()
        print(f"Generated HTML length: {len(result)} characters")
        return result
    except Exception as e:
        print(f"Error creating HTML: {str(e)}")
        raise

def convert_pdf_to_html(pdf_path, output_dir='html_output'):
    """Convert PDF to HTML and save the result."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the PDF filename without extension
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f'{pdf_name}.html')
        
        # Extract text from PDF
        print(f"Extracting text from {pdf_path}...")
        text_content = extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(text_content)} pages of content")
        
        if not text_content:
            print("Warning: No text content extracted from PDF")
            return
        
        # Convert to HTML
        print("Converting to HTML...")
        html_content = create_html_from_text(text_content)
        
        if not html_content:
            print("Warning: No HTML content generated")
            return
        
        # Save the HTML file
        print(f"Saving HTML to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            bytes_written = f.write(html_content)
            print(f"Wrote {bytes_written} bytes to file")
        
        # Verify the file was written
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"File created successfully. Size: {file_size} bytes")
        else:
            print("Warning: File was not created!")
            
        print(f"Conversion complete! HTML file saved to {output_path}")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        raise

def main():
    # Directory containing PDF files
    pdf_dir = 'reference'
    
    # Process all PDF files in the directory
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"\nProcessing {filename}...")
            try:
                convert_pdf_to_html(pdf_path)
            except Exception as e:
                print(f"Failed to process {filename}: {str(e)}")

if __name__ == '__main__':
    main() 