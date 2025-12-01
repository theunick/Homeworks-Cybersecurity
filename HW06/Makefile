# Makefile for HW06_Nicolas_Leone_1986354

# Docker images and containers
DOCKER_COMPOSE = docker-compose
PROJECT_NAME = hw06

# LaTeX files
TEX_FILE = HW06_Nicolas_Leone_1986354.tex
PDF_FILE = HW06_Nicolas_Leone_1986354.pdf

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	$(DOCKER_COMPOSE) build

# Run the game
run:
	@echo "🎮 Starting Rock-Paper-Scissors game..."
	$(DOCKER_COMPOSE) up --abort-on-container-exit

# Run in detached mode
run-detached:
	@echo "🎮 Starting game in background..."
	$(DOCKER_COMPOSE) up -d

# Stop containers
stop:
	@echo "🛑 Stopping containers..."
	$(DOCKER_COMPOSE) stop

# View logs
logs:
	$(DOCKER_COMPOSE) logs -f

# Clean Docker containers and networks
clean-docker:
	@echo "🧹 Cleaning up Docker containers and networks..."
	$(DOCKER_COMPOSE) down

# Compile LaTeX document
pdf: $(TEX_FILE)
	@echo "📄 Compiling LaTeX document..."
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@pdflatex -interaction=nonstopmode $(TEX_FILE) > /dev/null 2>&1 || true
	@echo "🧹 Cleaning temporary files..."
	@rm -f *.aux *.log *.out *.toc
	@echo "✅ Done! PDF generated: $(PDF_FILE)"

# Run test game and generate PDF
all: build run pdf

# Test: build and run one game
test: build
	@echo "🧪 Running test game..."
	$(DOCKER_COMPOSE) up --abort-on-container-exit
	@echo "✅ Test complete!"

# Clean temporary LaTeX files
clean:
	@rm -f *.aux *.log *.out *.toc

# Clean everything including PDF and Docker images
cleanall: clean clean-docker
	@rm -f $(PDF_FILE)
	@echo "🧹 Removing Docker images..."
	@docker rmi -f $(PROJECT_NAME)-alice $(PROJECT_NAME)-bob 2>/dev/null || true
	@echo "✅ Cleanup complete"

.PHONY: build run run-detached stop logs clean-docker pdf all test clean cleanall
