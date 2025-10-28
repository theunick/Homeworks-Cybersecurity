#!/bin/bash
# Script to compile LaTeX document and clean temporary files
# Usage: ./compile_latex.sh

FILENAME="HW02_Nicolas_Leone_1986354"

echo "📄 Compiling ${FILENAME}.tex..."

# Compile twice for table of contents and references
pdflatex -interaction=nonstopmode "${FILENAME}.tex" > /dev/null
pdflatex -interaction=nonstopmode "${FILENAME}.tex" > /dev/null

# Clean temporary files
echo "🧹 Cleaning temporary files..."
rm -f "${FILENAME}.aux" "${FILENAME}.log" "${FILENAME}.out" "${FILENAME}.toc"

echo "✅ Done! PDF generated: ${FILENAME}.pdf"
