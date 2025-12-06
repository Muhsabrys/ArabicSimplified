// Standardized Context Arabic Template Components
// This provides consistent navigation and styling across all lesson pages

const ContextTemplate = {
    // Module color schemes matching the main index
    colors: {
        Reading: { primary: '#64748b', accent: '#f97316', border: '#cbd5e1' },
        Listening: { primary: '#22c55e', accent: '#10b981', border: '#bbf7d0' },
        Vocabulary: { primary: '#a78bfa', accent: '#ec4899', border: '#e9d5ff' },
        Grammar: { primary: '#0ea5e9', accent: '#06b6d4', border: '#bae6fd' },
        Quizzes: { primary: '#eab308', accent: '#f59e0b', border: '#fde047' },
        Games: { primary: '#ef4444', accent: '#f59e0b', border: '#fecaca' },
        Culture: { primary: '#d97706', accent: '#fbbf24', border: '#fde68a' },
        EgyptianArabic: { primary: '#22c55e', accent: '#10b981', border: '#bbf7d0' }
    },

    // Generate consistent header HTML
    getHeader(moduleName, lessonTitle) {
        const colors = this.colors[moduleName] || this.colors.Reading;
        return `
    <nav class="sticky top-0 z-50 shadow-lg" style="background: linear-gradient(135deg, ${colors.primary}, ${colors.accent});">
        <div class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <a href="../index.html" class="flex items-center gap-3 text-white hover:opacity-80 transition">
                    <i class="fas fa-home text-2xl"></i>
                    <span class="font-semibold text-lg hidden md:inline">Home</span>
                </a>
                <div class="text-center flex-1">
                    <h1 class="text-2xl md:text-3xl font-bold text-white">${lessonTitle}</h1>
                </div>
                <a href="index.html" class="flex items-center gap-3 text-white hover:opacity-80 transition">
                    <span class="font-semibold text-lg hidden md:inline">${moduleName}</span>
                    <i class="fas fa-arrow-right text-2xl"></i>
                </a>
            </div>
        </div>
    </nav>
        `;
    },

    // Generate consistent footer HTML
    getFooter(moduleName) {
        const colors = this.colors[moduleName] || this.colors.Reading;
        return `
    <footer class="mt-16 py-8 text-white text-center" style="background: linear-gradient(135deg, ${colors.primary}, ${colors.accent});">
        <div class="container mx-auto px-6">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                <a href="../index.html" class="hover:opacity-80 transition">
                    <i class="fas fa-brain text-2xl mr-2"></i>
                    <span class="font-semibold">Context Arabic</span>
                </a>
                <p class="text-sm opacity-90">&copy; 2025 - Learn Arabic in Context</p>
                <a href="index.html" class="hover:opacity-80 transition">
                    <span class="font-semibold">Back to ${moduleName}</span>
                    <i class="fas fa-arrow-right ml-2"></i>
                </a>
            </div>
        </div>
    </footer>
        `;
    },

    // Required CSS/JS imports
    getRequiredImports() {
        return `
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Lato', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .font-arabic {
            font-family: 'Cairo', sans-serif;
        }
        main {
            flex: 1;
        }
        html {
            scroll-behavior: smooth;
        }
    </style>
        `;
    }
};
