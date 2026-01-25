#!/bin/bash
# CCRS-2 Installation Script
# Install the CCRS-2 CLI wrapper system-wide

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation locations
INSTALL_DIR="/usr/local/bin"
CCRS2_HOME="$HOME/.ccrs2"

show_logo() {
    echo -e "${BLUE}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║         CCRS-2 INSTALLER              ║"
    echo "  ║    Claude Code Routing Service        ║"
    echo -e "  ║           ${GREEN}Simple & Effective${BLUE}           ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

show_help() {
    show_logo
    echo "Install CCRS-2 CLI wrapper system-wide"
    echo
    echo -e "${GREEN}USAGE:${NC}"
    echo "  ./install.sh [OPTIONS]"
    echo
    echo -e "${GREEN}OPTIONS:${NC}"
    echo "  --global         Install system-wide (requires sudo)"
    echo "  --local          Install to user's local bin"
    echo "  --uninstall      Remove installed CCRS-2"
    echo "  --help           Show this help"
    echo
    echo -e "${GREEN}EXAMPLES:${NC}"
    echo "  ./install.sh --global     # Install for all users"
    echo "  ./install.sh --local      # Install for current user"
    echo "  ./install.sh --uninstall  # Remove installation"
}

# Check if running from CCRS-2 directory
check_location() {
    if [[ ! -f "./ccrs2" ]] || [[ ! -f "./cli.py" ]]; then
        echo -e "${RED}❌ Error: Must run from CCRS-2 directory${NC}" >&2
        echo -e "   Make sure you have ccrs2 and cli.py files" >&2
        exit 1
    fi
}

# Install globally (requires sudo)
install_global() {
    echo -e "${BLUE}🚀 Installing CCRS-2 globally...${NC}"

    # Check sudo permissions
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}📋 Need sudo permissions for global installation${NC}"
        sudo -v || {
            echo -e "${RED}❌ Sudo required for global installation${NC}" >&2
            exit 1
        }
    fi

    # Create CCRS2_HOME directory
    mkdir -p "$CCRS2_HOME"

    # Copy files to CCRS2_HOME
    echo -e "${GREEN}📁 Copying files to $CCRS2_HOME${NC}"
    cp -r ./* "$CCRS2_HOME/"
    chmod +x "$CCRS2_HOME/ccrs2"

    # Create wrapper script in /usr/local/bin
    echo -e "${GREEN}🔗 Creating global wrapper${NC}"
    sudo tee "$INSTALL_DIR/ccrs2" > /dev/null << EOF
#!/bin/bash
# CCRS-2 Global Wrapper
export CCRS2_INSTALLED_DIR="$CCRS2_HOME"
cd "$CCRS2_HOME"
exec "./ccrs2" "\$@"
EOF

    sudo chmod +x "$INSTALL_DIR/ccrs2"

    echo -e "${GREEN}✅ CCRS-2 installed globally!${NC}"
    echo -e "   Command available: ${YELLOW}ccrs2${NC}"
    echo -e "   Installation directory: ${BLUE}$CCRS2_HOME${NC}"
}

# Install locally to user bin
install_local() {
    echo -e "${BLUE}🚀 Installing CCRS-2 locally...${NC}"

    # Local bin directory
    LOCAL_BIN="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN"
    mkdir -p "$CCRS2_HOME"

    # Copy files to CCRS2_HOME
    echo -e "${GREEN}📁 Copying files to $CCRS2_HOME${NC}"
    cp -r ./* "$CCRS2_HOME/"
    chmod +x "$CCRS2_HOME/ccrs2"

    # Create wrapper script in local bin
    echo -e "${GREEN}🔗 Creating local wrapper${NC}"
    cat > "$LOCAL_BIN/ccrs2" << EOF
#!/bin/bash
# CCRS-2 Local Wrapper
export CCRS2_INSTALLED_DIR="$CCRS2_HOME"
cd "$CCRS2_HOME"
exec "./ccrs2" "\$@"
EOF

    chmod +x "$LOCAL_BIN/ccrs2"

    # Check if local bin is in PATH
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        echo -e "${YELLOW}⚠️  $LOCAL_BIN not in PATH${NC}"
        echo -e "   Add this to your shell config (.bashrc, .zshrc):"
        echo -e "   ${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo
    fi

    echo -e "${GREEN}✅ CCRS-2 installed locally!${NC}"
    echo -e "   Command available: ${YELLOW}ccrs2${NC}"
    echo -e "   Installation directory: ${BLUE}$CCRS2_HOME${NC}"
}

# Uninstall CCRS-2
uninstall() {
    echo -e "${YELLOW}🗑️  Uninstalling CCRS-2...${NC}"

    # Remove global installation
    if [[ -f "$INSTALL_DIR/ccrs2" ]]; then
        echo -e "${BLUE}Removing global installation${NC}"
        sudo rm -f "$INSTALL_DIR/ccrs2"
    fi

    # Remove local installation
    if [[ -f "$HOME/.local/bin/ccrs2" ]]; then
        echo -e "${BLUE}Removing local installation${NC}"
        rm -f "$HOME/.local/bin/ccrs2"
    fi

    # Remove CCRS2_HOME (ask for confirmation)
    if [[ -d "$CCRS2_HOME" ]]; then
        echo -e "${YELLOW}Remove CCRS-2 files from $CCRS2_HOME? [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf "$CCRS2_HOME"
            echo -e "${GREEN}✅ CCRS-2 files removed${NC}"
        fi
    fi

    echo -e "${GREEN}✅ CCRS-2 uninstalled!${NC}"
}

# Test installation
test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${NC}"

    if command -v ccrs2 &> /dev/null; then
        echo -e "${GREEN}✅ ccrs2 command found${NC}"
        ccrs2 --version
        return 0
    else
        echo -e "${RED}❌ ccrs2 command not found${NC}"
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