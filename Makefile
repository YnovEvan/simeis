# --- Couleurs pour l'affichage ---
HELP_COLOR=\033[36m
RESET=\033[0m

## help: Affiche cette aide
help:
	@echo "Usage:"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## init : Installation de rust et des composants nécessaires (clippy, rustfmt)
init: 
	@echo "${HELP_COLOR}==> Installation de rust en cours...${RESET}"
	rustup update stable && rustup default stable
	cargo install --locked typst-cli
	rustup component add rustfmt
	rustup component add clippy

## build: Compile le binaire pour l'OS actuel
build: init
	@echo "${HELP_COLOR}==> Compilation en cours...${RESET}"
	RUSTFLAGS="-Ccode-model=kernel -Ccodegen-units=1" cargo build --verbose

## build-release: Compile le binaire en mode release
build-release: init
	@echo "${HELP_COLOR}==> Compilation en mode release...${RESET}"
	cargo build --release --verbose

# test: Compile et lance les tests
test: build
	@echo "${HELP_COLOR}==> Lancement des tests...${RESET}"
	cargo test --verbose

# test-release: Compile et lance les tests en mode release
test-release: build-release
	@echo "${HELP_COLOR}==> Lancement des tests en mode release...${RESET}"
	cargo test --release --verbose

# lint: Lint le code avec clippy et traite les warnings comme des erreurs
lint:
	@echo "${HELP_COLOR}==> Linting du code...${RESET}"
	cargo clippy -- -D warnings

# fmt: Formate le code avec rustfmt et traite les erreurs de formatage comme des erreurs
fmt:
	@echo "${HELP_COLOR}==> Formatage du code...${RESET}"
	cargo fmt --all -- --check

## start: Compile et lance l'application
start: build
	@echo "${HELP_COLOR}==> Lancement de l'application...${RESET}"
	cargo run 

## start: Lance l'application simplement
run: 
	@echo "${HELP_COLOR}==> Lancement de l'application...${RESET}"
	cargo run

## docu: Création de la documentation (en cas d'erreur : make init)
docu:
	@echo "${HELP_COLOR}==> Generation de la documentation...${RESET}"
	typst compile ./doc/manual.typ ./doc/manuel.pdf