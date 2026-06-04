IMG=2025-05-13-raspios-bookworm-arm64-lite.img
LOOP=$(sudo losetup -P -f --show $IMG)
mkdir -p mnt/boot mnt/rootfs
sudo mount ${LOOP}p1 mnt/boot
sudo mount ${LOOP}p2 mnt/rootfs

sudo touch mnt/boot/ssh

sudo rm -f mnt/rootfs/etc/systemd/system/multi-user.target.wants/userconfig.service

sudo bash -c "echo 'asm_noobs:x:1000:1000:,,,:/home/asm_noobs:/bin/bash' >> mnt/rootfs/etc/passwd"
sudo bash -c "echo 'asm_noobs:x:1000:' >> mnt/rootfs/etc/group"
sudo sed -i '/^sudo:/s/$/,asm_noobs/' mnt/rootfs/etc/group
sudo mkdir -p mnt/rootfs/home/asm_noobs
sudo cp -r mnt/rootfs/etc/skel/. mnt/rootfs/home/asm_noobs/

HASH=$(openssl passwd -6 'yourpassword')
# Verificar que empiece con $6$
sudo bash -c "echo \"asm_noobs:$HASH:19000:0:99999:7:::\" >> mnt/rootfs/etc/shadow"

# Usar uid/gid numérico para evitar conflicto con usuario del host
sudo chown -R 1000:1000 mnt/rootfs/home/asm_noobs

sync
sudo umount mnt/boot mnt/rootfs
sudo losetup -d $LOOP