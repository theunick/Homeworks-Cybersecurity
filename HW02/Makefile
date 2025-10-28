# Makefile per HW02_Nicolas_Leone_1986354.c

# Percorsi OpenSSL da Homebrew
OPENSSL_PATH = /opt/homebrew/opt/openssl@3
OPENSSL_INCLUDE = $(OPENSSL_PATH)/include
OPENSSL_LIB = $(OPENSSL_PATH)/lib

# Compiler e flags
CC = gcc
CFLAGS = -Wall -I$(OPENSSL_INCLUDE)
LDFLAGS = -L$(OPENSSL_LIB) -lssl -lcrypto

# Target e source
TARGET = HW02
SOURCE = HW02_Nicolas_Leone_1986354.c
TEX_FILE = HW02_Nicolas_Leone_1986354.tex
PDF_FILE = HW02_Nicolas_Leone_1986354.pdf

# Regola di compilazione C
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET) $(LDFLAGS)

# Regola per compilare LaTeX
pdf: $(TEX_FILE)
	@echo "📄 Compiling LaTeX document..."
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Done! PDF generated: $(PDF_FILE)"

# Regola per pulire
clean:
	rm -f $(TARGET) *.aux *.log *.out *.toc

# Regola per pulire anche il PDF
cleanall: clean
	rm -f $(PDF_FILE)

# Regola per eseguire
run: $(TARGET)
	./$(TARGET)

.PHONY: clean cleanall run pdf
