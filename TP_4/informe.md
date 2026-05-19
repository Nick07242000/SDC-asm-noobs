# Trabajo Practico N°4

## Modulos de Kernel

**Materia:** Sistemas de Computacion  
**Grupo:** asm_noobs  
**Integrantes:** [Fabian Nicolas Hidalgo] · [Juan Manuel Caceres] · [Agustin Alvarez]  
**Repositorio:** [Github](https://github.com/Nick07242000/SDC-asm-noobs/blob/main/TP_4)

---

### Desafio #1 

> ¿Qué es checkinstall y para qué sirve?

Es una herramienta para GNU/Linux que permite instalar software compilado desde código fuente y al mismo tiempo generar un paquete instalable del sistema.

Normalmente, cuando se compila un programa manualmente se usa:

```bash
./configure
make
sudo make install
```

El problema es que `make install` copia archivos al sistema sin que el gestor de paquetes los controle. Luego resulta difícil desinstalar o auditar qué se instaló.

Checkinstall reemplaza `sudo make install` por `sudo checkinstall` y automáticamente registra los archivos instalados, crea un paquete instalable, permite desinstalarlo fácilmente, mantiene el sistema más ordenado y seguro.

> Usarlo para empaquetar un hello world

Para esto generamos un programa en c `hello.c`, el cual compilamos con gcc y luego generamos un makefile parausar con checkinstall.

Ejecutamos el mismo con `sudo checkinstall` y generamos el paquete: 

imagen

Luego instalamos el paquete con `dpkg` y lo ejecutamos:

imagen

> Revisar la bibliografía para impulsar acciones que permitan mejorar la seguridad del kernel.
> Concretamente: evitando cargar módulos que no estén firmados.

Un módulo firmado posee una firma criptográfica verificada por el kernel antes de cargarse. Si la firma no es válida el módulo se rechaza y no puede ejecutarse dentro del kernel.

Si el sistema permite cargar cualquier módulo, un atacante con privilegios puede insertar código malicioso directamente en el kernel.

Para evitar estos modulos no firmados podemos realizar diversas acciones:

1. Activar “Module Signature Verification”: Esto obliga al kernel a aceptar únicamente módulos firmados.
2. Usar Secure Boot: permite que el firmware valide el bootloader, el bootloader valide el kernel y el kernel valide módulos.
3. Deshabilitar carga dinámica de módulos: no se pueden cargar más módulos, incluso siendo root.
4. Restringir herramientas peligrosas: como `insmod`, `modprobe` y `rmmod` solo a administradores confiables.

> ¿ Que son rootkits? 

Un rootkit es software malicioso diseñado para ocultarse, obtener privilegios elevados y modificar el comportamiento del sistema.

Los rootkits de kernel son especialmente peligrosos porque operan con privilegios máximos.

Entre las cosas que pueden realizar encontramos que pueden interceptar syscalls, ocultar procesos, ocultar archivos, ocultar conexiones de red y alterar logs.

### Desafio #2

> ¿Qué funciones tiene disponible un programa y un módulo?

Un programa en espacio de usuario utiliza funciones de bibliotecas (libc, pthread, etc), realiza llamadas al sistema (read, write, fork, socket), posee memoria virtual aislada y tienepermisos restringidos.

Este no tiene acceso directo al hardware.

Por otro lado un módulo del kernel puede acceder directamente al hardware, manipular memoria del kernel, registrar drivers, interceptar llamadas y manejar interrupciones.

Este tiene privilegios totales.

> Espacio de usuario o espacio del kernel.

El espacio de usuario es donde se ejecutan aplicaciones, shells, navegadores y programas comunes.

Se caracteriza por su acceso restringido, aislamiento entre procesos y produce errores menos críticos.

Son las aplicaciones que conocemos como Firefox, Bash, VSCode, etc

El espacio del kernel es donde se ejecuta el kernel y sus módulos.

Se caracteriza por su acceso completo al hardware, posee máxima prioridad, y si produce un error puede colgar todo el sistema.

Por ejemplo el scheduler, los drivers, el sistema de memoria y el filesystem.

> Espacio de datos.

El espacio de datos de un proceso contiene sus variables globales, sus variables estáticas, su heap y su stack.

Se divide típicamente en Text (que es el código ejecutable), Data (las variables inicializadas), BSS (las variables no inicializadas), Heap	(la memoria dinámica) y el Stack (las variables locales y las llamadas).

> Drivers. Investigar contenido de /dev.

Un driver es software que permite al sistema operativo comunicarse con hardware.

Tenemos drivers para el teclado, el disco, la placa de red, la GPU y los puertos USB.

En Linux muchos drivers son módulos del kernel (.ko).

Con respecto a `/dev` Linux lo utiliza para representar dispositivos como archivos.

La idea central de Unix es que todo es un archivo.

Asi por ejemplo tenemos:

| Archivo        | Función                  |
| -------------- | ------------------------ |
| `/dev/sda`     | disco duro               |
| `/dev/tty`     | terminal                 |
| `/dev/null`    | descarta datos           |
| `/dev/zero`    | genera ceros             |
| `/dev/random`  | números aleatorios       |
| `/dev/urandom` | números pseudoaleatorios |
| `/dev/input/*` | dispositivos de entrada  |
| `/dev/snd/*`   | audio                    |

### Modulos

que hace esto?

```bash
cd part1
make
sudo insmod mimodulo.ko
sudo dmesg
lsmod | grep mod
```

describir resultado y poner imagen de ejecucion

que hace esto?

```bash
sudo rmmod mimodulo
sudo dmsg
lsmod | grep mod
cat /proc/modules  | grep mod
```

describir resultado y poner imagen de ejecucion

que hace esto?

```bash
modinfo mimodulo.ko 
modinfo /lib/modules/$(uname -r)/kernel/crypto/des_generic.ko
```

describir resultado y poner imagen de ejecucion

> ¿Qué diferencias se pueden observar entre los dos modinfo ? 

...

> ¿Qué divers/modulos estan cargados en sus propias pc?  
> Comparar las salidas con las computadoras de cada integrante del grupo.  
> Expliquen las diferencias.  
> Carguen un txt con la salida de cada integrante en el repo y pongan un diff en el informe.

...

> ¿Cuales no están cargados pero están disponibles?  
> Que pasa cuando el driver de un dispositivo no está disponible. 

...

> Correr hwinfo en una pc real con hw real y agregar la url de la información de hw en el reporte. 

...

> ¿Qué diferencia existe entre un módulo y un programa?

...

> ¿Cómo puede ver una lista de las llamadas al sistema que realiza un simple helloworld en c?

...

> ¿Qué es un segmentation fault?
> ¿Cómo lo maneja el kernel y como lo hace un programa?

...

> Intentar firmar un módulo de kernel y documentar el proceso?

...

> Agregar evidencia de la compilación, carga y descarga de su propio módulo imprimiendo el nombre del equipo en los registros del kernel. 

...

> ¿Que pasa si mi compañero con secure boot habilitado intenta cargar un módulo firmado por mi? 

...

> Dada la siguiente [nota](https://arstechnica.com/security/2024/08/a-patch-microsoft-spent-2-years-preparing-is-making-a-mess-for-some-linux-users/)  
> ¿Cuál fue la consecuencia principal del parche de Microsoft sobre GRUB en sistemas con arranque dual (Linux y Windows)?

...

> Dada la siguiente [nota](https://arstechnica.com/security/2024/08/a-patch-microsoft-spent-2-years-preparing-is-making-a-mess-for-some-linux-users/)  
> ¿Qué implicancia tiene desactivar Secure Boot como solución al problema descrito en el artículo?

...

> Dada la siguiente [nota](https://arstechnica.com/security/2024/08/a-patch-microsoft-spent-2-years-preparing-is-making-a-mess-for-some-linux-users/)  
> ¿Cuál es el propósito principal del Secure Boot en el proceso de arranque de un sistema?

...

### Referencias

> [Kernel Redhat](https://access.redhat.com/documentation/es-es/red_hat_enterprise_linux/8/html/managing_monitoring_and_updating_the_kernel/signing-kernel-modules-for-secure-boot_managing-kernel-modules)

> [Kernel Module](https://sysprog21.github.io/lkmpg/#what-is-a-kernel-module)

> [Strace](https://opensource.com/article/19/10/strace)

> [???](https://docs.google.com/presentation/d/1BYES6Zkfx5K85REWyXsFeW-VngBLOzlDzaYCsTVoc0Y/edit#slide=id.g724a4c87a0_0_5 )

> [Sign Kernel](https://askubuntu.com/questions/770205/how-to-sign-kernel-modules-with-sign-file)

> [Dual Boot Issue](https://arstechnica.com/security/2024/08/a-patch-microsoft-spent-2-years-preparing-is-making-a-mess-for-some-linux-users/)
