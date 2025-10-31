# Makefile for HW03_Nicolas_Leone_1986354.c

# OpenSSL paths from Homebrew
OPENSSL_PATH = /opt/homebrew/opt/openssl@3
OPENSSL_INCLUDE = $(OPENSSL_PATH)/include
OPENSSL_LIB = $(OPENSSL_PATH)/lib

# Compiler and flags
CC = gcc
CFLAGS = -Wall -I$(OPENSSL_INCLUDE)
LDFLAGS = -L$(OPENSSL_LIB) -lssl -lcrypto

# Target and source
TARGET = HW03
SOURCE = HW03_Nicolas_Leone_1986354.c
GEN_FILE = generate_testfile.c
GEN_TARGET = generate_testfile
TEX_FILE = HW03_Nicolas_Leone_1986354.tex
PDF_FILE = HW03_Nicolas_Leone_1986354.pdf

# Main compilation rule
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET) $(LDFLAGS)

# Compile test file generator
$(GEN_TARGET): $(GEN_FILE)
	$(CC) $(GEN_FILE) -o $(GEN_TARGET)

# Generate test file
testfile: $(GEN_TARGET)
	./$(GEN_TARGET)

# Run performance tests with single file
run: $(TARGET) testfile_10MB.bin
	@echo "Running performance tests with 10MB file..."
	./$(TARGET) testfile_10MB.bin

# Run tests with all file sizes
run-all: $(TARGET) testfile
	@echo "Running performance tests with all file sizes..."
	./run_all_tests.sh

# Generate charts from results
charts: results_testfile_10MB.bin.csv
	@echo "📊 Generating performance charts..."
	python3 generate_charts.py

# Generate multi-size charts
charts-multi: 
	@echo "📊 Generating multi-size performance charts..."
	python3 generate_charts_multi.py

# Compile LaTeX document
pdf: $(TEX_FILE)
	@echo "📄 Compiling LaTeX document..."
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Done! PDF generated: $(PDF_FILE)"

# Complete workflow
all: $(TARGET) testfile run charts pdf

# Clean binaries and results
clean:
	rm -f $(TARGET) $(GEN_TARGET) testfile.bin results.csv
	rm -f *.aux *.log *.out *.toc

# Clean everything including PDF and charts
cleanall: clean
	rm -f $(PDF_FILE) *.png

.PHONY: clean cleanall run testfile charts pdf all
