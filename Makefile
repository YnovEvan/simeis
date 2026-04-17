# --- Couleurs pour l'affichage ---
HELP_COLOR=\033[36m
RESET=\033[0m

## help: Affiche cette aide
help:
	@echo "Usage:"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## init : Installation de rust
init: 
	@echo "${HELP_COLOR}==> Installation de rust en cours...${RESET}"
	rustup update stable && rustup default stable
	cargo install --locked typst-cli
	
## build: Compile le binaire pour l'OS actuel
build: init
	@echo "${HELP_COLOR}==> Compilation en cours...${RESET}"
	RUSTFLAGS="-Ccode-model=kernel -Ccodegen-units=1" cargo build --verbose

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