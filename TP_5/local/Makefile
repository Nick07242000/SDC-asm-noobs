obj-m += asmn_driver.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	make -C $(KDIR) M=$(PWD) modules

run: all
	sudo rmmod asmn_driver 2>/dev/null || true
	sudo insmod asmn_driver.ko
	python3 app.py
	
clean:
	sudo rmmod asmn_driver 2>/dev/null || true
	make -C $(KDIR) M=$(PWD) clean