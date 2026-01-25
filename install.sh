#!/bin/bash
# CCRS Installation Script
# Install the CCRS CLI wrapper system-wide

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation locations
INSTALL_DIR="/usr/local/bin"
CCRS_HOME="$HOME/.ccrs"

show_logo() {
    echo -e "${BLUE}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║         CCRS INSTALLER              ║"
    echo "  ║    Claude Code Routing Service        ║"
    echo -e "  ║           ${GREEN}Simple & Effective${BLUE}           ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

show_help() {
    show_logo
    echo "Install CCRS CLI wrapper system-wide"
    echo
    echo -e "${GREEN}USAGE:${NC}"
    echo "  ./install.sh [OPTIONS]"
    echo
    echo -e "${GREEN}OPTIONS:${NC}"
    echo "  --global         Install system-wide (requires sudo)"
    echo "  --local          Install to user's local bin"
    echo "  --uninstall      Remove installed CCRS"
    echo "  --help           Show this help"
    echo
    echo -e "${GREEN}EXAMPLES:${NC}"
    echo "  ./install.sh --global     # Install for all users"
    echo "  ./install.sh --local      # Install for current user"
    echo "  ./install.sh --uninstall  # Remove installation"
}

# Check if running from CCRS directory
check_location() {
    if [[ ! -f "./ccrs" ]] || [[ ! -f "./cli.py" ]]; then
        echo -e "${RED}❌ Error: Must run from CCRS directory${NC}" >&2
        echo -e "   Make sure you have ccrs and cli.py files" >&2
        exit 1
    fi
}

# Install globally (requires sudo)
install_global() {
    echo -e "${BLUE}🚀 Installing CCRS globally...${NC}"

    # Check sudo permissions
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}📋 Need sudo permissions for global installation${NC}"
        sudo -v || {
            echo -e "${RED}❌ Sudo required for global installation${NC}" >&2
            exit 1
        }
    fi

    # Create CCRS_HOME directory
    mkdir -p "$CCRS_HOME"

    # Copy files to CCRS_HOME
    echo -e "${GREEN}📁 Copying files to $CCRS_HOME${NC}"
    cp -r ./* "$CCRS_HOME/"
    chmod +x "$CCRS_HOME/ccrs"

    # Create wrapper script in /usr/local/bin
    echo -e "${GREEN}🔗 Creating global wrapper${NC}"
    sudo tee "$INSTALL_DIR/ccrs" > /dev/null << EOF
#!/bin/bash
# CCRS Global Wrapper
export CCRS_INSTALLED_DIR="$CCRS_HOME"
cd "$CCRS_HOME"
exec "./ccrs" "\$@"
EOF

    sudo chmod +x "$INSTALL_DIR/ccrs"

    echo -e "${GREEN}✅ CCRS installed globally!${NC}"
    echo -e "   Command available: ${YELLOW}ccrs${NC}"
    echo -e "   Installation directory: ${BLUE}$CCRS_HOME${NC}"
}

# Install locally to user bin
install_local() {
    echo -e "${BLUE}🚀 Installing CCRS locally...${NC}"

    # Local bin directory
    LOCAL_BIN="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN"
    mkdir -p "$CCRS_HOME"

    # Copy files to CCRS_HOME
    echo -e "${GREEN}📁 Copying files to $CCRS_HOME${NC}"
    cp -r ./* "$CCRS_HOME/"
    chmod +x "$CCRS_HOME/ccrs"

    # Create wrapper script in local bin
    echo -e "${GREEN}🔗 Creating local wrapper${NC}"
    cat > "$LOCAL_BIN/ccrs" << EOF
#!/bin/bash
# CCRS Local Wrapper
export CCRS_INSTALLED_DIR="$CCRS_HOME"
cd "$CCRS_HOME"
exec "./ccrs" "\$@"
EOF

    chmod +x "$LOCAL_BIN/ccrs"

    # Check if local bin is in PATH
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        echo -e "${YELLOW}⚠️  $LOCAL_BIN not in PATH${NC}"
        echo -e "   Add this to your shell config (.bashrc, .zshrc):"
        echo -e "   ${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo
    fi

    echo -e "${GREEN}✅ CCRS installed locally!${NC}"
    echo -e "   Command available: ${YELLOW}ccrs${NC}"
    echo -e "   Installation directory: ${BLUE}$CCRS_HOME${NC}"
}

# Uninstall CCRS
uninstall() {
    echo -e "${YELLOW}🗑️  Uninstalling CCRS...${NC}"

    # Remove global installation
    if [[ -f "$INSTALL_DIR/ccrs" ]]; then
        echo -e "${BLUE}Removing global installation${NC}"
        sudo rm -f "$INSTALL_DIR/ccrs"
    fi

    # Remove local installation
    if [[ -f "$HOME/.local/bin/ccrs" ]]; then
        echo -e "${BLUE}Removing local installation${NC}"
        rm -f "$HOME/.local/bin/ccrs"
    fi

    # Remove CCRS_HOME (ask for confirmation)
    if [[ -d "$CCRS_HOME" ]]; then
        echo -e "${YELLOW}Remove CCRS files from $CCRS_HOME? [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf "$CCRS_HOME"
            echo -e "${GREEN}✅ CCRS files removed${NC}"
        fi
    fi

    echo -e "${GREEN}✅ CCRS uninstalled!${NC}"
}

# Test installation
test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${NC}"

    if command -v ccrs &> /dev/null; then
        echo -e "${GREEN}✅ ccrs command found${NC}"
        ccrs --version
        return 0
    else
        echo -e "${RED}❌ ccrs command not found${NC}"
        return 1
    fi
}

# Main function
main() {
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --global)
            check_location
            install_global
            test_installation
            ;;
        --local)
            check_location
            install_local
            test_installation
            ;;
        --uninstall)
            uninstall
            ;;
        "")
            show_help
            echo
            echo -e "${YELLOW}Choose installation type:${NC}"
            echo -e "  ${GREEN}1)${NC} Global installation (all users, requires sudo)"
            echo -e "  ${GREEN}2)${NC} Local installation (current user only)"
            echo -e "  ${GREEN}3)${NC} Exit"
            echo
            read -p "Enter choice [1-3]: " choice
            case $choice in
                1)
                    check_location
                    install_global
                    test_installation
                    ;;
                2)
                    check_location
                    install_local
                    test_installation
                    ;;
                3)
                    echo "Exiting..."
                    exit 0
                    ;;
                *)
                    echo -e "${RED}Invalid choice${NC}"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            show_help
            exit 1
            ;;
    esac
}

main "$@"