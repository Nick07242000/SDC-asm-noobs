#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/random.h>
#include <linux/timer.h>
#include <linux/uaccess.h>
#include <linux/device.h>

#define DEVICE_NAME "asmn_driver"

static dev_t dev_num;
static struct cdev asmn_cdev;
static struct class *asmn_class;

static struct timer_list asmn_timer;

static int selected_channel = 0;
static int signal_0 = 0;
static int signal_1 = 0;

static int counter = 0;

static void generate_signals(void)
{
    signal_0 = (counter % 20) * 5;
    signal_1 = get_random_u32() % 100;
    counter++;
}

static void timer_callback(struct timer_list *t)
{
    generate_signals();
    printk(KERN_INFO "Signal0=%d Signal1=%d\n", signal_0, signal_1);
    mod_timer(&asmn_timer, jiffies + msecs_to_jiffies(1000));
}

static char *asmn_devnode(const struct device *dev, umode_t *mode)
{
    if (mode) *mode = 0666;
    return NULL;
}

static int asmn_open(struct inode *inode, struct file *file)
{
    printk(KERN_INFO "ASMN Driver opened\n");
    return 0;
}

static int asmn_release(struct inode *inode, struct file *file)
{
    printk(KERN_INFO "ASMN Driver closed\n");
    return 0;
}

static ssize_t asmn_read(struct file *file, char __user *buf, size_t len, loff_t *off)
{
    char message[64];

    int value;
    int bytes;

    if (*off > 0) return 0;

    if (selected_channel == 0) value = signal_0;
    else value = signal_1;

    bytes = sprintf(message, "%d: %d\n", counter, value);

    if (copy_to_user(buf, message, bytes)) return -EFAULT;

    *off += bytes;

    return bytes;
}

static ssize_t asmn_write(struct file *file, const char __user *buf, size_t len, loff_t *off)
{
    char kbuf[8];

    if (copy_from_user(kbuf, buf, len))return -EFAULT;

    kbuf[len] = '\0';

    if (kbuf[0] == '0') selected_channel = 0;
    else if (kbuf[0] == '1')selected_channel = 1;

    printk(KERN_INFO "Selected channel: %d\n", selected_channel);

    return len;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = asmn_open,
    .release = asmn_release,
    .read = asmn_read,
    .write = asmn_write,
};

static int __init asmn_init(void)
{
    alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);

    cdev_init(&asmn_cdev, &fops);
    cdev_add(&asmn_cdev, dev_num, 1);

    asmn_class = class_create("asmn_class");
    asmn_class->devnode = asmn_devnode;
    device_create(asmn_class, NULL, dev_num, NULL, DEVICE_NAME);

    timer_setup(&asmn_timer, timer_callback, 0);
    mod_timer(&asmn_timer, jiffies + msecs_to_jiffies(1000));

    printk(KERN_INFO "ASMN Driver registered. Major=%d\n", MAJOR(dev_num));

    return 0;
}

static void __exit asmn_exit(void)
{
    del_timer(&asmn_timer);

    device_destroy(asmn_class, dev_num);

    class_destroy(asmn_class);

    cdev_del(&asmn_cdev);

    unregister_chrdev_region(dev_num, 1);

    printk(KERN_INFO "ASMN Driver unloaded\n");
}

module_init(asmn_init);
module_exit(asmn_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("asm_noobs");
MODULE_DESCRIPTION("TP5 Character Device Driver");
