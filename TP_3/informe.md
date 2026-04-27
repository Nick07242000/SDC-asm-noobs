# Trabajo Practico N°3

## Modo Protegido

**Materia:** Sistemas de Computacion  
**Grupo:** asm_noobs  
**Integrantes:** [Fabian Nicolas Hidalgo] · [Juan Manuel Caceres] · [Agustin Alvarez]  
**Repositorio:** [Github](https://github.com/Nick07242000/SDC-asm-noobs/blob/main/TP_3)

---

### Desafio: BIOS, UEFI y Coreboot

#### ¿Qué es UEFI? 

UEFI, o Unified Extensible Firmware Interface segun sus siglas, es el sucesor moderno del BIOS. 

Es el "primer software" que se ejecuta cuando se enciende la computadora y actua como el puente principal entre el hardware y el sistema operativo.

A diferencia del BIOS tradicional la UEFI es practicamente un sistema operativo en miniatura con capacidades mucho mas avanzadas. Entre ellas mencionamos:

- Capacidad de disco: soporta particiones de disco mayores a 2.2 TB gracias al estandar GPT.
- Velocidad: permite un inicio del sistema mucho mas rapido.
- Interfaz: soporta el uso del mouse y graficos en alta resolucion.
- Seguridad: incluye Secure Boot que evita que se cargue software malicioso o controladores no firmados durante el arranque.

UEFI ademas expone una API de servicios (Boot Services y Runtime Services) accesibles a través de punteros a funciones en estructuras C estandar.

#### ¿Como se usa?

La UEFI puede utilizarse de forma interactiva para configurar como se comporta el hardware del sistema.

La forma clasica de acceder a ella es presionar una tecla especifica (como F2, F12, Del o Esc) justo después de presionar el boton de encendido.

Una vez dentro podemos realizar diversas configuraciones, como cambiar el orden de arranque para instalar un sistema operativo desde un USB, ajustar las velocidades del procesador o la memoria RAM o revisar la temperatura de la CPU y la velocidad de los ventiladores en tiempo real.

#### Funciones UEFI

Una funcionalidad que puede ser explotada es la de escribir aplicaciones que corran directamente en el entorno UEFI antes de que cargue el sistema operativo. 
Esto se hace a través de servicios de arranque o servicios de tiempo de ejecucion.

Para escribir y ejecutar un programa en UEFI generalmente se utiliza el lenguaje C y un entorno de desarrollo. 
Los programas UEFI se ejecutan de forma independiente antes de que cargue el sistema operativo.

Una funcion basica que podemos llamar es `GetTime` de los Runtime Services para mostrar la fecha y la hora del sistema:
> Returns the current time and date information, and the time-keeping capabilities of the hardware platform.

Para esto se genera un programa en C de la forma:

```C
#include <Uefi.h>
#include <Library/UefiLib.h>

// entrypoint de la app UEFI
EFI_STATUS
EFIAPI
UefiMain (IN EFI_HANDLE ImageHandle, IN EFI_SYSTEM_TABLE *SystemTable)
{
  EFI_TIME Time;

  // llamamos a la funcion desde los runtime services
  SystemTable->RuntimeServices->GetTime(&Time, NULL);

  return EFI_SUCCESS;
}
```

Aqui encontramos los siguientes componentes del programa:
- `UefiMain`: Es el equivalente al `main()` en un programa C normal. Es lo primero que se ejecuta.
- `SystemTable`: Es el parametro mas importante. Es un puntero gigante que la UEFI le pasa al programa. Contiene todas las funciones necesarias para interactuar con el hardware.
- `EFI_TIME Time`: Esta es una estructura predefinida por UEFI que contiene espacios para el año, mes, dia, hora, etc.

El contenido de Time entonces nos queda disponible dentro del programa para realizar lo que precisemos, obtenido directamente del hardware del sistema.

Este programa debe ser compilado con un entorno de desarrollo con la extension `.efi`, y luego este puede ser ejecutado desde un USB o una VM.

#### Bugs de UEFI

Algunos de los bugs mas simples mas comunes que suelen aparecer en UEFI son:

_Buffer Overflows NVRAM_
> Ocurre cuando el codigo de la UEFI extrae configuraciones guardadas sin verificar bien su tamaño lo que permite a un atacante introducir una variable gigante manipulada desde el sistema operativo.  
Al reiniciar la UEFI intenta leerla y desborda el espacio de memoria asignado y termina ejecutando el codigo malicioso adjunto durante las primeras fases del arranque secuestrando el proceso antes de que cargue el sistema.

_SMM Callouts_
> Se produce cuando el modo de gestion del sistema que opera de forma invisible y posee los privilegios mas altos del procesador confia ciegamente en las direcciones de memoria que le envia el sistema operativo regular.  
Esto permite entregarle un puntero falso engañando al SMM para que salga de su entorno seguro y ejecute codigo malicioso alojado en la memoria normal del usuario otorgando control absoluto sobre la maquina.

_FlashSPI Writing_
> Sucede cuando no estan activados los bloqueos a nivel de hardware que protegen el chip fisico de la placa base contra modificaciones no autorizadas.  
Esta permite sobrescribir el firmware original e instalar un rootkit profundo y permanente que sobrevivira a cualquier formateo o cambio fisico del disco duro.

#### Vulnerabilidades de UEFI

Un codigo malicioso alojado en la UEFI es invisible para los antivirus tradicionales y sobrevive a formateos de disco duro o reinstalaciones del sistema operativo. Algunas de las amenazas mas grandes de tiempos recientes son:

_Secure Boot Bypass_
> Varias aplicaciones de recuperacion del sistema incluian un cargador de ejecutables personalizado que tomaba archivos desde una ruta fija en el disco y los ejecutaba sin comprobar sus firmas criptograficas en lugar de usar las funciones estandar de la UEFI.  
Un atacante con privilegios de administrador podira copiar esta aplicacion vulnerable firmada junto con su propio codigo malicioso y Secure Boot permitia la ejecucion de la aplicacion porque estaba firmada por Microsoft, y luego la aplicacion cargaba ciegamente el malware del atacante.  
El atacante podia llevar el binario a cualquier PC y usarlo para ejecutar codigo no firmado en sistemas UEFI.

_Baton Drop Bypass_
> El malware copia en el arranque versiones antiguas vulnerables del gestor de arranque de Windows las cuales aun eran validas para Microsoft pero contenian el fallo. Al reiniciar se ejecuta ese gestor antiguo y la vulnerabilidad permite corromper la memoria para eliminar las politicas de Secure Boot antes de que apliquen.  
Con el Secure Boot neutralizado BlackLotus inyecta su propia clave en la base de datos de la UEFI para asegurarse de que su codigo malicioso sea considerado de confianza en futuros reinicios.  
Una vez activo BlackLotus desactiva protecciones de bajo nivel del sistema operativo. 

_LogoFAIL_
> Durante el arranque de UEFI la placa base carga una imagen para mostrar el logotipo del fabricante. Las librerias que leen esas imagenes no tenian mecanismos de validacion de entrada. Un atacante con privilegios de escritura en la particion EFI puede reemplazar el logotipo por una imagen maliciosamente alterada.  
Cuando la UEFI intenta procesar esa imagen falsa se provoca un buffer overflow. Esto hace que la libreria colapse y termine ejecutando un codigo malicioso escondido dentro de los metadatos de la propia imagen.  
Debido a que el analisis del logo ocurre antes de que se activen las protecciones clave del sistema operativo y del hardware estas medidas quedan completamente inutiles.

#### Converged Security and Management Engine

El CSME es en esencia un "ordenador dentro de tu ordenador". Este funciona incluso si el equipo esta apagado pero enchufado y tiene su propio sistema operativo, memoria y privilegios de acceso.

Es un subsistema autonomo que vive dentro del chipset de las placas base modernas de Intel y se encarga de tareas criticas que la CPU no puede o no debe manejar por si solo. 

Es una combinacion de hardware especializado y firmware que utiliza un microcontrolador basado en una arquitectura separada que ejecuta un sistema operativo en tiempo real llamado `MINIX 3`.

Permite certificar que el firmware de la BIOS/UEFI sea legitimo y no haya sido alterado por malware antes de que el procesador principal empiece a trabajar.

Tambien protege las claves de cifrado y realiza operaciones seguras que el sistema operativo principal no puede ver directamente.

Ademas permite acceder a un ordenador de forma remota incluso si el sistema operativo esta colapsado o la maquina esta apagada.

#### Intel Management Engine BIOS Extension

El Intel MEBx es una interfaz de configuracion a nivel de plataforma que se utiliza para configurar y gestionar la tecnologia `Intel Active Management Technology (AMT)`.

Se encarga especificamente de los ajustes del `Intel Management Engine (ME)` que es un pequeño procesador independiente integrado en los chipsets de Intel que funciona incluso cuando el ordenador esta apagado.

Este permite habilitar o deshabilitar las funciones de gestion remota a nivel de hardware y cambiar la contraseña predeterminado, lo cual es obligatorio antes de poder usar cualquier funcion remota.

Tambien permite asignar una direccion IP dedicada al ME para que los administradores de TI puedan acceder al PC aunque el sistema operativo se haya bloqueado.

Configura el modo "Small Business" o "Enterprise" para determinar como se conecta el dispositivo a una consola de gestion.

#### Coreboot

Es un proyecto de software libre y de codigo abierto que tiene como objetivo reemplazar el firmware propietario como BIOS o UEFI tradicional que viene instalado de fabrica en la mayoria de las computadoras.

Su filosofia se basa en realizar unicamente la inicializacion minima e indispensable del hardware como encender la memoria RAM y el procesador. Una vez que el hardware basico esta funcionando, coreboot pasa el control a un programa secundario llamado "payload" que es el encargado de buscar y arrancar el sistema operativo.

Coreboot es el estandar en ciertos nichos de mercado y empresas enfocadas en Linux, privacidad y codigo abierto. Algunos productos y marcas destacadas incluyen Google Chromebooks, System76, Framework Laptops, Purism, Star Labs y routers y equipos integrados como placas base para firewalls y routers.

El uso de coreboot ofrece beneficios significativos en comparacion con el firmware propietario tradicional. Con este conseguimos un arranque ultrarrapido donde el tiempo desde que se presiona el boton de encendido hasta que carga el sistema operativo se reduce drasticamente.

Tambien obtenemos seguridad auditable al ser de codigo abierto. Cualquier desarrollador o experto en seguridad puede revisar su codigo por lo que es mucho mas dificil esconder backdoors, rootkits o vulnerabilidades. Ademas reduce la superficie de ataque al no incluir millones de lineas de codigo y docenas de aplicaciones integradas que pueden ser hackeadas.

Tambien da mayor control y privacidad al permitir a los usuarios neutralizar o reducir significativamente el alcance de estos sistemas propietarios devolviendo el control del hardware al dueño del equipo.

Finalmente tiene mas vida util del hardware añadiendo soporte para nuevas funciones o parcheando vulnerabilidades mucho después de que el fabricante original lo haya abandonado al ser mantenido por la comunidad.

---

### Desafio: Linker y Hello World Bare-Metal

**¿Qué es un linker y qué hace?**
El linker (enlazador), como `ld` de GNU, es la herramienta que realiza el paso final en la creación de un binario. Su función es combinar múltiples archivos objeto y archivos de archivo (.a), relocalizar sus datos y resolver las referencias a símbolos (como etiquetas de funciones o variables). El linker se guía por un "Linker Script" que describe cómo deben organizarse las secciones de código y datos en el archivo de salida final para que el hardware pueda interpretarlas correctamente.

**¿Qué es la dirección que aparece en el script del linker? ¿Por qué es necesaria?**
En el script, el símbolo `.` representa el "location counter" (contador de ubicación). Al asignarle el valor `0x7c00`, le estamos indicando al linker que la dirección virtual de memoria (VMA) de nuestro código comienza exactamente ahí. 

Esta dirección es crítica debido a una decisión de diseño que data de la IBM PC 5150 (1981). Los desarrolladores de la BIOS eligieron `0x7c00` porque, en máquinas que entonces tenían solo 32KB de RAM, esta dirección permitía cargar el sector de arranque lo suficientemente alto para no sobrescribir la Tabla de Vectores de Interrupción (IVT) en la parte baja, pero dejando espacio suficiente arriba para que el sistema operativo cargara su propio código y manejara su pila (stack) sin colisiones. Si no definimos esto en el linker, las referencias a datos dentro de nuestro ensamblador serían calculadas desde la dirección `0x0`, y el programa fallaría al intentar leer variables una vez cargado en la RAM real.

**Comparación de la salida de objdump con hd.**
La comparación nos permite ver el programa desde dos perspectivas:
* **objdump -S:** Nos muestra la vista lógica, relacionando las instrucciones de ensamblador con sus direcciones de memoria y los opcodes resultantes (por ejemplo, ver que la instrucción `hlt` se traduce al byte `f4`).
* **hd (hexdump):** Nos muestra la vista física del archivo `.img`. Aquí verificamos que los bytes estén en el orden exacto y que la firma de arranque `55 AA` ocupe los bytes 511 y 512 del sector. Al contrastarlos, confirmamos que el linker colocó cada sección en el offset correcto para que la BIOS lo reconozca como un disco booteable.

**¿Para qué se utiliza la opción --oformat binary en el linker?**
Se utiliza para generar un archivo binario "plano" (flat binary). Por defecto, los linkers modernos generan archivos en formato ELF o PE, que contienen encabezados complejos con metadatos para el sistema operativo. En un entorno bare-metal, no hay un sistema operativo para leer esos encabezados; el procesador simplemente empieza a ejecutar bytes uno tras otro. La opción `--oformat binary` elimina toda esa estructura extra y deja únicamente las instrucciones de máquina puras, que es lo único que el CPU puede procesar en modo real.

**Grabar la imagen en un pendrive y probarla en una PC**

Para llevar nuestro código bare-metal a un entorno físico, el primer paso es compilar y enlazar el código fuente. Desde nuestra terminal en Linux, ejecutamos la siguiente secuencia:

* **Ensamblado:** `as -g -o main.o main.S`
    Este comando utiliza el GNU Assembler para traducir nuestro código fuente (`main.S`) a código objeto (`main.o`), incluyendo información de depuración mediante la bandera `-g`.
* **Enlazado:** `ld --oformat binary -o main.img -T link.ld main.o`
    El GNU Linker toma el archivo objeto y, aplicando las reglas matemáticas de nuestro script `link.ld`, ubica el código en la dirección de memoria correcta (`0x7c00`), generando un archivo binario puro (`main.img`).

Una vez obtenida la imagen booteable, procedemos a transferirla al pendrive. Es fundamental desmontar la unidad previamente para evitar conflictos con el sistema operativo:

* **Desmontaje:** `sudo umount /dev/sdb1`
* **Escritura a bajo nivel:** `sudo dd if=main.img of=/dev/sdb status=progress`
    La herramienta `dd` toma nuestra imagen y escribe sus bytes exactos directamente en el primer sector físico del USB (`/dev/sdb`), ignorando cualquier sistema de archivos previo y convirtiendo al dispositivo en un disco de arranque válido (MBR).

![Captura de terminal con los comandos de compilación y flasheo](Screenshot_20260426_225116.png)

Finalmente, procedimos a probar el pendrive booteable. Para sortear las restricciones del firmware UEFI de las notebooks modernas, utilizamos una computadora de escritorio. Las placas madre de escritorio suelen ofrecer módulos CSM (Compatibility Support Module) más robustos, permitiendo emular a la perfección el arranque *Legacy* de 16 bits. 

Al encender el equipo y seleccionar el pendrive en el menú de arranque, el procesador inició en modo real, ejecutó nuestras instrucciones nativamente y logró imprimir la cadena de texto con éxito antes de entrar en un estado de detención controlada (`hlt`).

![Monitor mostrando el texto Hello World! (a medias) ejecutándose en el hardware físico](20260426_231746.jpg)

Se llama protegido porque fue diseñado especificamente para proteger a los programas y al sistema operativo para que no interfieran entre si. 

Antes de que existiera este modo, los procesadores funcionaban en Modo Real donde cualquier programa podia acceder a cualquier parte de la memoria del sistema. Si un programa fallaba o estaba mal escrito, podia sobreescribir la memoria del sistema operativo y hacer que toda la computadora colapsara.

Para iniciar la sesión de depuración en frío, lanzamos el emulador utilizando el siguiente comando:
* `qemu-system-i386 -fda main.img -boot a -s -S -monitor stdio`: Inicia la máquina virtual cargando nuestra imagen, pero congela la ejecución de la CPU antes de la primera instrucción (`-S`) y abre un servidor local (`-s`) a la espera de que nos conectemos.

![QEMU iniciado en estado de pausa](Screenshot_20260427_011843.png)

Desde una terminal secundaria iniciamos GDB y ejecutamos la siguiente secuencia para tomar el control del hardware emulado:
* `target remote localhost:1234`: Establece la conexión directa con la sesión de QEMU.
* `set architecture i8086`: Fuerza al depurador a interpretar la memoria y los registros en modo real de 16 bits, evitando errores de decodificación.
* `break *0x7c00`: Fija un punto de interrupción exactamente en la dirección física donde la BIOS carga el MBR.
* `continue`: Permite que la BIOS ejecute su rutina de inicio normal y nos devuelva el control al llegar a nuestro código.
* `info registers`: Imprime el estado interno del procesador. Aquí confirmamos que el registro `eip` (Instruction Pointer) apuntaba a `0x7c00`.

![Conexión de GDB, breakpoint y estado de los registros](Screenshot_20260427_012327.png)

Para evitar que el depurador ingrese a leer las rutinas internas de la placa madre al momento de imprimir texto, necesitamos identificar nuestras instrucciones físicas en memoria:
* `x/15i $pc`: Examina y traduce a lenguaje ensamblador las próximas 15 instrucciones a partir del Program Counter actual. Esto nos permitió ubicar la interrupción (`int $0x10`) en `0x7c0a`.
* `break *0x7c0c`: Establece un segundo punto de interrupción en la instrucción inmediatamente posterior al llamado de video (`jmp 0x7c05`), creando una barrera de contención.

![Inspección de memoria con decodificación de instrucciones y creación del segundo breakpoint](Screenshot_20260427_012701.png)

Con la zona de interrupción delimitada, controlamos el avance del procesador alternando dos comandos clave:
* `si` (step instruction): Ejecuta el código avanzando estrictamente una instrucción de ensamblador por vez, permitiendo analizar la carga de los registros.
* `c` (continue): Al ubicarnos justo sobre la instrucción `int $0x10`, ejecutamos este comando para que la BIOS tome el control a velocidad normal, dibuje el carácter "H" en pantalla y se detenga inmediatamente al chocar con nuestro segundo breakpoint, listos para la siguiente vuelta del bucle.

![Impresión del primer carácter en QEMU y detención post-interrupción en GDB](Screenshot_20260427_013012.png)

---

### Desafio: Modo Protegido

...

> [UEFI](https://www.lenovo.com/ar/es/glosario/uefi/?orgRef=https%253A%252F%252Fwww.google.com%252F&srsltid=AfmBOoor62-eWIfMZRmqttBQIAzpi4Ajjr5AdGcm7_H7YJSJBs37MAms)

> [UEFI Functions](https://uefi.org/specs/UEFI/2.10/01_Introduction.html)

> [UEFI Bugs](https://www.binarly.io/blog/efixplorer-hunting-uefi-firmware-nvram-vulnerabilities)

> [Vulnerabilidad Secure Boot](https://www.welivesecurity.com/es/investigaciones/uefi-secure-boot-vulnerabilidad-bootkit/)

> [Vulnerabilidad Black Lotus](https://www.binarly.io/blog/the-untold-story-of-the-blacklotus-uefi-bootkit)

> [Vulnerabilidad LogoFAIL](https://tuxcare.com/blog/logofail-vulnerabilities/)

> [Converged Security and Management Engine](https://www.intel.la/content/www/xl/es/download/19392/intel-converged-security-and-management-engine-version-detection-tool-intel-csmevdt.html)

> [Intel Management Engine BIOS Extension](https://dl.dell.com/manuals/all-products/esuprt_laptop/esuprt_latitude_laptop/latitude-e6400_administrator-guide_es-mx.pdf)

> [Coreboot](https://www.coreboot.org/)
