#!/usr/bin/env python3
import sass
import os

def compile_scss():
    """Compile SCSS files to CSS"""
    
    # Define paths
    scss_file = 'static/css/dashboard.scss'
    css_file = 'static/css/dashboard.css'
    
    # Check if SCSS file exists
    if not os.path.exists(scss_file):
        print(f"Error: {scss_file} not found!")
        return False
    
    try:
        # Compile SCSS to CSS
        with open(scss_file, 'r') as f:
            scss_content = f.read()
        
        # Compile with libsass
        css_content = sass.compile(string=scss_content, output_style='expanded')
        
        # Write compiled CSS
        with open(css_file, 'w') as f:
            f.write(css_content)
        
        print(f"✅ Successfully compiled {scss_file} to {css_file}")
        print(f"📁 CSS file size: {len(css_content)} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Error compiling SCSS: {e}")
        return False

if __name__ == "__main__":
    compile_scss() 