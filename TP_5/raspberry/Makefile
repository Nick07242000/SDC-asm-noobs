ARCH          := arm64
CROSS_COMPILE := aarch64-linux-gnu-
KDIR          := /usr/src/linux-headers-6.12.25+rpt-rpi-v8

obj-m += asmn_driver.o

all:
	make -C $(KDIR) M=$(PWD) \
	  ARCH=$(ARCH) \
	  CROSS_COMPILE=$(CROSS_COMPILE) \
	  modules

clean:
	make -C $(KDIR) M=$(PWD) \
	  ARCH=$(ARCH) \
	  CROSS_COMPILE=$(CROSS_COMPILE) \
	  clean