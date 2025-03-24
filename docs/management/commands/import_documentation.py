import os
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from docs.models import DocumentationCategory, DocumentationArticle

class Command(BaseCommand):
    help = 'Imports documentation from a text file'

    def handle(self, *args, **options):
        file_path = 'Documentation.txt'
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} does not exist!'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Išvalome duomenbazę prieš importą
        DocumentationArticle.objects.all().delete()
        DocumentationCategory.objects.all().delete()

        # Sukuriame visas kategorijas pagal turinį
        contents = re.search(r'## TURINYS\n(.*?)---', content, re.DOTALL)
        categories = []
        
        if contents:
            contents_text = contents.group(1)
            categories_in_toc = re.findall(r'(\d+)\. ([^\n]+)', contents_text)
            
            for order, cat_name in categories_in_toc:
                category, created = DocumentationCategory.objects.get_or_create(
                    slug=slugify(cat_name),
                    defaults={
                        'name': cat_name,
                        'order': int(order)
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category from TOC: {cat_name}'))
                
                categories.append((int(order), cat_name, category))
        
        # Ištraukiame visas sekcijas ir jų turinį
        sections = re.split(r'---\s*\n+', content)
        
        # Apdorojame kiekvieną sekciją
        for section in sections:
            # Praleisti tuščias sekcijas
            if not section.strip():
                continue
                
            # Ieškome sekcijos numerio ir pavadinimo
            section_match = re.search(r'## (\d+)\. ([^\n]+)', section)
            if not section_match:
                continue
                
            section_number = int(section_match.group(1))
            section_title = section_match.group(2).strip()
            
            # Randame atitinkamą kategoriją
            category = None
            for order, name, cat in categories:
                if order == section_number:
                    category = cat
                    break
            
            if not category:
                self.stdout.write(self.style.ERROR(f'Category not found for section {section_number}: {section_title}'))
                continue
            
            # Ištraukiame visas subsekcijas
            subsections = re.split(r'### \d+\.\d+\. ', section)
            
            # Praleisti sekcijos antraštę
            if len(subsections) > 0:
                subsections = subsections[1:]
            
            # Jei nėra subsekcijų, sukuriame vieną straipsnį visai sekcijai
            if len(subsections) == 0:
                cleaned_section = re.sub(r'## \d+\. [^\n]+\n+', '', section)
                article_content = f"<h1>{category.name}</h1>\n\n{self.format_content(cleaned_section)}"
                
                article, created = DocumentationArticle.objects.get_or_create(
                    slug=category.slug,
                    category=category,
                    defaults={
                        'title': category.name,
                        'content': article_content,
                        'order': 1
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created main article: {category.name}'))
                
                continue
            
            # Sukuriame straipsnius subsekcijoms
            for i, subsection in enumerate(subsections):
                # Ištraukiame pavadinimą
                title_match = re.match(r'([^\n]+)', subsection)
                if not title_match:
                    continue
                    
                title = title_match.group(1).strip()
                
                # Pašaliname pavadinimą iš turinio
                content_text = re.sub(r'[^\n]+\n+', '', subsection, 1)
                
                # Formatuojame HTML
                article_content = f"<h1>{title}</h1>\n\n{self.format_content(content_text)}"
                
                # Sukuriame straipsnį
                article_slug = slugify(f"{category.slug}-{title}")
                article, created = DocumentationArticle.objects.get_or_create(
                    slug=article_slug,
                    category=category,
                    defaults={
                        'title': title,
                        'content': article_content,
                        'order': i + 1
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created article: {title}'))
    
    def format_content(self, content):
        """Convert markdown-like content to simple HTML"""
        # Replace numbered lists
        content = re.sub(r'^(\d+)\.\s(.+?)$', r'<li>\2</li>', content, flags=re.MULTILINE)
        
        # Wrap lists in <ol> tags
        content = re.sub(r'(<li>.+?</li>\n)+', r'<ol>\n\g<0></ol>\n', content, flags=re.DOTALL)
        
        # Replace bullet lists
        content = re.sub(r'^-\s(.+?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        
        # Wrap bullet lists in <ul> tags
        content = re.sub(r'(<li>.+?</li>\n)+', r'<ul>\n\g<0></ul>\n', content, flags=re.DOTALL)
        
        # Replace headers
        content = re.sub(r'^####\s(.+?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
        content = re.sub(r'^###\s(.+?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^##\s(.+?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^#\s(.+?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Replace bold text
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        
        # Replace italic text
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        
        # Replace paragraphs
        content = re.sub(r'([^\n]+)\n\n', r'<p>\1</p>\n\n', content)
        
        return content 