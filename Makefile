# --- Couleurs pour l'affichage ---
HELP_COLOR=\033[36m
RESET=\033[0m

ifdef OS
   VENV = test_env/Scripts
else
   ifeq ($(shell uname), Linux)
      VENV = test_env/bin
   endif
endif


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
rust-build: rust-init
	@echo "${HELP_COLOR}==> Compilation en cours...${RESET}"
	RUSTFLAGS="-Ccode-model=kernel -Ccodegen-units=1" cargo build --verbose

## rust-build-heavy-testing: Compile le binaire avec les features heavy-testing
rust-build-heavy-testing: rust-init
	@echo "${HELP_COLOR}==> Compilation en cours...${RESET}"
	cargo build --profile=heavy-testing --features=heavy-testing

rust-heavy-test: rust-build-heavy-testing
	@echo "${HELP_COLOR}==> Lancement des tests avec heavy-testing...${RESET}"
	python3 tests/main.py

## rust-build-release: Compile le binaire en mode release
rust-build-release: rust-init
	@echo "${HELP_COLOR}==> Compilation en mode release...${RESET}"
	cargo build --release --verbose

# rust-test: Compile et lance les tests
rust-test: rust-build
	@echo "${HELP_COLOR}==> Lancement des tests...${RESET}"
	cargo test --verbose

# rust-test-release: Compile et lance les tests en mode release
rust-test-release: rust-build-release
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

# audit: Vérifie les vulnérabilités dans les dépendances
rust-audit: rust-init
	@echo "${HELP_COLOR}==> Audit du code...${RESET}"
	cargo audit

# udeps: Vérifie les dépendances non utilisées
rust-udeps: rust-init
	@echo "${HELP_COLOR}==> Verification des dependances...${RESET}"
	cargo udeps


## rust-start: Compile et lance l'application
rust-start: rust-build
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
	${VENV}/python -m pip install --upgrade pip
	${VENV}/pip install --upgrade pylint
	${VENV}/pip install --upgrade black

## python-lint : Lint le code python avec clippy et traite les warnings comme des erreurs
python-lint:
	@echo "${HELP_COLOR}==> Linting du code python...${RESET}"
	${VENV}/pylint */*.py --disable=W

python-fmt:
	@echo "${HELP_COLOR}==> Formatage du code python...${RESET}"
	${VENV}/black */*.py


## python-property-test: Lance les tests property-based (mode rapide, 3s par propriété)
python-property-test:
	@echo "${HELP_COLOR}==> Lancement des tests property-based (rapide)...${RESET}"
	${VENV}/python tests/propertybased.py --time 3

## python-property-test-heavy: Lance les tests property-based en mode lourd (120s par propriété)
python-property-test-heavy:
	@echo "${HELP_COLOR}==> Lancement des tests property-based (lourd)...${RESET}"
	${VENV}/python tests/propertybased.py --time 120


init: rust-init python-init

lint: rust-lint python-lint

fmt: rust-fmt python-fmt

test-init: 
	cargo install --locked cargo-tarpaulin

test-coverage: 
	cargo tarpaulin