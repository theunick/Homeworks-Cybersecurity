# Makefile for HW04_Nicolas_Leone_1986354

# OpenSSL paths from Homebrew
OPENSSL_PATH = /opt/homebrew/opt/openssl@3
OPENSSL_INCLUDE = $(OPENSSL_PATH)/include
OPENSSL_LIB = $(OPENSSL_PATH)/lib

# Compiler and flags
CC = gcc
CFLAGS = -Wall -I$(OPENSSL_INCLUDE)
LDFLAGS = -L$(OPENSSL_LIB) -lssl -lcrypto

# Target and source
TARGET = HW04
SOURCE = HW04_Nicolas_Leone_1986354.c
TEX_FILE = HW04_Nicolas_Leone_1986354.tex
PDF_FILE = HW04_Nicolas_Leone_1986354.pdf

# Main compilation rule (if C program is needed)
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET) $(LDFLAGS)

# Run the program
run: $(TARGET)
	@echo "Running $(TARGET)..."
	./$(TARGET)

# Compile LaTeX document
pdf: $(TEX_FILE)
	@echo "📄 Compiling LaTeX document..."
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Done! PDF generated: $(PDF_FILE)"

# Complete workflow
all: pdf

# Clean binaries and temporary files
clean:
	rm -f $(TARGET)
	rm -f *.aux *.log *.out *.toc

# Clean everything including PDF
cleanall: clean
	rm -f $(PDF_FILE)

.PHONY: clean cleanall run pdf all
