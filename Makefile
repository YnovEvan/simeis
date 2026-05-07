# --- Couleurs pour l'affichage ---
HELP_COLOR=\033[36m
RESET=\033[0m

## ------------------------ Rust ------------------------ ##

## help: Affiche cette aide
help:
	@echo "Usage:"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## rust-init : Installation de rust et des composants nécessaires (clippy, rustfmt)
rust-init:
	@echo "${HELP_COLOR}==> Installation de rust en cours...${RESET}"
	rustup update stable && rustup default stable
	cargo install --locked typst-cli
	rustup component add rustfmt
	rustup component add clippy

## rust-build: Compile le binaire pour l'OS actuel
rust-build: init
	@echo "${HELP_COLOR}==> Compilation en cours...${RESET}"
	RUSTFLAGS="-Ccode-model=kernel -Ccodegen-units=1" cargo build --verbose

## rust-build-release: Compile le binaire en mode release
rust-build-release: init
	@echo "${HELP_COLOR}==> Compilation en mode release...${RESET}"
	cargo build --release --verbose

# rust-test: Compile et lance les tests
rust-test: build
	@echo "${HELP_COLOR}==> Lancement des tests...${RESET}"
	cargo test --verbose

# rust-test-release: Compile et lance les tests en mode release
rust-test-release: build-release
	@echo "${HELP_COLOR}==> Lancement des tests en mode release...${RESET}"
	cargo test --release --verbose

# lint: Lint le code rust avec clippy et traite les warnings comme des erreurs
rust-lint:
	@echo "${HELP_COLOR}==> Linting du code...${RESET}"
	cargo clippy -- -D warnings

# fmt: Formate le code avec rustfmt et traite les erreurs de formatage comme des erreurs
rust-fmt:
	@echo "${HELP_COLOR}==> Formatage du code...${RESET}"
	cargo fmt --all -- --check

## rust-start: Compile et lance l'application
rust-start: build
	@echo "${HELP_COLOR}==> Lancement de l'application...${RESET}"
	cargo run

## rust-docu: Création de la documentation (en cas d'erreur : make init)
rust-docu:
	@echo "${HELP_COLOR}==> Generation de la documentation...${RESET}"
	typst compile ./doc/manual.typ ./doc/manuel.pdf

## rust-check: Vérifier que le code rust compile bien
rust-check:
	@echo "${HELP_COLOR}==> Verification de la compilation...${RESET}"
	cargo check


## ------------------------ Python ------------------------ ##

python-init:
	@echo "${HELP_COLOR}==> Installation de python...${RESET}"
	python -m venv test_env
	ls test_env
	test_env/Scripts/python -m pip install --upgrade pip
	test_env/Scripts/pip install --upgrade pylint
	test_env/Scripts/pip install --upgrade black

## python-lint : Lint le code python avec clippy et traite les warnings comme des erreurs
python-lint:
	@echo "${HELP_COLOR}==> Linting du code python...${RESET}"
	test_env/Scripts/pylint */*.py --disable=W

python-fmt:
	@echo "${HELP_COLOR}==> Formatage du code python...${RESET}"
	test_env/Scripts/black */*.py


init: rust-init python-init

lint: rust-lint python-lint

fmt: rust-fmt python-fmt
