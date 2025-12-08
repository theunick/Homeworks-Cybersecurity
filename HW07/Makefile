.PHONY: build run test logs clean cleanall pdf help

# Docker targets
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

run:
	@echo "🎲 Running dice game..."
	docker-compose up

test:
	@echo "🧪 Running test match..."
	@$(MAKE) build
	@docker-compose up --abort-on-container-exit
	@echo "✅ Test complete!"

logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

clean-docker:
	@echo "🧹 Cleaning Docker containers and networks..."
	docker-compose down
	@echo "✅ Docker cleanup complete!"

# LaTeX targets
pdf:
	@echo "📄 Compiling LaTeX document..."
	@pdflatex -interaction=nonstopmode HW07_Nicolas_Leone_1986354.tex > /dev/null
	@pdflatex -interaction=nonstopmode HW07_Nicolas_Leone_1986354.tex > /dev/null
	@pdflatex -interaction=nonstopmode HW07_Nicolas_Leone_1986354.tex > /dev/null
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Done! PDF generated: HW07_Nicolas_Leone_1986354.pdf"

# Cleanup targets
clean:
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Cleanup complete!"

cleanall: clean clean-docker
	@echo "🧹 Removing PDF..."
	@rm -f HW07_Nicolas_Leone_1986354.pdf
	@docker rmi -f hw07-alice hw07-bob 2>/dev/null || true
	@echo "✅ Full cleanup complete!"

help:
	@echo "Available targets:"
	@echo "  build        - Build Docker images"
	@echo "  run          - Run the dice game"
	@echo "  test         - Build and run test match"
	@echo "  logs         - Show Docker logs"
	@echo "  pdf          - Compile LaTeX document"
	@echo "  clean        - Remove temporary files"
	@echo "  clean-docker - Remove Docker containers"
	@echo "  cleanall     - Full cleanup (files + Docker + PDF)"
