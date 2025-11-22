# Makefile for HW05_Nicolas_Leone_1986354

# Target and source
BENCHMARK = drbg_benchmark.py
TEX_FILE = HW05_Nicolas_Leone_1986354.tex
PDF_FILE = HW05_Nicolas_Leone_1986354.pdf

# Run benchmark to generate plots
benchmark: $(BENCHMARK)
	@echo "🔬 Running DRBG benchmark..."
	@python3 $(BENCHMARK)
	@echo "✅ Benchmark complete!"

# Compile LaTeX document
pdf: $(TEX_FILE)
	@echo "📄 Compiling LaTeX document..."
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Done! PDF generated: $(PDF_FILE)"

# Complete workflow: run benchmark then generate PDF
all: benchmark pdf

# Clean temporary files
clean:
	@rm -f *.aux *.log *.out *.toc

# Clean everything including PDF and generated files
cleanall: clean
	@rm -f $(PDF_FILE) *.png summary_table.tex

.PHONY: clean cleanall pdf all benchmark
