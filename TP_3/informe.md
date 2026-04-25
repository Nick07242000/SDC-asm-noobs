# Trabajo Practico N°3

## Calculadora de Indices

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

...

---

### Desafio: Modo Protegido

...

---

### Depuracion con GDB + QEMU

...

---

### Referencias

> ...
