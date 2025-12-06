#!/usr/bin/env python3
"""
Generate interactive listening lesson pages from DOCX files
"""
import zipfile
import xml.etree.ElementTree as ET
import re
import os
from pathlib import Path

# Lesson mapping (original DOCX name -> clean filename)
LESSONS = {
    'حجز غرفة -  مريم.docx': {
        'filename': 'hotel_reservation_mariam',
        'title_ar': 'حجز غرفة في فندق - مريم',
        'title_en': 'Hotel Reservation - Mariam',
        'audio': 'حجز غرفة -  مريم.mp3',
        'level': 'Intermediate'
    },
    'حجز فندق.docx': {
        'filename': 'hotel_booking',
        'title_ar': 'حجز فندق',
        'title_en': 'Hotel Booking',
        'audio': 'حجز فندق.mp3',
        'level': 'Intermediate'
    },
    'سارة.docx': {
        'filename': 'sara_story',
        'title_ar': 'قصة سارة',
        'title_en': 'Sara\'s Story',
        'audio': 'سارة.mp3',
        'level': 'Advanced'
    },
    'عربية جديدة.docx': {
        'filename': 'new_car',
        'title_ar': 'عربية جديدة',
        'title_en': 'New Car',
        'audio': 'عربية جديدة.mp3',
        'level': 'Intermediate'
    },
    'كل يوم في مشكلة.docx': {
        'filename': 'daily_problems',
        'title_ar': 'كل يوم في مشكلة',
        'title_en': 'Daily Problems',
        'audio': 'كل يوم في مشكلة.mp3',
        'level': 'Advanced'
    },
    'ماذا ستفعل لو كنتَ مكاني.docx': {
        'filename': 'if_you_were_me',
        'title_ar': 'ماذا ستفعل لو كنت مكاني',
        'title_en': 'What Would You Do If You Were Me',
        'audio': 'ماذا ستفعل لو كنت مكاني.mp3',
        'level': 'Advanced'
    },
    'محمود وخالد في السينما.docx': {
        'filename': 'cinema_friends',
        'title_ar': 'محمود وخالد في السينما',
        'title_en': 'Mahmoud and Khaled at the Cinema',
        'audio': 'محمود وخالد في السينما.mp3',
        'level': 'Beginner'
    },
    'يوم الأربع.docx': {
        'filename': 'wednesday',
        'title_ar': 'يوم الأربعاء',
        'title_en': 'Wednesday',
        'audio': 'يوم الأربع.mp3',
        'level': 'Beginner'
    }
}

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        xml_content = zip_ref.read('word/document.xml')
    root = ET.fromstring(xml_content)
    
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    
    for para in root.findall('.//w:p', namespace):
        texts = []
        for text in para.findall('.//w:t', namespace):
            if text.text:
                texts.append(text.text)
        if texts:
            paragraphs.append(''.join(texts))
    
    return paragraphs

def parse_questions(paragraphs):
    """Parse questions from document paragraphs"""
    tf_questions = []
    mcq_questions = []
    matching_questions = []
    
    current_section = None
    current_question = None
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Detect sections
        if 'صح أو خطأ' in para or 'True / False' in para:
            current_section = 'tf'
            continue
        elif 'اختيار من متعدد' in para or 'Multiple-Choice' in para:
            current_section = 'mcq'
            continue
        elif 'توصيل' in para or 'Matching' in para:
            current_section = 'matching'
            continue
            
        # Parse True/False
        if current_section == 'tf':
            if re.match(r'^\d+[\.)]\s', para) or ('صح' in para or 'خطأ' in para or '✔️' in para or '❌' in para):
                # Check if it's a T/F statement
                is_correct = 'صح' in para or '✔️' in para
                # Remove answer indicators
                statement = re.sub(r'(صح|خطأ|✔️|❌|خطأ —.*$)', '', para).strip()
                statement = re.sub(r'^\d+[\.)]\s*', '', statement).strip()
                if len(statement) > 10:
                    tf_questions.append({
                        'statement': statement,
                        'correct': is_correct
                    })
        
        # Parse MCQ
        elif current_section == 'mcq':
            # Check if it's a question (starts with number or ends with ?)
            if re.match(r'^\d+[\.)]', para) or para.endswith('؟'):
                if current_question:
                    mcq_questions.append(current_question)
                current_question = {
                    'question': re.sub(r'^\d+[\.)\s]*', '', para).strip(),
                    'options': []
                }
            # Check if it's an option
            elif re.match(r'^[أ-د][\.)]', para) or re.match(r'^[ابجد]\.', para):
                if current_question:
                    option_text = re.sub(r'^[أ-د][\.)\s]*', '', para).strip()
                    is_correct = '✔️' in para or '✓' in para
                    option_text = option_text.replace('✔️', '').replace('✓', '').strip()
                    current_question['options'].append({
                        'text': option_text,
                        'correct': is_correct
                    })
    
    # Add last MCQ if exists
    if current_question and current_section == 'mcq':
        mcq_questions.append(current_question)
    
    return {
        'tf': tf_questions[:10],  # Limit to 10
        'mcq': mcq_questions[:10]  # Limit to 10
    }

def generate_html(lesson_info, questions, output_dir):
    """Generate HTML page for a lesson"""
    html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lesson_info['title_ar']} - Context Arabic</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Cairo', sans-serif; }}
        .font-english {{ font-family: 'Lato', sans-serif; }}
        .audio-player {{
            background: linear-gradient(135deg, #22c55e, #10b981);
            border-radius: 1rem;
            padding: 2rem;
            color: white;
        }}
        .question-card {{
            background: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        .question-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .option-btn {{
            background: #f3f4f6;
            border: 2px solid #e5e7eb;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
            text-align: right;
            width: 100%;
            margin: 0.25rem 0;
        }}
        .option-btn:hover {{
            background: #e5e7eb;
            border-color: #22c55e;
        }}
        .option-btn.selected {{
            background: #dbeafe;
            border-color: #3b82f6;
        }}
        .option-btn.correct {{
            background: #d1fae5;
            border-color: #10b981;
        }}
        .option-btn.incorrect {{
            background: #fee2e2;
            border-color: #ef4444;
        }}
        .score-display {{
            background: linear-gradient(135deg, #22c55e, #10b981);
            color: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            margin-top: 2rem;
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-gray-50 to-green-50">

    <!-- Navigation -->
    <nav class="sticky top-0 z-50 shadow-lg" style="background: linear-gradient(135deg, #22c55e, #10b981);">
        <div class="container mx-auto px-4 md:px-6 py-3 md:py-4">
            <div class="flex items-center justify-between">
                <a href="../index.html" class="flex items-center gap-2 text-white hover:opacity-80 transition">
                    <i class="fas fa-home text-xl md:text-2xl"></i>
                    <span class="font-semibold text-sm md:text-lg hidden sm:inline">Home</span>
                </a>
                <div class="text-center flex-1 px-4">
                    <span class="text-lg md:text-2xl font-bold text-white">{lesson_info['title_ar']}</span>
                </div>
                <a href="index.html" class="flex items-center gap-2 text-white hover:opacity-80 transition">
                    <span class="font-semibold text-sm md:text-lg hidden sm:inline">Listening Module</span>
                    <i class="fas fa-arrow-right text-xl md:text-2xl"></i>
                </a>
            </div>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8 max-w-4xl">
        
        <!-- Header -->
        <div class="text-center mb-8">
            <div class="inline-block px-4 py-2 bg-green-100 text-green-800 rounded-full mb-4">
                <i class="fas fa-signal mr-2"></i>{lesson_info['level']}
            </div>
            <h1 class="text-4xl font-bold text-gray-900 mb-2">{lesson_info['title_ar']}</h1>
            <p class="text-xl text-gray-600 font-english">{lesson_info['title_en']}</p>
        </div>

        <!-- Audio Player -->
        <div class="audio-player mb-8">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <i class="fas fa-headphones text-3xl mb-2"></i>
                    <p class="text-lg">استمع إلى التسجيل الصوتي</p>
                    <p class="text-sm opacity-90 font-english">Listen to the audio recording</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold" id="playCount">0</div>
                    <div class="text-sm opacity-90">مرات الاستماع</div>
                </div>
            </div>
            <audio id="audioPlayer" controls class="w-full">
                <source src="{lesson_info['audio']}" type="audio/mpeg">
                متصفحك لا يدعم تشغيل الملفات الصوتية
            </audio>
        </div>

        <!-- Instructions -->
        <div class="bg-blue-50 border-r-4 border-blue-500 p-4 rounded-lg mb-8">
            <h2 class="text-xl font-bold text-blue-900 mb-2">
                <i class="fas fa-info-circle ml-2"></i>تعليمات
            </h2>
            <ul class="list-disc list-inside text-blue-800 space-y-1">
                <li>استمع إلى التسجيل الصوتي بتركيز</li>
                <li>يمكنك إعادة الاستماع أكثر من مرة</li>
                <li>أجب على الأسئلة بعد الاستماع</li>
                <li>اضغط على "تحقق من الإجابات" لمعرفة نتيجتك</li>
            </ul>
        </div>

        <!-- True/False Section -->
        <div id="tf-section" class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">
                <i class="fas fa-check-circle text-green-600 ml-2"></i>
                أسئلة صح أو خطأ
            </h2>
'''
    
    # Add T/F questions
    for i, q in enumerate(questions['tf'], 1):
        html += f'''
            <div class="question-card">
                <p class="text-lg mb-3"><span class="font-bold text-green-600">{i}.</span> {q['statement']}</p>
                <div class="flex gap-4">
                    <button class="option-btn tf-option" data-question="{i}" data-answer="true" onclick="selectTF(this, {i}, 'true')">
                        <i class="fas fa-check ml-2 text-green-600"></i>صح
                    </button>
                    <button class="option-btn tf-option" data-question="{i}" data-answer="false" onclick="selectTF(this, {i}, 'false')">
                        <i class="fas fa-times ml-2 text-red-600"></i>خطأ
                    </button>
                </div>
            </div>
'''
    
    html += '''
        </div>

        <!-- MCQ Section -->
        <div id="mcq-section" class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">
                <i class="fas fa-list-ul text-blue-600 ml-2"></i>
                أسئلة اختيار من متعدد
            </h2>
'''
    
    # Add MCQ questions
    for i, q in enumerate(questions['mcq'], 1):
        qnum = i + len(questions['tf'])
        html += f'''
            <div class="question-card">
                <p class="text-lg font-bold mb-3 text-gray-900">{qnum}. {q['question']}</p>
                <div class="space-y-2">
'''
        for j, opt in enumerate(q['options']):
            opt_letter = ['أ', 'ب', 'ج', 'د'][j] if j < 4 else str(j+1)
            html += f'''
                    <button class="option-btn mcq-option" data-question="{qnum}" data-correct="{str(opt['correct']).lower()}" onclick="selectMCQ(this, {qnum})">
                        <span class="font-bold text-blue-600 ml-2">{opt_letter}.</span> {opt['text']}
                    </button>
'''
        html += '''
                </div>
            </div>
'''
    
    html += f'''
        </div>

        <!-- Submit Button -->
        <button onclick="checkAnswers()" class="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold py-4 rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg">
            <i class="fas fa-check-double ml-2"></i>تحقق من الإجابات
        </button>

        <!-- Score Display -->
        <div id="scoreDisplay" class="hidden score-display">
            <i class="fas fa-trophy ml-2"></i>
            <span id="scoreText"></span>
        </div>

    </main>

    <!-- Footer -->
    <footer class="mt-16 py-6 md:py-8 text-white text-center" style="background: linear-gradient(135deg, #22c55e, #10b981);">
        <div class="container mx-auto px-6">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                <a href="../index.html" class="hover:opacity-80 transition">
                    <i class="fas fa-brain text-xl md:text-2xl mr-2"></i>
                    <span class="font-semibold text-sm md:text-base">Context Arabic</span>
                </a>
                <p class="text-xs md:text-sm opacity-90">&copy; 2025 - Learn Arabic in Context</p>
                <a href="index.html" class="hover:opacity-80 transition">
                    <span class="font-semibold text-sm md:text-base">Back to Listening</span>
                    <i class="fas fa-arrow-right ml-2"></i>
                </a>
            </div>
        </div>
    </footer>

    <script>
        // Track play count
        let playCount = 0;
        const audioPlayer = document.getElementById('audioPlayer');
        const playCountDisplay = document.getElementById('playCount');
        
        audioPlayer.addEventListener('play', () => {{
            playCount++;
            playCountDisplay.textContent = playCount;
        }});

        // Store answers
        const tfAnswers = {{}};
        const mcqAnswers = {{}};
        const tfCorrect = {{{','.join(f'{i+1}: {str(q["correct"]).lower()}' for i, q in enumerate(questions['tf']))}}};
        const mcqCorrect = {{}};
        
        // Store MCQ correct answers
        {chr(10).join(f"mcqCorrect[{i + len(questions['tf']) + 1}] = {next((str(opt['correct']).lower() for opt in q['options'] if opt['correct']), 'false')};" for i, q in enumerate(questions['mcq']))}

        function selectTF(btn, qnum, answer) {{
            // Deselect other buttons in this question
            document.querySelectorAll(`[data-question="${{qnum}}"].tf-option`).forEach(b => {{
                b.classList.remove('selected');
            }});
            
            btn.classList.add('selected');
            tfAnswers[qnum] = (answer === 'true');
        }}

        function selectMCQ(btn, qnum) {{
            // Deselect other buttons in this question
            document.querySelectorAll(`[data-question="${{qnum}}"].mcq-option`).forEach(b => {{
                b.classList.remove('selected');
            }});
            
            btn.classList.add('selected');
            mcqAnswers[qnum] = (btn.dataset.correct === 'true');
        }}

        function checkAnswers() {{
            let tfScore = 0;
            let mcqScore = 0;
            
            // Check T/F
            Object.keys(tfCorrect).forEach(qnum => {{
                const buttons = document.querySelectorAll(`[data-question="${{qnum}}"].tf-option`);
                const userAnswer = tfAnswers[qnum];
                const correct = tfCorrect[qnum];
                
                buttons.forEach(btn => {{
                    btn.classList.remove('correct', 'incorrect');
                    const btnAnswer = (btn.dataset.answer === 'true');
                    
                    if (btnAnswer === correct) {{
                        btn.classList.add('correct');
                    }} else if (btn.classList.contains('selected')) {{
                        btn.classList.add('incorrect');
                    }}
                }});
                
                if (userAnswer === correct) {{
                    tfScore++;
                }}
            }});
            
            // Check MCQ
            Object.keys(mcqCorrect).forEach(qnum => {{
                const buttons = document.querySelectorAll(`[data-question="${{qnum}}"].mcq-option`);
                const userAnswer = mcqAnswers[qnum];
                const correct = mcqCorrect[qnum];
                
                buttons.forEach(btn => {{
                    btn.classList.remove('correct', 'incorrect');
                    const isCorrect = (btn.dataset.correct === 'true');
                    
                    if (isCorrect) {{
                        btn.classList.add('correct');
                    }} else if (btn.classList.contains('selected')) {{
                        btn.classList.add('incorrect');
                    }}
                }});
                
                if (userAnswer === correct) {{
                    mcqScore++;
                }}
            }});
            
            // Display score
            const totalScore = tfScore + mcqScore;
            const totalQuestions = Object.keys(tfCorrect).length + Object.keys(mcqCorrect).length;
            const percentage = Math.round((totalScore / totalQuestions) * 100);
            
            const scoreDisplay = document.getElementById('scoreDisplay');
            const scoreText = document.getElementById('scoreText');
            
            scoreText.textContent = `نتيجتك: ${{totalScore}} من ${{totalQuestions}} (${{percentage}}%)`;
            scoreDisplay.classList.remove('hidden');
            
            // Scroll to score
            scoreDisplay.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
    </script>
</body>
</html>'''
    
    # Write HTML file
    output_path = output_dir / f"{lesson_info['filename']}.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return lesson_info['filename']

def main():
    source_dir = Path('/Users/SEMESTERS/OLD/Summer25/Lis')
    output_dir = Path('/Users/muhammadsabdo/ArabicSimplified/Listening')
    
    generated_files = []
    
    print("🎧 Generating Listening Lessons...")
    print("=" * 50)
    
    for docx_file, lesson_info in LESSONS.items():
        docx_path = source_dir / docx_file
        
        if not docx_path.exists():
            print(f"⚠️  {docx_file} not found")
            continue
        
        print(f"\n📄 Processing: {lesson_info['title_ar']}")
        
        # Extract text
        paragraphs = extract_text_from_docx(docx_path)
        
        # Parse questions
        questions = parse_questions(paragraphs)
        
        print(f"   ✓ Found {len(questions['tf'])} T/F questions")
        print(f"   ✓ Found {len(questions['mcq'])} MCQ questions")
        
        # Generate HTML
        filename = generate_html(lesson_info, questions, output_dir)
        generated_files.append({
            'filename': filename,
            'title_ar': lesson_info['title_ar'],
            'title_en': lesson_info['title_en'],
            'level': lesson_info['level']
        })
        
        print(f"   ✅ Generated: {filename}.html")
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully generated {len(generated_files)} lesson pages!")
    print("\nGenerated files:")
    for f in generated_files:
        print(f"  • {f['filename']}.html - {f['title_ar']}")

if __name__ == '__main__':
    main()
