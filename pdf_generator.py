import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
# from reportlab.lib import colors  # Not needed, using specific color imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

class ProfessionalResumeTemplate:
    def __init__(self):
        # Professional color scheme
        self.primary_color = HexColor('#2C3E50')      # Dark blue-gray
        self.accent_color = HexColor('#3498DB')       # Professional blue
        self.text_color = HexColor('#2C3E50')         # Dark text
        self.light_gray = HexColor('#ECF0F1')         # Light background
        self.medium_gray = HexColor('#95A5A6')        # Medium gray
        
        # Page margins
        self.margin_left = 0.75 * inch
        self.margin_right = 0.75 * inch
        self.margin_top = 0.75 * inch
        self.margin_bottom = 0.75 * inch
        
        # Create styles
        self.styles = self._create_professional_styles()
    
    def _create_professional_styles(self):
        """Create professional paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Header name style - large and prominent
        styles.add(ParagraphStyle(
            name='ProfHeaderName',
            parent=styles['Normal'],
            fontSize=28,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            alignment=TA_CENTER,
            leading=32
        ))
        
        # Contact info style
        styles.add(ParagraphStyle(
            name='ProfContactInfo',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            fontName='Helvetica',
            spaceAfter=12,
            alignment=TA_CENTER,
            leading=14
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='ProfSectionHeader',
            parent=styles['Normal'],
            fontSize=14,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=16,
            alignment=TA_LEFT,
            leading=16
        ))
        
        # Job title style
        styles.add(ParagraphStyle(
            name='ProfJobTitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=4,
            spaceBefore=8,
            alignment=TA_LEFT,
            leading=14
        ))
        
        # Company and date style
        styles.add(ParagraphStyle(
            name='ProfCompanyDate',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.accent_color,
            fontName='Helvetica-Oblique',
            spaceAfter=6,
            alignment=TA_LEFT,
            leading=13
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='ProfBodyText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            fontName='Helvetica',
            spaceAfter=4,
            alignment=TA_JUSTIFY,
            leading=12
        ))
        
        # Bullet point style
        styles.add(ParagraphStyle(
            name='ProfBulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            fontName='Helvetica',
            spaceAfter=3,
            leftIndent=12,
            bulletIndent=6,
            alignment=TA_LEFT,
            leading=12
        ))
        
        # Skills item style - for horizontal tags
        styles.add(ParagraphStyle(
            name='ProfSkillItem',
            parent=styles['Normal'],
            fontSize=9,
            textColor=white,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            leading=11
        ))
        
        # Skills category style - enhanced with underline effect
        styles.add(ParagraphStyle(
            name='ProfSkillCategory',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=10,
            alignment=TA_LEFT,
            leading=14,
            borderWidth=0,
            borderColor=self.accent_color
        ))
        
        # Skills tag style - for individual skill badges
        styles.add(ParagraphStyle(
            name='ProfSkillTag',
            parent=styles['Normal'],
            fontSize=9,
            textColor=white,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            leading=11
        ))
        
        return styles

class ProfessionalResumePDFGenerator:
    def __init__(self):
        self.template = ProfessionalResumeTemplate()
    
    def clean_text(self, text):
        """Clean text by removing markdown formatting and extra characters"""
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Remove *italic*
        text = re.sub(r'^\*+\s*', '', text)             # Remove leading asterisks
        text = re.sub(r'\s*\*+$', '', text)             # Remove trailing asterisks
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def parse_resume_content(self, resume_text):
        """Parse comprehensive resume content into structured sections"""
        sections = {
            'name': '',
            'contact': {
                'phone': '',
                'email': '',
                'address': ''
            },
            'profile': '',
            'experience': [],
            'education': [],
            'skills': {},
            'certifications': [],
            'additional_skills': []
        }
        
        lines = [line.strip() for line in resume_text.strip().split('\n') if line.strip()]
        current_section = None
        current_experience = {}
        
        # Extract name - look for the first bold line or standalone name
        for i, line in enumerate(lines[:10]):
            clean_line = self.clean_text(line)
            if (clean_line and 
                not clean_line.lower().startswith('here is') and
                not any(keyword in clean_line.lower() for keyword in ['mobile:', 'email:', '@', 'phone:', 'summary', 'professional']) and
                len(clean_line.split()) >= 2 and
                not clean_line.startswith('-') and
                not clean_line.startswith('*')):
                sections['name'] = clean_line.upper()
                break
        
        # Parse content line by line
        i = 0
        while i < len(lines):
            line = lines[i]
            clean_line = self.clean_text(line)
            if not clean_line:
                i += 1
                continue
            
            line_lower = clean_line.lower()
            
            # Skip separator lines
            if clean_line.startswith('---') or clean_line.startswith('==='):
                i += 1
                continue
            
            # Extract contact information
            if 'mobile:' in line_lower or 'phone:' in line_lower:
                phone_match = re.search(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', clean_line)
                if phone_match:
                    sections['contact']['phone'] = phone_match.group(1)
                i += 1
                continue
            
            if 'email:' in line_lower or '@' in clean_line:
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', clean_line)
                if email_match:
                    sections['contact']['email'] = email_match.group()
                i += 1
                continue
            
            # Detect major sections
            if any(keyword in line_lower for keyword in ['professional summary', 'summary', 'profile', 'objective']):
                current_section = 'profile'
                # Collect profile content until next section
                i += 1
                profile_lines = []
                while i < len(lines):
                    next_line = self.clean_text(lines[i])
                    if not next_line:
                        i += 1
                        continue
                    if next_line.startswith('---'):
                        i += 1
                        break
                    if any(section_keyword in next_line.lower() for section_keyword in 
                           ['technical skills', 'professional experience', 'experience', 'education', 'certifications']):
                        break
                    profile_lines.append(next_line)
                    i += 1
                sections['profile'] = ' '.join(profile_lines)
                continue
            
            elif any(keyword in line_lower for keyword in ['technical skills', 'skills']):
                current_section = 'skills'
                i += 1
                # Parse skills section
                while i < len(lines):
                    skill_line = self.clean_text(lines[i])
                    if not skill_line or skill_line.startswith('---'):
                        i += 1
                        continue
                    if any(section_keyword in skill_line.lower() for section_keyword in 
                           ['professional experience', 'experience', 'education', 'certifications']):
                        break
                    
                    # Parse skill categories
                    if skill_line.startswith('-') and ':' in skill_line:
                        # Format: - **Category:** skill1, skill2, skill3
                        category_match = re.search(r'-\s*\*?\*?([^:*]+)\*?\*?:\s*(.+)', skill_line)
                        if category_match:
                            category = category_match.group(1).strip()
                            skills_text = category_match.group(2).strip()
                            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                            sections['skills'][category] = skills_list
                    i += 1
                continue
            
            elif any(keyword in line_lower for keyword in ['professional experience', 'work experience', 'experience']):
                current_section = 'experience'
                i += 1
                # Parse experience section
                while i < len(lines):
                    exp_line = self.clean_text(lines[i])
                    if not exp_line or exp_line.startswith('---'):
                        i += 1
                        continue
                    if any(section_keyword in exp_line.lower() for section_keyword in 
                           ['education', 'certifications', 'additional skills']):
                        break
                    
                    # Check if this is a company/location line
                    if (not exp_line.startswith('-') and not exp_line.startswith('•') and 
                        (',' in exp_line or any(keyword in exp_line.lower() for keyword in ['inc', 'corp', 'llc', 'ltd', 'company']))):
                        
                        # Save previous experience if exists
                        if current_experience:
                            sections['experience'].append(current_experience)
                        
                        # Start new experience entry
                        current_experience = {
                            'company': exp_line,
                            'title': '',
                            'dates': '',
                            'responsibilities': []
                        }
                        
                        # Look for job title and dates in next lines
                        i += 1
                        if i < len(lines):
                            title_line = self.clean_text(lines[i])
                            if title_line.startswith('*') or 'developer' in title_line.lower() or 'engineer' in title_line.lower():
                                current_experience['title'] = title_line.strip('*').strip()
                                i += 1
                                if i < len(lines):
                                    date_line = self.clean_text(lines[i])
                                    if re.search(r'\d{4}', date_line):
                                        current_experience['dates'] = date_line.strip('*').strip()
                                        i += 1
                        continue
                    
                    # Check for responsibilities
                    elif exp_line.startswith('-') or exp_line.startswith('•'):
                        if current_experience:
                            responsibility = exp_line.lstrip('-• ').strip()
                            current_experience['responsibilities'].append(responsibility)
                    
                    i += 1
                
                # Add last experience
                if current_experience:
                    sections['experience'].append(current_experience)
                    current_experience = {}
                continue
            
            elif any(keyword in line_lower for keyword in ['education']):
                current_section = 'education'
                i += 1
                while i < len(lines):
                    edu_line = self.clean_text(lines[i])
                    if not edu_line or edu_line.startswith('---'):
                        i += 1
                        continue
                    if any(section_keyword in edu_line.lower() for section_keyword in 
                           ['certifications', 'additional skills', 'notes']):
                        break
                    sections['education'].append(edu_line)
                    i += 1
                continue
            
            elif any(keyword in line_lower for keyword in ['certifications', 'training']):
                current_section = 'certifications'
                i += 1
                while i < len(lines):
                    cert_line = self.clean_text(lines[i])
                    if not cert_line or cert_line.startswith('---'):
                        i += 1
                        continue
                    if any(section_keyword in cert_line.lower() for section_keyword in 
                           ['additional skills', 'notes']):
                        break
                    if cert_line.startswith('-') or cert_line.startswith('•'):
                        cert_line = cert_line.lstrip('-• ').strip()
                    sections['certifications'].append(cert_line)
                    i += 1
                continue
            
            elif any(keyword in line_lower for keyword in ['additional skills', 'attributes']):
                current_section = 'additional_skills'
                i += 1
                while i < len(lines):
                    skill_line = self.clean_text(lines[i])
                    if not skill_line or skill_line.startswith('---'):
                        i += 1
                        continue
                    if 'notes' in skill_line.lower():
                        break
                    if skill_line.startswith('-') or skill_line.startswith('•'):
                        skill_line = skill_line.lstrip('-• ').strip()
                    sections['additional_skills'].append(skill_line)
                    i += 1
                continue
            
            i += 1
        
        return sections
    
    def create_header(self, story, sections):
        """Create professional header with name and contact info"""
        if sections['name']:
            # Name
            name_para = Paragraph(sections['name'], self.template.styles['ProfHeaderName'])
            story.append(name_para)
        
        # Contact information
        contact_parts = []
        if sections['contact']['phone']:
            contact_parts.append(f"Phone: {sections['contact']['phone']}")
        if sections['contact']['email']:
            contact_parts.append(f"Email: {sections['contact']['email']}")
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            contact_para = Paragraph(contact_text, self.template.styles['ProfContactInfo'])
            story.append(contact_para)
        
        # Add separator line
        story.append(Spacer(1, 12))
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 2, self.template.accent_color),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
        ]))
        story.append(line_table)
    
    def create_section(self, story, title, content_func, *args):
        """Create a section with title and content"""
        if args and any(args):  # Only create section if there's content
            # Section header
            header_para = Paragraph(title.upper(), self.template.styles['ProfSectionHeader'])
            story.append(header_para)
            
            # Section content
            content_func(story, *args)
            
            # Add spacing after section
            story.append(Spacer(1, 12))
    
    def add_profile_content(self, story, profile):
        """Add profile/summary content"""
        if profile:
            profile_para = Paragraph(profile, self.template.styles['ProfBodyText'])
            story.append(profile_para)
    
    def add_experience_content(self, story, experiences):
        """Add work experience content"""
        for exp in experiences:
            if exp.get('title'):
                # Job title
                title_para = Paragraph(exp['title'], self.template.styles['ProfJobTitle'])
                story.append(title_para)
            
            # Company and dates
            company_date_parts = []
            if exp.get('company'):
                company_date_parts.append(exp['company'])
            if exp.get('dates'):
                company_date_parts.append(exp['dates'])
            
            if company_date_parts:
                company_date_text = " | ".join(company_date_parts)
                company_para = Paragraph(company_date_text, self.template.styles['ProfCompanyDate'])
                story.append(company_para)
            
            # Responsibilities
            if exp.get('responsibilities'):
                for resp in exp['responsibilities']:
                    if resp.strip():
                        bullet_para = Paragraph(f"• {resp}", self.template.styles['ProfBulletPoint'])
                        story.append(bullet_para)
            
            story.append(Spacer(1, 8))
    
    def add_skills_content(self, story, skills):
        """Add skills content with modern horizontal tag layout"""
        for category, skill_list in skills.items():
            if skill_list:
                # Category header with enhanced styling and underline
                cat_para = Paragraph(f"<b>{category}</b>", self.template.styles['ProfSkillCategory'])
                story.append(cat_para)
                
                # Add subtle underline for category
                underline_table = Table([['']], colWidths=[6.5*inch])
                underline_table.setStyle(TableStyle([
                    ('LINEBELOW', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(underline_table)
                
                # Create horizontal skill tags using table
                skills_to_show = skill_list[:12]  # Limit to 12 skills per category
                
                # Create skill tags in rows of 3-4 skills each for better spacing
                rows = []
                current_row = []
                skills_per_row = 3  # Reduced for better spacing
                
                for i, skill in enumerate(skills_to_show):
                    # Create skill tag with enhanced styling
                    skill_text = f"<b>{skill}</b>"
                    skill_cell = Paragraph(skill_text, self.template.styles['ProfSkillTag'])
                    current_row.append(skill_cell)
                    
                    # Start new row after specified number of skills or if it's the last skill
                    if len(current_row) == skills_per_row or i == len(skills_to_show) - 1:
                        # Fill remaining cells in row if needed
                        while len(current_row) < skills_per_row:
                            current_row.append('')
                        rows.append(current_row)
                        current_row = []
                
                if rows:
                    # Calculate column widths for better distribution
                    col_width = 2.2 * inch  # Wider columns for better readability
                    table = Table(rows, colWidths=[col_width] * skills_per_row, rowHeights=24)
                    
                    # Enhanced styling with gradient-like effect
                    table_style = [
                        # Default background for all cells
                                        ('BACKGROUND', (0, 0), (-1, -1), white),
                ('TEXTCOLOR', (0, 0), (-1, -1), white),
                        
                        # Padding and alignment
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        
                        # Subtle borders for definition
                        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                        ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ]
                    
                    # Create attractive color scheme for skill tags
                    skill_colors = [
                        colors.Color(0.2, 0.5, 0.8),   # Professional blue
                        colors.Color(0.15, 0.4, 0.65), # Darker blue
                        colors.Color(0.25, 0.55, 0.75), # Medium blue
                        colors.Color(0.1, 0.35, 0.6),  # Deep blue
                        colors.Color(0.3, 0.6, 0.8),   # Light blue
                        colors.Color(0.18, 0.45, 0.7), # Balanced blue
                    ]
                    
                    # Apply colors to non-empty cells
                    color_index = 0
                    for row_idx in range(len(rows)):
                        for col_idx in range(skills_per_row):
                            if rows[row_idx][col_idx] != '':  # Only style non-empty cells
                                bg_color = skill_colors[color_index % len(skill_colors)]
                                table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color))
                                color_index += 1
                    
                    table.setStyle(TableStyle(table_style))
                    story.append(table)
                
                story.append(Spacer(1, 12))
    
    def add_education_content(self, story, education):
        """Add education content"""
        for edu in education:
            edu_para = Paragraph(f"• {edu}", self.template.styles['ProfBodyText'])
            story.append(edu_para)
    
    def add_certifications_content(self, story, certifications):
        """Add certifications content"""
        for cert in certifications:
            cert_para = Paragraph(f"• {cert}", self.template.styles['ProfBodyText'])
            story.append(cert_para)
    
    def add_additional_skills_content(self, story, additional_skills):
        """Add additional skills and attributes content"""
        for skill in additional_skills:
            skill_para = Paragraph(f"• {skill}", self.template.styles['ProfBodyText'])
            story.append(skill_para)
    
    def generate_pdf(self, resume_text, filename=None):
        """Generate professional PDF resume"""
        # Parse content
        sections = self.parse_resume_content(resume_text)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=self.template.margin_left,
            rightMargin=self.template.margin_right,
            topMargin=self.template.margin_top,
            bottomMargin=self.template.margin_bottom
        )
        
        story = []
        
        # Header
        self.create_header(story, sections)
        
        # Profile section
        self.create_section(story, "Professional Summary", self.add_profile_content, sections['profile'])
        
        # Experience section
        self.create_section(story, "Work Experience", self.add_experience_content, sections['experience'])
        
        # Skills section
        self.create_section(story, "Technical Skills", self.add_skills_content, sections['skills'])
        
        # Education section
        self.create_section(story, "Education", self.add_education_content, sections['education'])
        
        # Certifications section
        self.create_section(story, "Certifications & Training", self.add_certifications_content, sections['certifications'])
        
        # Additional Skills section
        self.create_section(story, "Additional Skills & Attributes", self.add_additional_skills_content, sections['additional_skills'])
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data

class ModernCoverLetterTemplate:
    """Modern professional cover letter template with enhanced styling"""
    
    def __init__(self):
        # Modern color palette
        self.primary_color = HexColor('#2C3E50')      # Dark blue-gray
        self.accent_color = HexColor('#3498DB')       # Modern blue
        self.secondary_color = HexColor('#34495E')    # Darker gray
        self.text_color = HexColor('#2C3E50')         # Dark text
        self.light_gray = HexColor('#ECF0F1')         # Light background
        self.border_color = HexColor('#BDC3C7')       # Light border
        
        # Modern typography
        self.header_font = 'Helvetica-Bold'
        self.body_font = 'Helvetica'
        self.accent_font = 'Helvetica-Oblique'
        
        # Layout settings
        self.margin_left = 0.75 * inch
        self.margin_right = 0.75 * inch
        self.margin_top = 0.75 * inch
        self.margin_bottom = 0.75 * inch
        
        # Create styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create modern custom paragraph styles"""
        
        # Modern header style
        self.styles.add(ParagraphStyle(
            name='ModernHeader',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=self.primary_color,
            fontName=self.header_font,
            alignment=TA_LEFT,
            spaceAfter=8,
            leftIndent=0,
            letterSpacing=1
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.accent_color,
            fontName=self.body_font,
            alignment=TA_LEFT,
            spaceAfter=20,
            leftIndent=0
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ModernContact',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.secondary_color,
            fontName=self.body_font,
            alignment=TA_LEFT,
            spaceAfter=0,
            leftIndent=0,
            leading=12
        ))
        
        # Date style
        self.styles.add(ParagraphStyle(
            name='ModernDate',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            fontName=self.body_font,
            alignment=TA_RIGHT,
            spaceAfter=16,
            rightIndent=0
        ))
        
        # Recipient style
        self.styles.add(ParagraphStyle(
            name='ModernRecipient',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            fontName=self.body_font,
            alignment=TA_LEFT,
            spaceAfter=6,
            leftIndent=0,
            leading=14
        ))
        
        # Salutation style
        self.styles.add(ParagraphStyle(
            name='ModernSalutation',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.primary_color,
            fontName=self.header_font,
            alignment=TA_LEFT,
            spaceAfter=18,
            leftIndent=0
        ))
        
        # Body paragraph style
        self.styles.add(ParagraphStyle(
            name='ModernBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            fontName=self.body_font,
            alignment=TA_JUSTIFY,
            spaceAfter=16,
            leading=16,
            leftIndent=0,
            rightIndent=0
        ))
        
        # Closing style
        self.styles.add(ParagraphStyle(
            name='ModernClosing',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            fontName=self.body_font,
            alignment=TA_LEFT,
            spaceAfter=36,
            leftIndent=0
        ))
        
        # Signature style
        self.styles.add(ParagraphStyle(
            name='ModernSignature',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.primary_color,
            fontName=self.header_font,
            alignment=TA_LEFT,
            spaceAfter=0,
            leftIndent=0
        ))

class ProfessionalCoverLetterPDFGenerator:
    """Professional cover letter PDF generator with modern business letter formatting"""
    
    def __init__(self):
        self.template = ModernCoverLetterTemplate()
        
    def parse_cover_letter_content(self, cover_letter_text):
        """Parse cover letter content into structured sections"""
        lines = [line.strip() for line in cover_letter_text.split('\n') if line.strip()]
        
        # Initialize sections
        sections = {
            'date': '',
            'recipient_info': [],
            'salutation': '',
            'body_paragraphs': [],
            'closing': '',
            'signature': ''
        }
        
        current_section = 'body_paragraphs'
        
        for i, line in enumerate(lines):
            # Check for date (usually at the beginning)
            if i == 0 and (any(month in line.lower() for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']) or 
                          re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', line) or
                          re.match(r'\w+\s+\d{1,2},?\s+\d{4}', line)):
                sections['date'] = line
                continue
                
            # Check for salutation
            if line.lower().startswith(('dear ', 'hello ', 'hi ', 'to whom it may concern')):
                sections['salutation'] = line
                current_section = 'body_paragraphs'
                continue
                
            # Check for closing
            if line.lower().startswith(('sincerely', 'best regards', 'yours truly', 'respectfully', 'thank you', 'kind regards', 'warm regards')):
                sections['closing'] = line
                current_section = 'signature'
                continue
                
            # Check for recipient info (company name, address, etc.)
            if i < 5 and not sections['salutation'] and not sections['date']:
                # Likely recipient information
                if any(keyword in line.lower() for keyword in ['company', 'corporation', 'inc', 'ltd', 'manager', 'director', 'hr', 'human resources', 'hiring']):
                    sections['recipient_info'].append(line)
                    continue
                elif re.match(r'\d+.*[A-Za-z].*\d{5}', line):  # Address pattern
                    sections['recipient_info'].append(line)
                    continue
                    
            # Add to current section
            if current_section == 'body_paragraphs':
                sections['body_paragraphs'].append(line)
            elif current_section == 'signature':
                sections['signature'] = line
                break
                
        return sections
    
    def create_modern_header(self, story, applicant_name="", contact_info=""):
        """Create modern professional header with enhanced styling and proper spacing"""
        
        # Extract name from contact info if not provided
        if not applicant_name and contact_info:
            lines = contact_info.split('\n')
            for line in lines:
                if line.strip() and not '@' in line and not any(char.isdigit() for char in line[:5]):
                    applicant_name = line.strip()
                    break
        
        if not applicant_name:
            applicant_name = "Your Name"
        
        # Create name paragraph with proper spacing
        name_paragraph = Paragraph(applicant_name, self.template.styles['ModernHeader'])
        story.append(name_paragraph)
        story.append(Spacer(1, 6))  # Small space after name
        
        # Process contact info with better formatting
        if contact_info:
            contact_lines = []
            lines = [line.strip() for line in contact_info.split('\n') if line.strip()]
            
            for line in lines:
                if line != applicant_name:  # Don't repeat the name
                    contact_lines.append(line)
            
            # Create contact info with proper spacing
            if contact_lines:
                # Join with bullet separators and proper spacing
                contact_text = ' • '.join(contact_lines[:4])  # Allow up to 4 contact items
                contact_paragraph = Paragraph(contact_text, self.template.styles['ModernContact'])
                story.append(contact_paragraph)
        
        story.append(Spacer(1, 8))  # Space before decorative line
        
        # Add decorative line with proper width
        line_table = Table([['']], colWidths=[7*inch], rowHeights=[2])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.template.accent_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(line_table)
        story.append(Spacer(1, 24))  # Proper space after header section
    
    def create_date_section(self, story, date_text):
        """Create modern date section"""
        if date_text:
            story.append(Paragraph(date_text, self.template.styles['ModernDate']))
        else:
            # Add current date if none provided
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(current_date, self.template.styles['ModernDate']))
    
    def create_recipient_section(self, story, recipient_info):
        """Create modern recipient information section"""
        if recipient_info:
            for line in recipient_info:
                story.append(Paragraph(line, self.template.styles['ModernRecipient']))
        
        story.append(Spacer(1, 20))  # Increased space after recipient info
    
    def create_salutation_section(self, story, salutation):
        """Create modern salutation section"""
        if not salutation:
            salutation = "Dear Hiring Manager,"
            
        story.append(Paragraph(salutation, self.template.styles['ModernSalutation']))
    
    def create_body_section(self, story, body_paragraphs):
        """Create modern body paragraphs section"""
        for paragraph in body_paragraphs:
            if paragraph.strip():
                story.append(Paragraph(paragraph, self.template.styles['ModernBody']))
    
    def create_closing_section(self, story, closing, signature):
        """Create modern closing and signature section"""
        if not closing:
            closing = "Sincerely,"
            
        story.append(Paragraph(closing, self.template.styles['ModernClosing']))
        
        # Signature
        if signature:
            story.append(Paragraph(signature, self.template.styles['ModernSignature']))
        
        # Add some space at the bottom
        story.append(Spacer(1, 20))
    
    def generate_pdf(self, cover_letter_text, applicant_name="", contact_info="", filename=None):
        """Generate modern professional PDF cover letter"""
        # Parse content
        sections = self.parse_cover_letter_content(cover_letter_text)
        
        # Create PDF with modern styling
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=self.template.margin_left,
            rightMargin=self.template.margin_right,
            topMargin=self.template.margin_top,
            bottomMargin=self.template.margin_bottom,
            title="Professional Cover Letter"
        )
        
        story = []
        
        # Modern header with enhanced styling
        self.create_modern_header(story, applicant_name, contact_info)
        
        # Date
        self.create_date_section(story, sections['date'])
        
        # Recipient information
        self.create_recipient_section(story, sections['recipient_info'])
        
        # Salutation
        self.create_salutation_section(story, sections['salutation'])
        
        # Body paragraphs
        self.create_body_section(story, sections['body_paragraphs'])
        
        # Closing and signature
        self.create_closing_section(story, sections['closing'], sections['signature'])
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data

# Compatibility functions
def generate_resume_pdf(resume_text, filename=None):
    """Generate professional resume PDF"""
    generator = ProfessionalResumePDFGenerator()
    return generator.generate_pdf(resume_text, filename)

def generate_cover_letter_pdf(cover_letter_text, applicant_name="", contact_info="", filename=None):
    """Generate professional cover letter PDF"""
    generator = ProfessionalCoverLetterPDFGenerator()
    return generator.generate_pdf(cover_letter_text, applicant_name, contact_info, filename)

# Legacy function for backward compatibility
def convert_text_to_pdf(text):
    """Convert text to PDF (legacy function)"""
    return generate_resume_pdf(text)
