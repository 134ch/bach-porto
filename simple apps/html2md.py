import os
from bs4 import BeautifulSoup
from pathlib import Path
import re

def extract_video_embed(soup):
    """Extract video embed URLs (YouTube, Loom, etc.)"""
    videos = []
    
    # Find iframes (YouTube, Loom embeds)
    iframes = soup.find_all('iframe')
    for iframe in iframes:
        src = iframe.get('src', '')
        # Filter out non-video iframes (like Stripe)
        if any(domain in src for domain in ['youtube.com', 'loom.com', 'vimeo.com', 'wistia']):
            videos.append(src)
    
    return videos

def extract_images(soup):
    """Extract image URLs from the main content"""
    images = []
    
    # Find images in the main content area
    main_content = soup.find('div', class_=lambda x: x and 'skool-editor2' in x)
    if main_content:
        imgs = main_content.find_all('img')
        for img in imgs:
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            if src and 'assets.skool.com' in src:  # Only skool content images
                images.append({'src': src, 'alt': alt, 'title': title})
    
    return images

def clean_text(text):
    """Clean up text content"""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def process_content_element(element, level=0):
    """Recursively process content elements and convert to markdown"""
    if element.name is None:  # Text node
        return clean_text(element.string) if element.string else ""
    
    markdown = ""
    
    # Headings
    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(element.name[1])
        text = element.get_text(strip=True)
        markdown = f"\n\n{'#' * level} {text}\n\n"
    
    # Paragraphs
    elif element.name == 'p':
        text = ""
        for child in element.children:
            if child.name == 'strong' or child.name == 'b':
                text += f"**{child.get_text(strip=True)}**"
            elif child.name == 'em' or child.name == 'i':
                text += f"*{child.get_text(strip=True)}*"
            elif child.name == 'a':
                link_text = child.get_text(strip=True)
                link_url = child.get('href', '')
                text += f"[{link_text}]({link_url})"
            elif child.name == 'code':
                text += f"`{child.get_text(strip=True)}`"
            elif child.string:
                text += child.string
            else:
                text += child.get_text()
        
        text = clean_text(text)
        if text:
            markdown = f"{text}\n\n"
    
    # Lists
    elif element.name == 'ul':
        for li in element.find_all('li', recursive=False):
            li_text = ""
            for child in li.children:
                if child.name == 'p':
                    li_text += process_content_element(child).strip()
                elif child.name == 'strong' or child.name == 'b':
                    li_text += f"**{child.get_text(strip=True)}**"
                elif child.name == 'em' or child.name == 'i':
                    li_text += f"*{child.get_text(strip=True)}*"
                elif child.name == 'a':
                    link_text = child.get_text(strip=True)
                    link_url = child.get('href', '')
                    li_text += f"[{link_text}]({link_url})"
                elif child.string:
                    li_text += child.string
                else:
                    li_text += child.get_text()
            
            li_text = clean_text(li_text)
            if li_text:
                markdown += f"- {li_text}\n"
        markdown += "\n"
    
    elif element.name == 'ol':
        for idx, li in enumerate(element.find_all('li', recursive=False), 1):
            li_text = ""
            for child in li.children:
                if child.name == 'p':
                    li_text += process_content_element(child).strip()
                elif child.name == 'strong' or child.name == 'b':
                    li_text += f"**{child.get_text(strip=True)}**"
                elif child.name == 'em' or child.name == 'i':
                    li_text += f"*{child.get_text(strip=True)}*"
                elif child.name == 'a':
                    link_text = child.get_text(strip=True)
                    link_url = child.get('href', '')
                    li_text += f"[{link_text}]({link_url})"
                elif child.string:
                    li_text += child.string
                else:
                    li_text += child.get_text()
            
            li_text = clean_text(li_text)
            if li_text:
                markdown += f"{idx}. {li_text}\n"
        markdown += "\n"
    
    # Horizontal rule
    elif element.name == 'hr':
        markdown = "\n---\n\n"
    
    # Blockquote
    elif element.name == 'blockquote':
        text = element.get_text(strip=True)
        lines = text.split('\n')
        markdown = '\n'.join([f"> {line}" for line in lines if line.strip()]) + "\n\n"
    
    # Code blocks
    elif element.name == 'pre':
        code = element.get_text(strip=True)
        markdown = f"\n```\n{code}\n```\n\n"
    
    # Images (embedded in content)
    elif element.name == 'img':
        src = element.get('src', '')
        alt = element.get('alt', '')
        title = element.get('title', '')
        if src and 'assets.skool.com' in src:
            markdown = f"\n![{alt}]({src})\n\n"
    
    # Links
    elif element.name == 'a':
        link_text = element.get_text(strip=True)
        link_url = element.get('href', '')
        markdown = f"[{link_text}]({link_url})"
    
    # Strong/Bold
    elif element.name in ['strong', 'b']:
        markdown = f"**{element.get_text(strip=True)}**"
    
    # Emphasis/Italic
    elif element.name in ['em', 'i']:
        markdown = f"*{element.get_text(strip=True)}*"
    
    return markdown

def extract_main_content(soup):
    """Extract the main content text and convert to markdown"""
    markdown_content = ""
    
    # Find the main content area (the rich text editor content)
    main_content = soup.find('div', class_=lambda x: x and 'skool-editor2' in x)
    
    if main_content:
        for element in main_content.children:
            if element.name:  # Skip pure text nodes at root level
                markdown_content += process_content_element(element)
    
    return clean_text(markdown_content)

def extract_title(soup):
    """Extract the module/lesson title"""
    # Try to find the title in the module wrapper
    title_elem = soup.find('div', class_=lambda x: x and 'ModuleTitle' in x if x else False)
    if title_elem:
        return title_elem.get_text(strip=True)
    
    # Fallback to page title
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        # Clean up the title (remove site name, etc.)
        title = title.split('·')[0].strip()
        title = title.split('-')[0].strip() if '-' in title else title
        return title
    
    return "Untitled"

def html_to_markdown(html_content):
    """Convert HTML content to Markdown"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract components
    title = extract_title(soup)
    videos = extract_video_embed(soup)
    content = extract_main_content(soup)
    
    # Build markdown document
    markdown = f"# {title}\n\n"
    
    # Add videos
    if videos:
        for video in videos:
            # Convert embed URLs to full URLs if needed
            if 'youtube.com/embed/' in video:
                video_id = video.split('youtube.com/embed/')[1].split('?')[0]
                markdown += f"[Video: YouTube]({video})\n\n"
            elif 'loom.com/embed/' in video:
                markdown += f"[Video: Loom]({video})\n\n"
            else:
                markdown += f"[Video]({video})\n\n"
    
    # Add main content
    markdown += content
    
    return markdown

def process_folder(input_folder, output_folder):
    """Process all HTML files in a folder"""
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each HTML file
    html_files = list(input_path.glob('*.html'))
    
    if not html_files:
        print(f"No HTML files found in {input_folder}")
        return
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    for html_file in html_files:
        print(f"\nProcessing: {html_file.name}")
        
        try:
            # Read HTML content
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Convert to Markdown
            markdown_content = html_to_markdown(html_content)
            
            # Create output filename (same name but .md extension)
            output_filename = html_file.stem + '.md'
            output_file = output_path / output_filename
            
            # Write Markdown file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✓ Created: {output_filename}")
        
        except Exception as e:
            print(f"✗ Error processing {html_file.name}: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"Output folder: {output_folder}")

if __name__ == "__main__":
    # Configuration
    INPUT_FOLDER = "input_html"  # Folder containing HTML files
    OUTPUT_FOLDER = "output_md"  # Folder for markdown files
    
    print("="*50)
    print("HTML to Markdown Converter")
    print("="*50)
    
    # You can modify these paths or make them command-line arguments
    input_folder = input("Enter input folder path (or press Enter for 'input_html'): ").strip()
    if not input_folder:
        input_folder = INPUT_FOLDER
    
    output_folder = input("Enter output folder path (or press Enter for 'output_md'): ").strip()
    if not output_folder:
        output_folder = OUTPUT_FOLDER
    
    process_folder(input_folder, output_folder)