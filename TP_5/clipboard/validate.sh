#!/usr/bin/env bash

set -e

MODULE_NAME="clipboard"
PROC_ENTRY="/proc/clipboard"

echo "============================================================"
echo " TP5 - Clipboard /proc Validation"
echo "============================================================"
echo

echo "============================================================"
echo " STEP 0 - Cleaning previous state"
echo "============================================================"

sudo rmmod ${MODULE_NAME} 2>/dev/null || true

sudo dmesg -C || true

make clean || true

echo
echo "[OK] Previous state cleaned"
echo

echo "============================================================"
echo " STEP 1 - Building module"
echo "============================================================"

make

echo
echo "[OK] Build completed"
echo

echo "============================================================"
echo " STEP 2 - Inserting module"
echo "============================================================"

sudo insmod ${MODULE_NAME}.ko

echo
echo "[OK] Module inserted"
echo

echo "============================================================"
echo " STEP 3 - Checking loaded modules"
echo "============================================================"

lsmod | grep ${MODULE_NAME} || true

echo

echo "============================================================"
echo " STEP 4 - Checking /proc entry"
echo "============================================================"

ls -l ${PROC_ENTRY}

echo

echo "============================================================"
echo " STEP 5 - Initial kernel logs"
echo "============================================================"

sudo dmesg | tail -20

echo

echo "============================================================"
echo " STEP 6 - Writing to clipboard"
echo "============================================================"

echo "Hola, somos asm-noobs..." | sudo tee ${PROC_ENTRY}

echo
echo "[OK] Write completed"
echo

echo "============================================================"
echo " STEP 7 - Reading from clipboard"
echo "============================================================"

cat ${PROC_ENTRY}

echo
echo "[OK] Read completed"
echo

echo

echo "============================================================"
echo " STEP 8 - Kernel logs after read/write"
echo "============================================================"

sudo dmesg | tail -20

echo

echo "============================================================"
echo " STEP 9 - Removing module"
echo "============================================================"

sudo rmmod ${MODULE_NAME}

echo
echo "[OK] Module removed"
echo

echo "============================================================"
echo " STEP 10 - Kernel logs after removal"
echo "============================================================"

sudo dmesg | tail -20

echo

echo "============================================================"
echo " STEP 11 - Verifying unload"
echo "============================================================"

lsmod | grep ${MODULE_NAME} || true

echo

echo "============================================================"
echo " STEP 12 - Cleanup"
echo "============================================================"

make clean

echo
echo "[OK] Cleanup completed"
echo

echo "============================================================"
echo " Clipboard Validation Completed"
echo "============================================================"
