import yaml
import os
import re
import unicodedata
from fpdf import FPDF
from fpdf.enums import XPos, YPos

def slugify(text):
    """
    Converts to lowercase, removes non-ascii characters, 
    and replaces spaces/special chars with underscores.
    """
    if not text:
        return "unknown"
    # Normalize unicode characters to their closest ascii representation
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and replace non-alphanumeric with underscores
    text = re.sub(r'[^a-zA-Z0-0\s]', '', text).lower()
    text = re.sub(r'[\s]+', '_', text.strip())
    # Remove duplicate underscores
    text = re.sub(r'_{2,}', '_', text)
    return text

class CV(FPDF):
    def __init__(self, data):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.data = data
        self.primary_blue = (0, 102, 204)
        self.text_black = (20, 20, 20)
        self.text_gray = (80, 80, 80)
        self.border_gray = (200, 200, 200)
        
        self.margin_x = 7.5 # Reduced to fit wider columns
        self.margin_y = 10 # Slightly tighter
        self.page_width = 210
        self.col1_width = 115
        self.col2_width = 74 # User requested
        self.gutter = 6


        
        self.set_auto_page_break(auto=True, margin=self.margin_y)
        
        # Setup Unicode fonts (Arial for Hungarian support)
        self.unicode_font = "Arial"
        self.setup_fonts()
        
        # Default labels (English)
        self.labels = {
            'summary': 'SUMMARY',
            'experience': 'EXPERIENCE',
            'projects': 'PROJECTS',
            'education': 'EDUCATION',
            'languages': 'LANGUAGES',
            'skills': 'SKILLS',
            'interests': 'INTERESTS'
        }
        # Override with custom labels if provided in the data
        if 'labels' in data:
            self.labels.update(data['labels'])

    def setup_fonts(self):
        """ Register Arial font for Unicode (Hungarian) character support. """
        font_dir = "C:\\Windows\\Fonts"
        fonts = [
            {"style": "", "file": "arial.ttf"},
            {"style": "B", "file": "arialbd.ttf"},
            {"style": "I", "file": "ariali.ttf"},
            {"style": "BI", "file": "arialbi.ttf"}
        ]
        
        for f in fonts:
            path = os.path.join(font_dir, f["file"])
            if os.path.exists(path):
                try:
                    self.add_font(self.unicode_font, f["style"], path)
                except Exception as e:
                    print(f"Warning: Failed to load font {path}: {e}")
            else:
                print(f"Warning: Font file not found: {path}")

    def clean_text(self, text, is_block=False):
        if not text: return ""
        replacements = {
            '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2022': '*'
        }
        for old, new in replacements.items():
            text = str(text).replace(old, new)
        
        if is_block:
            # Replace newlines and multiple spaces with a single space to prevent "airy" stretching
            text = re.sub(r'\s+', ' ', text).strip()
        return text

    def draw_icon_text(self, icon_name, text, x_offset, link=None):
        icon_path = os.path.join('assets', icon_name)
        icon_size = 3.5
        if os.path.exists(icon_path):
            self.image(icon_path, x=self.get_x() + self.c_margin, y=self.get_y() + 0.8, w=icon_size)
            self.set_x(self.get_x() + icon_size + 1.5)
        
        self.set_font(self.unicode_font, "", 9)
        if link:
            self.set_text_color(*self.primary_blue)
        else:
            self.set_text_color(*self.text_gray)
            
        # We use cell to keep things on the same line but need to manage manual wrapping if needed
        # Reduced padding from 6 to 2.5 to make it less "airy"
        text_w = self.get_string_width(self.clean_text(text)) + 2.5
        self.cell(text_w, 5, self.clean_text(text), link=link)
        return text_w

    def header_section(self):
        self.set_y(self.margin_y)
        
        # Check if profile picture is requested
        has_picture = 'image' in self.data and self.data['image']
        pic_size = 28 if has_picture else 0 # Was 32
        
        if has_picture:
            pic_path = self.data['image']
            if os.path.exists(pic_path):
                # Render the actual image
                self.image(pic_path, x=self.page_width - self.margin_x - pic_size, y=self.margin_y, w=pic_size, h=pic_size)
            else:
                # Profile Picture Placeholder (White box - top right) if file missing
                self.set_draw_color(*self.border_gray)
                self.set_fill_color(255, 255, 255)
                self.rect(self.page_width - self.margin_x - pic_size, self.margin_y, pic_size, pic_size, 'DF')
        
        # Name
        self.set_x(self.margin_x)
        self.set_font(self.unicode_font, "B", 24) # Was 26
        self.set_text_color(*self.text_black)
        name_width = self.page_width - self.margin_x*2 - pic_size - 5
        self.multi_cell(name_width, 10, self.clean_text(self.data['name']).upper(), border=0, align='L', # Was 12
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Title
        if self.data.get('title'):
            self.set_x(self.margin_x)
            self.set_font(self.unicode_font, "B", 12) # Was 13
            self.set_text_color(*self.primary_blue)
            self.multi_cell(name_width, 7, self.clean_text(self.data['title']), border=0, align='L', # Was 8
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Contact Info with Icons
        self.ln(2)
        self.set_x(self.margin_x)
        
        # Row 1: Phone, Email, Location
        if self.data['contact'].get('phone'):
            self.draw_icon_text('phone.png', self.data['contact']['phone'], self.margin_x)
        
        if self.data['contact'].get('email'):
            email = self.data['contact']['email']
            self.draw_icon_text('envelope-simple.png', email, self.margin_x, link=f"mailto:{email}")
        
        if self.data['contact'].get('location'):
            self.draw_icon_text('map-pin.png', self.data['contact']['location'], self.margin_x)
        self.ln(6)
        
        # Row 2: Socials (if any)
        if self.data['contact'].get('github') or self.data['contact'].get('linkedin'):
            self.set_x(self.margin_x)
            if self.data['contact'].get('github'):
                github = self.data['contact']['github']
                gh_link = github if github.startswith('http') else f"https://{github}"
                self.draw_icon_text('github-logo.png', github, self.margin_x, link=gh_link)
            if self.data['contact'].get('linkedin'):
                linkedin = self.data['contact']['linkedin']
                ln_link = linkedin if linkedin.startswith('http') else f"https://{linkedin}"
                self.draw_icon_text('linkedin-logo.png', linkedin, self.margin_x, link=ln_link)
            self.ln(6)
        
        # Ensure the line is below the profile picture
        pic_bottom = self.margin_y + pic_size
        if self.get_y() < pic_bottom:
            self.set_y(pic_bottom)
        
        self.ln(4)
        # Separator Line
        self.set_draw_color(*self.primary_blue)
        self.set_line_width(0.6)
        self.line(self.margin_x, self.get_y(), self.page_width - self.margin_x, self.get_y())
        self.ln(3) # Was 4
        return self.get_y()

    def section_header(self, title, width, x_pos):
        self.set_xy(x_pos, self.get_y())
        self.set_font(self.unicode_font, "B", 10.5) # Was 11
        self.set_text_color(0, 0, 0)
        self.multi_cell(width, 6, title, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT) # Was 7
        
        y = self.get_y()
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(x_pos, y, x_pos + width, y)
        self.ln(3) # Was 4

    def generate(self, output_file):
        self.add_page()
        start_y = self.header_section()
        header_page = self.page  # Save the page number the header is on
        # We save the Y position after header
        col1_x = self.margin_x
        col2_x = self.margin_x + self.col1_width + self.gutter
        
        # --- LEFT COLUMN (Experience) ---
        if 'experience' in self.data and self.data['experience']:
            self.set_xy(col1_x, start_y)
            self.section_header(self.labels.get('experience', 'EXPERIENCE'), self.col1_width, col1_x)
            
            for job in self.data['experience']:
                # Job Header
                self.set_x(col1_x)
                self.set_font(self.unicode_font, "B", 9.5) # Was 10
                self.set_text_color(*self.text_black)
                self.multi_cell(self.col1_width, 4.2, self.clean_text(job['role']), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                self.set_x(col1_x)
                self.set_font(self.unicode_font, "B", 9.5) # Was 10
                self.set_text_color(*self.primary_blue)
                self.multi_cell(self.col1_width, 4.2, self.clean_text(job['company']), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                self.set_x(col1_x)
                self.set_font(self.unicode_font, "I", 8)
                self.set_text_color(*self.text_gray)
                
                # Use Icons for Period and Location
                p_w = self.draw_icon_text('calendar-gray.png', job['period'], col1_x)
                self.set_x(col1_x + p_w + 4) # Gap between items
                self.draw_icon_text('map-pin-gray.png', job['location'], col1_x)
                self.ln(5)
                
                # Highlights
                self.set_font(self.unicode_font, "", 8.5) # Was 9
                self.set_text_color(*self.text_black)
                for point in job['highlights']:
                    self.cell(4, 3.8, "\u2022" + " ") # Reduced line weight/height
                    self.multi_cell(self.col1_width - 5, 3.8, self.clean_text(point, is_block=True), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.ln(2.5) # Was 3

        # --- PROJECTS ---
        if 'projects' in self.data and self.data['projects']:
            if self.get_y() > 220: # Prevent orphan project header
                self.add_page()
                self.set_y(self.margin_y)
            
            self.section_header(self.labels.get('projects', 'PROJECTS'), self.col1_width, col1_x)
            for project in self.data['projects']:
                # Project Name
                self.set_x(col1_x)
                self.set_font(self.unicode_font, "B", 9.5) # Was 10
                self.set_text_color(*self.text_black)
                self.multi_cell(self.col1_width, 4.2, self.clean_text(project['name']), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT) # Was 5
                
                # Optional Link (Blue)
                if 'link' in project:
                    self.set_x(col1_x)
                    p_link = project['link']
                    full_link = p_link if p_link.startswith('http') else f"https://{p_link}"
                    
                    if "github.com" in p_link.lower():
                        self.draw_icon_text('github-logo-gray.png', p_link, col1_x, link=full_link)
                    else:
                        self.set_font(self.unicode_font, "I", 8)
                        self.set_text_color(*self.primary_blue)
                        self.cell(self.col1_width, 4, self.clean_text(p_link), link=full_link)
                    self.ln(5)
                
                # Description
                self.set_x(col1_x)
                self.set_font(self.unicode_font, "", 8.5) # Was 9
                self.set_text_color(*self.text_black)
                self.multi_cell(self.col1_width, 3.6, self.clean_text(project['description'], is_block=True), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT) 
                
                # Highlights (if any)
                if 'highlights' in project:
                    for point in project['highlights']:
                        self.set_x(col1_x + self.c_margin)
                        self.cell(4, 3.8, "\u2022" + " ")
                        self.multi_cell(self.col1_width - 5, 3.8, self.clean_text(point, is_block=True), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                self.ln(2.5) # Was 3
        

        # --- RIGHT COLUMN (Everything else) ---
        # Reset to the page where header finished to avoid slipping to Page 2
        self.page = header_page # Essential fix for stable 2-column layout
        self.set_xy(col2_x, start_y)
        
        # Summary (Optional)
        if 'summary' in self.data and self.data['summary']:
            self.section_header(self.labels.get('summary', 'SUMMARY'), self.col2_width, col2_x)
            self.set_font(self.unicode_font, "", 8.5)
            self.set_text_color(*self.text_black)
            self.set_x(col2_x)
            # Changed align='J' to 'L' and reduced height to 3.8
            self.multi_cell(self.col2_width, 3.8, self.clean_text(self.data['summary'], is_block=True), align='L', new_x=XPos.LEFT, new_y=YPos.NEXT)
            self.ln(3) # Was 5
        
        # Education (was Certifications)
        if 'education' in self.data and self.data['education']:
            self.set_x(col2_x)
            self.section_header(self.labels.get('education', 'EDUCATION'), self.col2_width, col2_x)
            for edu in self.data['education']:
                # Degree (Bold)
                self.set_x(col2_x)
                self.set_font(self.unicode_font, "B", 9)
                self.set_text_color(*self.text_black)
                self.multi_cell(self.col2_width, 4.2, self.clean_text(edu['degree']), align='L', new_x=XPos.LEFT, new_y=YPos.NEXT)
                
                # Institution (Blue)
                self.set_x(col2_x)
                self.set_font(self.unicode_font, "B", 8.5)
                self.set_text_color(*self.primary_blue)
                self.multi_cell(self.col2_width, 3.8, self.clean_text(edu['institution']), align='L', new_x=XPos.LEFT, new_y=YPos.NEXT)
                
                # Period (Italic)
                self.set_x(col2_x)
                self.set_font(self.unicode_font, "I", 8)
                self.set_text_color(*self.text_gray)
                self.multi_cell(self.col2_width, 4, self.clean_text(edu['period']), new_x=XPos.LEFT, new_y=YPos.NEXT)
                
                if 'description' in edu:
                    self.set_x(col2_x)
                    self.set_font(self.unicode_font, "", 7.5)
                    self.set_text_color(*self.text_black)
                    self.multi_cell(self.col2_width, 3.2, self.clean_text(edu['description'], is_block=True), align='L', new_x=XPos.LEFT, new_y=YPos.NEXT)
                self.ln(2.5)
            self.ln(1)

        
        # Languages
        if 'languages' in self.data and self.data['languages']:
            self.set_x(col2_x)
            self.section_header(self.labels.get('languages', 'LANGUAGES'), self.col2_width, col2_x)
            for lang in self.data['languages']:
                self.set_x(col2_x)
                self.set_font(self.unicode_font, "B", 9)
                self.cell(self.col2_width, 5, self.clean_text(lang['name']), new_x=XPos.LEFT, new_y=YPos.NEXT)
                self.set_x(col2_x)
                self.set_font(self.unicode_font, "", 8)
                self.cell(self.col2_width, 4, self.clean_text(lang['level']), new_x=XPos.LEFT, new_y=YPos.NEXT)
                
                # Precise Dot Rating (Smaller 2mm dots)
                y_dot = self.get_y() + 0.5
                for i in range(5):
                    self.set_draw_color(*self.primary_blue)
                    self.set_fill_color(*(self.primary_blue if i < lang['rating'] else (255, 255, 255)))
                    self.ellipse(col2_x + self.c_margin + (i*4.5), y_dot, 2.2, 2.2, 'FD')
                self.set_y(y_dot + 5.5) # clearing dots + 3mm gap (Was 7.5)
            self.ln(1)
        
        # Skills
        if 'skills' in self.data and self.data['skills']:
            self.set_x(col2_x)
            self.section_header(self.labels.get('skills', 'SKILLS'), self.col2_width, col2_x)
            
            tag_bg = (242, 242, 242) # Slightly lighter
            tag_border = (210, 210, 210)
            tag_padding = 2.0 # Was 2.5
            tag_height = 5.2 # Was 6
            
            for group in self.data['skills']:
                self.set_x(col2_x)
                self.set_font(self.unicode_font, "B", 8.5) # Was 9
                self.set_text_color(*self.primary_blue)
                self.multi_cell(self.col2_width, 4.5, self.clean_text(group['category']), align='L', new_x=XPos.LEFT, new_y=YPos.NEXT) # Was 5
                
                # Start tag rendering
                self.set_font(self.unicode_font, "", 8)
                self.set_text_color(*self.text_black)
                
                curr_x = col2_x
                curr_y = self.get_y()
                for item in group['items']:
                    text = self.clean_text(item)
                    text_w = self.get_string_width(text)
                    box_w = text_w + tag_padding * 2
                    
                    # Check for wrap-around
                    if curr_x + box_w > col2_x + self.col2_width:
                        curr_y += tag_height + 1.5
                        curr_x = col2_x
                    
                    # Draw Box (Card)
                    self.set_xy(curr_x, curr_y)
                    # Background
                    self.set_fill_color(*tag_bg)
                    self.set_draw_color(*tag_border)
                    self.rect(curr_x, curr_y, box_w, tag_height, 'DF')
                    # Optional: Subtle bottom border for "premium" look (shadow line)
                    self.set_draw_color(180, 180, 180)
                    self.line(curr_x, curr_y + tag_height, curr_x + box_w, curr_y + tag_height)
                    
                    # Text inside box
                    self.set_xy(curr_x, curr_y + 0.5)
                    self.cell(box_w, tag_height - 1, text, align='C')
                    
                    curr_x += box_w + 1.2 # Was 1.5
                
                self.set_y(curr_y + tag_height + 1.5) # Was 2
            self.ln(1.5) # Was 3
        
        # Interests (Optional)
        if 'interests' in self.data and self.data['interests']:
            self.set_x(col2_x)
            self.section_header(self.labels.get('interests', 'INTERESTS'), self.col2_width, col2_x)
            
            # Optimized for narrow column (7pt, tight padding)
            self.set_font(self.unicode_font, "", 7) # Was 7.5
            self.set_text_color(*self.text_black)
            
            curr_x = col2_x
            curr_y = self.get_y()
            
            # Reduce padding/spacing to fit 4 items in 56mm
            int_padding = 1.8
            int_spacing = 1.0
            
            for item in self.data['interests']:
                text = self.clean_text(item)
                text_w = self.get_string_width(text)
                box_w = text_w + int_padding * 2
                
                # Check for wrap-around within col2_width
                if curr_x + box_w > col2_x + self.col2_width:
                    curr_y += tag_height + 1.5
                    curr_x = col2_x
                
                # Draw Box (Card)
                self.set_xy(curr_x, curr_y)
                self.set_fill_color(*tag_bg)
                self.set_draw_color(*tag_border)
                self.rect(curr_x, curr_y, box_w, tag_height, 'DF')
                
                # Subtle shadow line
                self.set_draw_color(180, 180, 180)
                self.line(curr_x, curr_y + tag_height, curr_x + box_w, curr_y + tag_height)
                
                # Text inside box
                self.set_xy(curr_x, curr_y + 0.5)
                self.cell(box_w, tag_height - 1, text, align='C')
                
                curr_x += box_w + int_spacing
            
            self.set_y(curr_y + tag_height + 3) # Was 5

    def output_to_file(self, filename):
        print(f"Generating Template PDF: {filename}...")
        self.output(filename)
        print("Done!")

def generate_pdf(data_file='cv_data.yaml', output_file=None):
    if not os.path.exists(data_file):
        print(f"Error: Data file not found: {data_file}")
        return
        
    with open(data_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Determine output filename if not provided
    if not output_file:
        name_slug = slugify(data.get('name', 'cv'))
        title_slug = slugify(data.get('title', 'output'))
        output_file = f"cv_{name_slug}_{title_slug}.pdf"
    
    cv = CV(data)
    cv.generate(output_file)
    cv.output_to_file(output_file)

if __name__ == "__main__":
    import sys
    
    # If a specific file is provided as an argument, process only that one
    if len(sys.argv) > 1:
        generate_pdf(data_file=sys.argv[1])
    else:
        # Default behavior: Try to generate both if they exist
        target_files = ['cv_data.yaml', 'cv_data_hu.yaml']
        generated_count = 0
        
        for df in target_files:
            if os.path.exists(df):
                print(f"\n--- Processing: {df} ---")
                generate_pdf(data_file=df)
                generated_count += 1
        
        if generated_count == 0:
            print("Error: No default data files found (cv_data.yaml or cv_data_hu.yaml)")
        else:
            print(f"\nFinished! Generated {generated_count} CV versions.")
