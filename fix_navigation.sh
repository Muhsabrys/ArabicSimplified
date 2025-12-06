#!/bin/bash

# Fix HTML files by adding consistent navigation
# This script adds navigation header and footer to all lesson HTML files

# Define module colors
declare -A MODULE_COLORS_PRIMARY=(
    ["Reading"]="#64748b"
    ["Listening"]="#22c55e"
    ["Vocabulary"]="#a78bfa"
    ["Grammar"]="#0ea5e9"
    ["Quizzes"]="#eab308"
    ["Games"]="#ef4444"
    ["Culture"]="#d97706"
    ["EgyptianArabicModule"]="#22c55e"
)

declare -A MODULE_COLORS_ACCENT=(
    ["Reading"]="#f97316"
    ["Listening"]="#10b981"
    ["Vocabulary"]="#ec4899"
    ["Grammar"]="#06b6d4"
    ["Quizzes"]="#f59e0b"
    ["Games"]="#f59e0b"
    ["Culture"]="#fbbf24"
    ["EgyptianArabicModule"]="#10b981"
)

# Function to create navigation HTML
create_nav() {
    local module="$1"
    local primary="${MODULE_COLORS_PRIMARY[$module]}"
    local accent="${MODULE_COLORS_ACCENT[$module]}"
    
    cat << EOF
    <!-- Context Arabic Navigation -->
    <nav class="sticky top-0 z-50 shadow-lg" style="background: linear-gradient(135deg, ${primary}, ${accent});">
        <div class="container mx-auto px-4 md:px-6 py-3 md:py-4">
            <div class="flex items-center justify-between">
                <a href="../index.html" class="flex items-center gap-2 text-white hover:opacity-80 transition">
                    <i class="fas fa-home text-xl md:text-2xl"></i>
                    <span class="font-semibold text-sm md:text-lg hidden sm:inline">Home</span>
                </a>
                <div class="text-center flex-1 px-4">
                    <span class="text-lg md:text-2xl font-bold text-white">${module}</span>
                </div>
                <a href="index.html" class="flex items-center gap-2 text-white hover:opacity-80 transition">
                    <span class="font-semibold text-sm md:text-lg hidden sm:inline">Module</span>
                    <i class="fas fa-arrow-right text-xl md:text-2xl"></i>
                </a>
            </div>
        </div>
    </nav>
EOF
}

# Function to create footer HTML
create_footer() {
    local module="$1"
    local primary="${MODULE_COLORS_PRIMARY[$module]}"
    local accent="${MODULE_COLORS_ACCENT[$module]}"
    
    cat << EOF
    <!-- Context Arabic Footer -->
    <footer class="mt-16 py-6 md:py-8 text-white text-center" style="background: linear-gradient(135deg, ${primary}, ${accent});">
        <div class="container mx-auto px-6">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                <a href="../index.html" class="hover:opacity-80 transition">
                    <i class="fas fa-brain text-xl md:text-2xl mr-2"></i>
                    <span class="font-semibold text-sm md:text-base">Context Arabic</span>
                </a>
                <p class="text-xs md:text-sm opacity-90">&copy; 2025 - Learn Arabic in Context</p>
                <a href="index.html" class="hover:opacity-80 transition">
                    <span class="font-semibold text-sm md:text-base">Back to ${module}</span>
                    <i class="fas fa-arrow-right ml-2"></i>
                </a>
            </div>
        </div>
    </footer>
EOF
}

# Process each module
MODULES=("Reading" "Listening" "Vocabulary" "Grammar" "Quizzes" "Games" "Culture" "EgyptianArabicModule")

total_files=0
fixed_files=0

for module in "${MODULES[@]}"; do
    module_dir="/Users/muhammadsabdo/ArabicSimplified/${module}"
    
    if [ ! -d "$module_dir" ]; then
        continue
    fi
    
    echo "📁 Processing ${module}..."
    
    # Find all HTML files except index.html
    while IFS= read -r -d '' file; do
        filename=$(basename "$file")
        
        # Skip index.html
        if [ "$filename" = "index.html" ]; then
            continue
        fi
        
        total_files=$((total_files + 1))
        echo "  📄 $filename..."
        
        # Create backup
        cp "$file" "${file}.bak"
        
        # Check if file already has Context Arabic Navigation
        if grep -q "Context Arabic Navigation" "$file"; then
            echo "    ⚠️  Already has navigation, skipping..."
            rm "${file}.bak"
            continue
        fi
        
        # Create temp file with navigation
        {
            # Copy everything up to and including <body
            sed -n '1,/<body/p' "$file"
            
            # Add navigation
            create_nav "$module"
            
            # Add main wrapper start if not exists
            echo '<main class="flex-1">'
            
            # Copy body content (skip <body tag line)
            sed -n '/<body/,/<\/body>/p' "$file" | sed '1d;$d'
            
            # Close main wrapper
            echo '</main>'
            
            # Add footer
            create_footer "$module"
            
            # Copy closing body and html tags
            echo '</body>'
            echo '</html>'
            
        } > "${file}.tmp"
        
        # Replace original with temp
        mv "${file}.tmp" "$file"
        rm "${file}.bak"
        
        fixed_files=$((fixed_files + 1))
        echo "    ✅ Fixed"
        
    done < <(find "$module_dir" -maxdepth 1 -name "*.html" -print0)
done

echo ""
echo "=================================================="
echo "✅ Fixed $fixed_files/$total_files files"
echo "=================================================="
