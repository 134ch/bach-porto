import os
import re
import csv
from pathlib import Path

def extract_module_number(filename):
    """Extract module number from filename"""
    # Try to find a number at the start of the filename
    # Examples: "3. Step 1 Call Intro.md", "Module 4.md", "7 - Introduction.md"
    match = re.match(r'^(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def extract_first_heading(md_content):
    """Extract the first # heading from markdown content"""
    lines = md_content.split('\n')
    for line in lines:
        line = line.strip()
        # Match heading that starts with exactly one #
        if re.match(r'^#\s+(.+)', line):
            # Remove the # and any extra whitespace
            heading = re.sub(r'^#\s+', '', line).strip()
            return heading
    return "No Title"

def detect_video_source(url):
    """Detect video source from URL"""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    elif 'loom.com' in url_lower:
        return 'Loom'
    elif 'vimeo.com' in url_lower:
        return 'Vimeo'
    elif 'wistia.com' in url_lower or 'wistia.net' in url_lower:
        return 'Wistia'
    elif 'vidyard.com' in url_lower:
        return 'Vidyard'
    elif 'streamable.com' in url_lower:
        return 'Streamable'
    else:
        return 'Other'

def extract_video_links(md_content):
    """Extract all video links from markdown content"""
    video_links = []
    
    # Pattern 1: [Video: Platform](URL) or [Video](URL)
    pattern1 = r'\[Video:?\s*[^\]]*\]\(([^\)]+)\)'
    matches1 = re.findall(pattern1, md_content)
    video_links.extend(matches1)
    
    # Pattern 2: Direct URLs that contain video platforms
    # Look for URLs in markdown links that might be videos
    pattern2 = r'\[([^\]]+)\]\((https?://[^\)]+(?:youtube|loom|vimeo|wistia)[^\)]+)\)'
    matches2 = re.findall(pattern2, md_content)
    video_links.extend([url for text, url in matches2])
    
    # Pattern 3: Bare URLs (if any) containing video platforms
    pattern3 = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|loom\.com|vimeo\.com|wistia\.com|wistia\.net)/[^\s\)]+)'
    matches3 = re.findall(pattern3, md_content)
    video_links.extend(matches3)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in video_links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    
    return unique_links

def process_markdown_files(input_folder):
    """Process all markdown files and extract video information"""
    input_path = Path(input_folder)
    
    # Find all markdown files
    md_files = list(input_path.glob('*.md'))
    
    if not md_files:
        print(f"No Markdown files found in {input_folder}")
        return []
    
    print(f"Found {len(md_files)} Markdown files")
    print("="*60)
    
    video_data = []
    
    for md_file in md_files:
        print(f"\nProcessing: {md_file.name}")
        
        # Extract module number from filename
        module_num = extract_module_number(md_file.name)
        
        if module_num is None:
            print(f"  ⚠ Could not extract module number, skipping...")
            continue
        
        try:
            # Read markdown content
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Extract first heading (course title)
            course_title = extract_first_heading(md_content)
            print(f"  Module: {module_num}")
            print(f"  Title: {course_title}")
            
            # Extract video links
            video_links = extract_video_links(md_content)
            
            if video_links:
                print(f"  Found {len(video_links)} video(s)")
                
                # If multiple videos, number them as x.1, x.2, x.3, etc.
                for idx, link in enumerate(video_links, 1):
                    video_source = detect_video_source(link)
                    
                    if len(video_links) == 1:
                        module_display = str(module_num)
                    else:
                        module_display = f"{module_num}.{idx}"
                    
                    video_data.append({
                        'module': module_num,
                        'module_display': module_display,
                        'sub_index': idx,
                        'link': link,
                        'course_title': course_title,
                        'video_source': video_source
                    })
                    
                    print(f"    {module_display}. {video_source}: {link[:60]}...")
            else:
                print(f"  No videos found")
                # Still add entry but with no video
                video_data.append({
                    'module': module_num,
                    'module_display': str(module_num),
                    'sub_index': 0,
                    'link': '',
                    'course_title': course_title,
                    'video_source': 'N/A'
                })
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    return video_data

def save_to_csv(video_data, output_file):
    """Save video data to CSV file"""
    if not video_data:
        print("\nNo data to save!")
        return
    
    # Sort by module number, then by sub_index
    video_data.sort(key=lambda x: (x['module'], x['sub_index']))
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Module Number', 'Link', 'Course Title', 'Video Source'])
        
        # Write data
        for item in video_data:
            writer.writerow([
                item['module_display'],
                item['link'],
                item['course_title'],
                item['video_source']
            ])
    
    print(f"\n✓ CSV file created: {output_file}")

def main():
    print("="*60)
    print("Video Link Extractor - Markdown to CSV")
    print("="*60)
    print()
    
    # Get input folder
    input_folder = input("Enter input folder path (or press Enter for 'output_md'): ").strip()
    if not input_folder:
        input_folder = "output_md"
    
    # Check if input folder exists
    if not Path(input_folder).exists():
        print(f"\n❌ Error: Input folder '{input_folder}' does not exist!")
        return
    
    # Get output CSV filename
    output_file = input("Enter output CSV filename (or press Enter for 'video_links.csv'): ").strip()
    if not output_file:
        output_file = "video_links.csv"
    
    # Make sure it has .csv extension
    if not output_file.endswith('.csv'):
        output_file += '.csv'
    
    print()
    
    # Process files
    video_data = process_markdown_files(input_folder)
    
    # Save to CSV
    if video_data:
        save_to_csv(video_data, output_file)
        
        # Summary
        print("\n" + "="*60)
        print("Summary:")
        print("="*60)
        video_count = sum(1 for item in video_data if item['link'])
        print(f"Total modules processed: {len(set(item['module'] for item in video_data))}")
        print(f"Total videos found: {video_count}")
        print(f"Modules without videos: {sum(1 for item in video_data if not item['link'])}")
    else:
        print("\n❌ No video data extracted!")

if __name__ == "__main__":
    main()