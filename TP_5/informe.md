# Trabajo Practico N°5

## Character Device Driver

**Materia:** Sistemas de Computacion  
**Grupo:** asm_noobs  
**Integrantes:** [Fabian Nicolas Hidalgo] · [Juan Manuel Caceres] · [Agustin Alvarez]  
**Repositorio:** [Github](https://github.com/Nick07242000/SDC-asm-noobs/blob/main/TP_5)

---

### Introduccion

En este trabajo practico se desarrolla un Character Device Driver (CDD) para Linux capaz de sensar dos señales externas.

Este las muestrea cada un segundo, y permite que una aplicacion de usuario seleccione cual señal leer.

Finalmente grafica la señal seleccionada en funcion del tiempo.

---

### Objetivos

Se va a diseñar e implementar un Character Device Driver capaz de adquirir dos señales y exponerlas a una aplicacion de usuario.

El objetivo principal es comprender la arquitectura de drivers Linux, la comunicacion entre User Space y el Kernel Space, el uso de CDDs, el manejo de `/dev`, el uso de timers en kernel y el intercambio de datos mediante `read()` y `write()`.

---

### Descripcion del Sistema

El sistema desarrollado se divide en dos partes:

#### Kernel Space

Implementado mediante un Character Device Driver, que tiene como responsabilidad:

- Generar dos señales.
- Actualizarlas cada segundo.
- Administrar el canal seleccionado.
- Entregar datos a user-space.

#### User Space

Aplicacion Python encargada de:

- Leer datos desde `/dev/asmn_driver`
- Graficar la señal.
- Permitir cambio de canal.
- Resetear el grafico.

```mermaid
flowchart LR
    App["Aplicacion Python"] -- "read/write" --> Dev["/dev/asmn_driver"]
    Dev --> Driver["Character Driver"]
    Driver --> S0("Señal 0")
    Driver --> S1("Señal 1")
```

---

### Desarrollo del Driver

#### Modulo Basico

El primer paso fue crear un modulo basico del kernel.

En Linux, todo modulo posee dos funciones principales, una de inicializacion, y una de finalizacion.

La de inicializacion se ejecuta cuando el modulo es cargado con `insmod`, mientras que la de finalizacion se ejecuta cuando el modulo es removido utilizando `rmmod`.

Las macros `module_init` y `module_exit` permiten registrar estas funciones dentro del kernel.

```c
#include <linux/module.h>
#include <linux/kernel.h>

static int __init asmn_init(void)
{
    printk(KERN_INFO "ASMN Driver loaded\n");
    return 0;
}

static void __exit asmn_exit(void)
{
    printk(KERN_INFO "ASMN Driver unloaded\n");
}

module_init(asmn_init);
module_exit(asmn_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("asm_noobs");
MODULE_DESCRIPTION("TP5 Character Device Driver");
```

Inicialmente el modulo solamente imprimía mensajes utilizando `printk()` para verificar correctamente la carga del modulo, la descarga y la visualizacion de mensajes en `dmesg`.

Para validar cada etapa del modulo se genero un makefile y un script para permitirnos visualizar la carga, descarga y ejecucion del modulo.

<img width="524" height="620" alt="Screenshot from 2026-05-28 22-48-19" src="https://github.com/user-attachments/assets/bf96331f-d3e7-48a5-a31b-64c2abd1efc1" />

Este módulo solo es código cargado en kernel-space que no existe /dev, nadie puede usarlo y no hay archivo.

#### Character Device Driver

Una vez validado el modulo basico el siguiente paso fue convertirlo en un Character Device Driver. El CDD es la interfaz que Linux usa para hablar con el módulo.

Para que Linux pueda asociar un archivo dentro de `/dev` con nuestro driver fue necesario registrar un numero major,minor.

El numero major identifica al driver dentro del kernel mientras que el minor identifica una instancia específica del dispositivo.

Para esto se utilizó `alloc_chrdev_region()` porque permite que el kernel asigne automáticamente un major libre evitando conflictos con otros dispositivos del sistema.

Aqui le estamos diciendo al kernel que este módulo sabe manejar un dispositivo de caracteres.

Al codigo incorporamos la estructura `struct cdev` la cual representa internamente el dispositivo de caracteres dentro del kernel.

Por medio de `cdev_init()` y `cdev_add()` asociamos las operaciones del driver con el dispositivo recién registrado.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/cdev.h>
#include <linux/cdev.h>

#define DEVICE_NAME "asmn_driver"

static dev_t dev_num;
static struct cdev asmn_cdev;

static int __init asmn_init(void)
{
    alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);

    cdev_init(&asmn_cdev, NULL);
    cdev_add(&asmn_cdev, dev_num, 1);

    printk(KERN_INFO "ASMN Driver registered. Major=%d\n", MAJOR(dev_num));

    return 0;
}

static void __exit asmn_exit(void)
{
    cdev_del(&asmn_cdev);

    unregister_chrdev_region(dev_num, 1);

    printk(KERN_INFO "ASMN Driver unloaded\n");
}

module_init(asmn_init);
module_exit(asmn_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("asm_noobs");
MODULE_DESCRIPTION("TP5 Character Device Driver");
```

Hasta este punto el módulo existía dentro del kernel pero Linux todavía no sabía cómo interactuar con él como dispositivo.

<img width="496" height="345" alt="Screenshot from 2026-05-28 22-50-59" src="https://github.com/user-attachments/assets/9f23a879-afee-49a6-85b4-208c10fa047a" />

Inicialmente generamos el archivo asociado dentro de dev de forma manual dentro del script:

```bash
sudo mknod ${DEVICE_NAME} c ${MAJOR} 0
sudo chmod 666 ${DEVICE_NAME}
```

#### File Operations

Una vez registrado el dispositivo se definio qué acciones realizaría el driver cuando un programa de usuario intentara interactuar con él.

En Linux todas las operaciones de un Character Device se describen mediante la estructura `struct file_operations` que funciona como una tabla de funciones que el kernel invoca automáticamente cuando ocurre alguna operación sobre el archivo del dispositivo.

Implementamos las operaciones minimas necesarias `open`, `release`, `read` y `write` para la comunicación user-space y kernel-space.

La estructura quedó definida como:

```C
static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = asmn_open,
    .release = asmn_release,
    .read = asmn_read,
    .write = asmn_write,
};
```

A partir de aquí cualquier programa que accediera a `/dev/asmn_driver` ejecutaría automáticamente las funciones correspondientes del módulo.

Por ejemplo `cat /dev/asmn_driver` genera internamente `open()`, `read()` y `release()`.

<img width="497" height="770" alt="Screenshot from 2026-05-28 22-53-00" src="https://github.com/user-attachments/assets/cfe6073e-2018-4205-9194-e6c4f21babd5" />

#### Generacion de Señales

Una vez establecida la comunicación básica el siguiente objetivo fue incorporar las señales requeridas por el TP.

En lugar de utilizar hardware real desde el comienzo se decidió generar señales simuladas dentro del kernel.

Se implementaron dos señales para disponer de dos fuentes de datos diferentes sobre las cuales trabajar.
- Señal 0 : Una señal periódica creciente simulando una onda.
- Señal 1 : Una señal aleatoria utilizando `prandom_u32()`.

```C
static int signal_0 = 0;
static int signal_1 = 0;

static int counter = 0;

static void generate_signals(void)
{
    signal_0 = (counter % 20) * 5;
    signal_1 = get_random_u32() % 100;
    counter++;
}
```

Asi podemos ver el valor generado por la señal simulada:

<img width="493" height="124" alt="Screenshot from 2026-05-29 00-22-37" src="https://github.com/user-attachments/assets/0f011820-54cc-447e-afbd-12357c59f33d" />

Para que las señales fueran muestreadas cada 1 segundo se implementó un timer del kernel utilizando `struct timer_list`.

El timer fue configurado para ejecutar periódicamente la generacion de las señales.

Posteriormente el timer se rearmaba utilizando `mod_timer()`.

```C
static void timer_callback(struct timer_list *t)
{
    generate_signals();
    printk(KERN_INFO "Signal0=%d Signal1=%d\n", signal_0, signal_1);
    mod_timer(&asmn_timer, jiffies + msecs_to_jiffies(1000));
}

static int __init asmn_init(void)
{
    alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);

    cdev_init(&asmn_cdev, &fops);
    cdev_add(&asmn_cdev, dev_num, 1);

    timer_setup(&asmn_timer, timer_callback, 0);
    mod_timer(&asmn_timer, jiffies + msecs_to_jiffies(1000));

    printk(KERN_INFO "ASMN Driver registered. Major=%d\n", MAJOR(dev_num));

    return 0;
}
```

Esto permitió que el driver funcionara de manera autónoma generando nuevas muestras periódicamente sin intervención de la aplicación de usuario.

<img width="499" height="574" alt="Screenshot from 2026-05-29 00-34-47" src="https://github.com/user-attachments/assets/9d95b3ae-0ddd-4f2c-9d27-e1a83775c50a" />

#### Lectura de Señales

Una vez que el driver ya generaba señales periódicamente el siguiente paso fue permitir que un programa de usuario pudiera leerlas.

Para esto se completo la funcion `asmn_read()` para identificar qué canal estaba seleccionado, obtener el valor correspondiente, formatearlo como texto y copiarlo a user-space.

```C
static ssize_t asmn_read(struct file *file, char __user *buf, size_t len, loff_t *off)
{
    char message[64];

    int value;
    int bytes;

    if (*off > 0) return 0;

    if (selected_channel == 0) value = signal_0;
    else value = signal_1;

    bytes = sprintf(message, "%d,%d\n", counter, value);

    if (copy_to_user(buf, message, bytes)) return -EFAULT;

    *off += bytes;

    return bytes;
}
```

Vemos ahora como haciendo `cat /dev/asmn_driver` en el paso doce de validacion podemos leer los valores sensados:

<img width="503" height="140" alt="Screenshot from 2026-05-29 19-49-54" src="https://github.com/user-attachments/assets/0875076d-7d30-4756-912c-4dc5211a6670" />

La copia de memoria se realizó utilizando `copy_to_user()` porque el kernel no puede acceder directamente a memoria de usuario de manera segura.

Durante esta etapa apareció un problema importante donde `cat` realizaba múltiples lecturas sucesivas porque el kernel esperaba recibir un EOF.

La solución consistió en utilizar `if (*off > 0) return 0;` para indicar correctamente el final de archivo luego de una lectura completa.

#### Seleccion de Canal

Para permitir que la aplicación seleccionara cuál señal leer se completo la implementacion de `asmn_write()`.

La idea fue utilizar el archivo `/dev/asmn_driver` también como mecanismo de configuración.

Se utilizo `copy_from_user()` para copiar el dato enviado desde user-space hacia memoria del kernel, y en baseo a eso actualizamos `selected_channel`. 

```C
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
```

Aqui logramos una comunicación bidireccional entre user-space y kernel.

Ahora con `echo 0 | sudo tee /dev/asmn_driver` podemos seleccionar el canal cero y con `echo 1 | sudo tee /dev/asmn_driver` podemos seleccionar el canal uno.

<img width="503" height="349" alt="Screenshot from 2026-05-29 21-30-54" src="https://github.com/user-attachments/assets/51f9f2cb-f86b-4f5e-88be-a9a6d9763c2e" />

#### Generacion Automatica de /dev

Hasta ahora el dispositivo existía dentro del kernel, pero todavía no aparecía automáticamente dentro de /dev, esto lo realizabamos de forma manual en el script:

```bash
echo "============================================================"
echo " STEP 5.1 - Creating device node manually"
echo "============================================================"

MAJOR=$(cat /proc/devices | grep ${MODULE_NAME} | awk '{print $1}')

if [ -z "${MAJOR}" ]; then
    echo "[ERROR] Could not find major number"
    exit 1
fi

if [ ! -e ${DEVICE_NAME} ]; then
    sudo mknod ${DEVICE_NAME} c ${MAJOR} 0
    sudo chmod 666 ${DEVICE_NAME}
    echo
    echo "[OK] Device node created"
else
    echo
    echo "[OK] Device node already exists"
fi
```

Para automatizar esto se utilizo `class_create()` y `device_create()` que registran el dispositivo dentro de `sysfs` permitiendo que `udev` cree automáticamente `/dev/asmn_driver`.

```C
static int __init asmn_init(void)
{
    alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);

    cdev_init(&asmn_cdev, &fops);
    cdev_add(&asmn_cdev, dev_num, 1);

    asmn_class = class_create("asmn_class");
    device_create(asmn_class, NULL, dev_num, NULL, DEVICE_NAME);

    timer_setup(&asmn_timer, timer_callback, 0);
    mod_timer(&asmn_timer, jiffies + msecs_to_jiffies(1000));

    printk(KERN_INFO "ASMN Driver registered. Major=%d\n", MAJOR(dev_num));

    return 0;
}
```

Esto tiene una correspondencia para destruir el dispositivo al quitar el modulo:

```C
static void __exit asmn_exit(void)
{
    del_timer(&asmn_timer);

    device_destroy(asmn_class, dev_num);

    class_destroy(asmn_class);

    cdev_del(&asmn_cdev);

    unregister_chrdev_region(dev_num, 1);

    printk(KERN_INFO "ASMN Driver unloaded\n");
}
```

Ante una primera ejecucion nos encontramos con falta de permisos:

<img width="498" height="690" alt="Screenshot from 2026-05-29 21-49-05" src="https://github.com/user-attachments/assets/47723e1f-1d15-40a3-a167-5f45bb29e6e8" />
<img width="496" height="77" alt="Screenshot from 2026-05-29 21-49-40" src="https://github.com/user-attachments/assets/6b6fdce3-35d6-485b-ba31-916ffb9d859d" />

Esto es porque eliminamos `sudo chmod 666 ${DEVICE_NAME}` del script que otorgaba los permisos de lectura y escritura.

Para resolver esto desde codigo definimos un callback para cargar en `devnode` de la clase creada, que otorgue estos permisos:

```C
static char *asmn_devnode(const struct device *dev, umode_t *mode)
{
    if (mode) *mode = 0666;
    return NULL;
}

static int __init asmn_init(void)
{
    ...
    asmn_class = class_create("asmn_class");
    asmn_class->devnode = asmn_devnode;
    ...
}
```

Con este ajuste al ejecutar podemos ver como se genera automaticamente el archivo dentro de `dev` y se ejecutan todas las funcionalidades:

<img width="491" height="803" alt="Screenshot from 2026-05-29 21-49-55" src="https://github.com/user-attachments/assets/9b1b32f1-1324-4a0b-816d-005f62deff27" />

Asi se integraron todas las partes desarrolladas, el módulo del kernel, el registro del device, las operaciones del dispositivo, el timer, la generación de señales, la lectura y escritura, y la creación automática de `/dev`.

El resultado final fue un Character Device Driver completamente funcional capaz de generar dos señales, muestrearlas periódicamente, permitir selección dinámica de canal y entregar datos a aplicaciones de usuario mediante `/dev/asmn_driver`.

---

## Aplicación y Visualización

Se desarrolló una aplicación en Python para interactuar con el dispositivo `/dev/asmn_driver` y visualizar en tiempo real las señales generadas por el Character Device Driver.

Para la interfaz gráfica se utilizó la biblioteca `Matplotlib`, la cual permite seleccionar una de las dos señales disponibles mediante botones y representar su evolución en función del tiempo.

Cuando el usuario presiona uno de los botones, se invoca a la función `set_channel()`, que escribe el valor correspondiente (0 o 1) en el archivo `/dev/asmn_driver`.Esto provoca que el driver cambie el canal de medición seleccionado y reinicia los datos almacenados para comenzar una nueva visualización.

La lectura de datos se realiza abriendo periódicamente el dispositivo con `read_device()` y obteniendo una cadena con el formato `contador:valor`, donde el contador representa el tiempo transcurrido y el valor corresponde a la medición de la señal seleccionada.

Mediante la función `FuncAnimation`, la aplicación consulta el driver cada 500 ms y actualiza automáticamente el gráfico, sin repetir muestras.

### Ejecución de app.py

Para la ejecucion de `app.py` utilizamos `make run`.
Al ejecutar este comando se realizan automáticamente las siguientes acciones:

- Se compila el módulo del kernel.
- Se elimina una versión previa del módulo (si estaba cargada).
- Se carga el módulo mediante `insmod`.
- Se ejecuta la aplicación Python.
- La aplicación comienza a comunicarse con el dispositivo /dev/asmn_driver y muestra las señales en tiempo real.

> [!NOTE]

Debido a que la aplicación utiliza la biblioteca `Matplotlib`, es necesario instalarla previamente:
```bash
sudo apt install python3-matplotlib
```
