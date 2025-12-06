#!/usr/bin/env python3
"""
Fix all HTML files in Context Arabic to have consistent navigation and styling
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Module color schemes matching the main index
MODULE_COLORS = {
    'Reading': {'primary': '#64748b', 'accent': '#f97316', 'name_ar': 'القراءة'},
    'Listening': {'primary': '#22c55e', 'accent': '#10b981', 'name_ar': 'الاستماع'},
    'Vocabulary': {'primary': '#a78bfa', 'accent': '#ec4899', 'name_ar': 'المفردات'},
    'Grammar': {'primary': '#0ea5e9', 'accent': '#06b6d4', 'name_ar': 'النحو'},
    'Quizzes': {'primary': '#eab308', 'accent': '#f59e0b', 'name_ar': 'الاختبارات'},
    'Games': {'primary': '#ef4444', 'accent': '#f59e0b', 'name_ar': 'الألعاب'},
    'Culture': {'primary': '#d97706', 'accent': '#fbbf24', 'name_ar': 'الثقافة'},
    'EgyptianArabicModule': {'primary': '#22c55e', 'accent': '#10b981', 'name_ar': 'العامية المصرية'}
}

def get_navigation_html(module_name, colors):
    """Generate consistent navigation HTML"""
    return f'''
    <!-- Context Arabic Navigation -->
    <nav class="sticky top-0 z-50 shadow-lg" style="background: linear-gradient(135deg, {colors['primary']}, {colors['accent']});">
        <div class="container mx-auto px-4 md:px-6 py-3 md:py-4">
            <div class="flex items-center justify-between">
                <a href="../index.html" class="flex items-center gap-2 text-white hover:opacity-80 transition">
                    <i class="fas fa-home text-xl md:text-2xl"></i>
                    <span class="font-semibold text-sm md:text-lg hidden sm:inline">Home</span>
                </a>
                <div class="text-center flex-1 px-4">
                    <span class="text-lg md:text-2xl font-bold text-white">{module_name}</span>
                </div>
                <a href="index.html" class="flex items-center gap-2 text-white hover:opacity-80 transition">
                    <span class="font-semibold text-sm md:text-lg hidden sm:inline">Module</span>
                    <i class="fas fa-arrow-right text-xl md:text-2xl"></i>
                </a>
            </div>
        </div>
    </nav>
'''

def get_footer_html(module_name, colors):
    """Generate consistent footer HTML"""
    return f'''
    <!-- Context Arabic Footer -->
    <footer class="mt-16 py-6 md:py-8 text-white text-center" style="background: linear-gradient(135deg, {colors['primary']}, {colors['accent']});">
        <div class="container mx-auto px-6">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                <a href="../index.html" class="hover:opacity-80 transition">
                    <i class="fas fa-brain text-xl md:text-2xl mr-2"></i>
                    <span class="font-semibold text-sm md:text-base">Context Arabic</span>
                </a>
                <p class="text-xs md:text-sm opacity-90">&copy; 2025 - Learn Arabic in Context</p>
                <a href="index.html" class="hover:opacity-80 transition">
                    <span class="font-semibold text-sm md:text-base">Back to {module_name}</span>
                    <i class="fas fa-arrow-right ml-2"></i>
                </a>
            </div>
        </div>
    </footer>
'''

def ensure_required_imports(soup):
    """Ensure required CSS/JS imports are present"""
    head = soup.find('head')
    if not head:
        return
    
    # Check for Tailwind
    has_tailwind = any('tailwindcss.com' in str(tag) for tag in head.find_all('script'))
    if not has_tailwind:
        script = soup.new_tag('script', src='https://cdn.tailwindcss.com')
        head.append(script)
    
    # Check for Font Awesome
    has_fa = any('font-awesome' in str(tag) for tag in head.find_all('link'))
    if not has_fa:
        link = soup.new_tag('link', rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css')
        head.append(link)
    
    # Check for Google Fonts
    has_fonts = any('Cairo' in str(tag) or 'Lato' in str(tag) for tag in head.find_all('link'))
    if not has_fonts:
        link = soup.new_tag('link', href='https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Lato:wght@400;700&display=swap', rel='stylesheet')
        head.append(link)

def fix_html_file(filepath, module_name):
    """Fix a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get colors for this module
        colors = MODULE_COLORS.get(module_name, MODULE_COLORS['Reading'])
        
        # Ensure required imports
        ensure_required_imports(soup)
        
        # Find body tag
        body = soup.find('body')
        if not body:
            print(f"  ⚠️  No body tag found in {filepath.name}")
            return False
        
        # Check if navigation already exists
        existing_nav = body.find('nav', class_=lambda c: c and 'sticky' in c)
        if existing_nav:
            # Remove old navigation
            existing_nav.decompose()
        
        # Check if footer already exists
        existing_footer = body.find('footer', class_=lambda c: c and 'mt-16' in str(c))
        if existing_footer:
            existing_footer.decompose()
        
        # Add navigation at the start of body
        nav_html = get_navigation_html(module_name, colors)
        nav_soup = BeautifulSoup(nav_html, 'html.parser')
        body.insert(0, nav_soup)
        
        # Add footer at the end of body
        footer_html = get_footer_html(module_name, colors)
        footer_soup = BeautifulSoup(footer_html, 'html.parser')
        body.append(footer_soup)
        
        # Make sure body has flex layout
        if body.get('class'):
            if 'flex' not in ' '.join(body.get('class', [])):
                body['class'].extend(['flex', 'flex-col', 'min-h-screen'])
        else:
            body['class'] = ['flex', 'flex-col', 'min-h-screen']
        
        # Find main content wrapper and add flex-1
        main_containers = body.find_all(['main', 'div'], class_=lambda c: c and ('container' in str(c) or 'max-w' in str(c)), limit=1)
        if main_containers:
            container = main_containers[0]
            if container.name != 'main':
                # Wrap in main tag
                main_tag = soup.new_tag('main', **{'class': 'flex-1'})
                container.wrap(main_tag)
            else:
                # Add flex-1 class
                if container.get('class'):
                    if 'flex-1' not in container.get('class', []):
                        container['class'].append('flex-1')
                else:
                    container['class'] = ['flex-1']
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {filepath.name}: {e}")
        return False

def main():
    """Main function to fix all HTML files"""
    base_dir = Path('/Users/muhammadsabdo/ArabicSimplified')
    
    modules = ['Reading', 'Listening', 'Vocabulary', 'Grammar', 'Quizzes', 'Games', 'Culture', 'EgyptianArabicModule']
    
    total_fixed = 0
    total_files = 0
    
    for module in modules:
        module_dir = base_dir / module
        if not module_dir.exists():
            continue
        
        print(f"\n📁 Processing {module}...")
        
        html_files = list(module_dir.glob('*.html'))
        # Exclude index.html files
        html_files = [f for f in html_files if f.name != 'index.html']
        
        for html_file in html_files:
            total_files += 1
            print(f"  📄 {html_file.name}...", end=' ')
            if fix_html_file(html_file, module):
                print("✅")
                total_fixed += 1
            else:
                print("❌")
    
    print(f"\n{'='*50}")
    print(f"✅ Fixed {total_fixed}/{total_files} files")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
