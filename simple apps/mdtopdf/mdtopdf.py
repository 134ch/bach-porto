import os
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def create_pdf_styles():
    """Create CSS styles for the PDF"""
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
    }
    
    body {
        font-family: 'Arial', 'Helvetica', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
    }
    
    h1 {
        font-size: 24pt;
        font-weight: bold;
        margin-top: 0;
        margin-bottom: 20px;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    
    h2 {
        font-size: 20pt;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 15px;
        color: #34495e;
    }
    
    h3 {
        font-size: 16pt;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 12px;
        color: #34495e;
    }
    
    h4 {
        font-size: 14pt;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #34495e;
    }
    
    p {
        margin-bottom: 12px;
        text-align: justify;
    }
    
    a {
        color: #3498db;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    ul, ol {
        margin-bottom: 15px;
        padding-left: 30px;
    }
    
    li {
        margin-bottom: 8px;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    
    pre {
        background-color: #f4f4f4;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        margin-bottom: 15px;
        border-left: 4px solid #3498db;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
    }
    
    blockquote {
        margin: 20px 0;
        padding: 10px 20px;
        background-color: #f9f9f9;
        border-left: 4px solid #3498db;
        font-style: italic;
    }
    
    hr {
        border: none;
        border-top: 2px solid #e0e0e0;
        margin: 30px 0;
    }
    
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 20px auto;
        border-radius: 5px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    
    table th,
    table td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: left;
    }
    
    table th {
        background-color: #f4f4f4;
        font-weight: bold;
    }
    
    strong, b {
        font-weight: bold;
        color: #2c3e50;
    }
    
    em, i {
        font-style: italic;
    }
    
    .video-link {
        display: block;
        padding: 15px;
        background-color: #e8f4f8;
        border: 2px solid #3498db;
        border-radius: 5px;
        margin: 20px 0;
        text-align: center;
        font-weight: bold;
    }
    
    .video-link::before {
        content: "🎥 ";
    }
    """
    return css_content

def preprocess_markdown(md_content):
    """Preprocess markdown content before conversion"""
    # Convert video links to styled blocks
    import re
    
    # Pattern to match video links
    video_pattern = r'\[Video:?\s*([^\]]+)\]\(([^\)]+)\)'
    
    def replace_video(match):
        platform = match.group(1)
        url = match.group(2)
        return f'\n<div class="video-link"><a href="{url}" target="_blank">Watch Video: {platform}</a><br><small>{url}</small></div>\n'
    
    md_content = re.sub(video_pattern, replace_video, md_content)
    
    return md_content

def markdown_to_pdf(md_file_path, output_pdf_path):
    """Convert a single Markdown file to PDF"""
    try:
        # Read markdown content
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Preprocess markdown
        md_content = preprocess_markdown(md_content)
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=[
                'extra',  # Includes tables, fenced code blocks, etc.
                'codehilite',  # Syntax highlighting
                'nl2br',  # Newline to <br>
                'sane_lists',  # Better list handling
            ]
        )
        
        # Wrap HTML in proper structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{md_file_path.stem}</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Create CSS
        css_styles = create_pdf_styles()
        font_config = FontConfiguration()
        
        # Convert HTML to PDF
        HTML(string=full_html).write_pdf(
            output_pdf_path,
            stylesheets=[CSS(string=css_styles, font_config=font_config)],
            font_config=font_config
        )
        
        return True
    
    except Exception as e:
        print(f"Error converting {md_file_path.name}: {str(e)}")
        return False

def process_folder(input_folder, output_folder):
    """Process all Markdown files in a folder and convert to PDF"""
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all markdown files
    md_files = list(input_path.glob('*.md'))
    
    if not md_files:
        print(f"No Markdown files found in {input_folder}")
        return
    
    print(f"Found {len(md_files)} Markdown files to convert...")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    
    for md_file in md_files:
        print(f"\nConverting: {md_file.name}")
        
        # Create output filename
        pdf_filename = md_file.stem + '.pdf'
        pdf_file_path = output_path / pdf_filename
        
        # Convert to PDF
        if markdown_to_pdf(md_file, pdf_file_path):
            print(f"✓ Created: {pdf_filename}")
            success_count += 1
        else:
            print(f"✗ Failed: {pdf_filename}")
            failed_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("Conversion Complete!")
    print("="*60)
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(md_files)}")
    print(f"\nOutput folder: {output_folder}")

def main():
    print("="*60)
    print("Markdown to PDF Bulk Converter")
    print("="*60)
    print()
    
    # Get input and output folders
    input_folder = input("Enter input folder path (or press Enter for 'output_md'): ").strip()
    if not input_folder:
        input_folder = "output_md"
    
    output_folder = input("Enter output folder path (or press Enter for 'output_pdf'): ").strip()
    if not output_folder:
        output_folder = "output_pdf"
    
    # Check if input folder exists
    if not Path(input_folder).exists():
        print(f"\n❌ Error: Input folder '{input_folder}' does not exist!")
        return
    
    print()
    process_folder(input_folder, output_folder)

if __name__ == "__main__":
    main()