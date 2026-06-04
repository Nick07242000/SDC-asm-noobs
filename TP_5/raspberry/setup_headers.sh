#!/bin/bash

set -e

RPI_USER="asm_noobs"
RPI_HOST="localhost"
RPI_PORT="2222"
KERNEL_VERSION="6.12.25+rpt-rpi-v8"
KBUILD_VERSION="6.12.25+rpt"
TMP_DIR="/tmp/rpi-debs"

echo "==> Limpiando symlinks y headers anteriores..."
sudo rm -f /usr/src/linux-headers-6.12.25+rpt-common-rpi
sudo rm -f /usr/src/linux-headers-6.12.25+rpt-rpi-v8
sudo rm -f /usr/lib/linux-kbuild-6.12.25+rpt

echo "==> Descargando debs en la RPi (apt-get download)..."
ssh -p ${RPI_PORT} ${RPI_USER}@${RPI_HOST} "
  mkdir -p ${TMP_DIR} && cd ${TMP_DIR} &&
  apt-get download \
    linux-headers-${KERNEL_VERSION} \
    linux-headers-6.12.25+rpt-common-rpi \
    linux-kbuild-${KBUILD_VERSION}
"

echo "==> Copiando debs al host..."
scp -P ${RPI_PORT} \
  "${RPI_USER}@${RPI_HOST}:${TMP_DIR}/*.deb" \
  /tmp/

echo "==> Extrayendo debs al sistema..."
sudo dpkg -x /tmp/linux-headers-6.12.25+rpt-common-rpi_*.deb /
sudo dpkg -x /tmp/linux-headers-${KERNEL_VERSION}_*.deb /
sudo dpkg -x /tmp/linux-kbuild-${KBUILD_VERSION}_*.deb /

echo "==> Limpiando debs temporales..."
rm -f /tmp/linux-headers-*.deb /tmp/linux-kbuild-*.deb
ssh -p ${RPI_PORT} ${RPI_USER}@${RPI_HOST} "rm -rf ${TMP_DIR}"

echo "==> Verificando..."
ls /usr/src/linux-headers-${KERNEL_VERSION}/Makefile
ls /usr/src/linux-headers-6.12.25+rpt-common-rpi/Makefile
ls /usr/lib/linux-kbuild-${KBUILD_VERSION}/scripts/Makefile.extrawarn

echo "==