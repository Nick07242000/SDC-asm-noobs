# Trabajo práctico 1. El rendimiento de las computadoras.

## 1. Relación entre tiempo y frecuencia.

Realizamos un código en lenguaje C que se ejecutará en una placa de desarrollo ESP-Wroom-32 con el objetivo de poder medir el tiempo de ejecución del programa, y así poder correr varias pruebas variando la frecuencia del microprocesador entre ellas, para realizar una tabla y comparar los resultados de como varían los tiempos totales respecto de los cambios en la frecuencia.
Como referencia, tomaremos una ejecución base configurada para durar alrededor de 10[s] (calibrada modificando la cantidad de operaciones en el bucle interno, y a una frecuencia inicial de 80[MHz], para poder ir incrementando en las iteraciones posteriores)

El código es el siguiente:

```cpp
#include <Arduino.h>

const uint32_t DEFAULT_ITERATIONS = 70460000;
const uint32_t CPU_FREQ_MHZ[] = {80, 160, 240};
const size_t CPU_FREQ_COUNT = sizeof(CPU_FREQ_MHZ) / sizeof(CPU_FREQ_MHZ[0]);
volatile uint32_t counter = 0;
volatile uint32_t requested_freq_mhz = CPU_FREQ_MHZ[0];
volatile uint32_t requested_iterations = DEFAULT_ITERATIONS;
volatile unsigned long long start_time_us = 0;
volatile unsigned long long end_time_us = 0;
volatile unsigned long long total_time_us = 0;

static void runBenchmark(uint32_t freqMHz, uint32_t iterations) {
    requested_freq_mhz = freqMHz;
    requested_iterations = iterations;
    setCpuFrequencyMhz(freqMHz);
    counter = 0;
    start_time_us = micros();
    for (uint32_t i = 0; i < iterations; i++) {
        counter++;
    }
    end_time_us = micros();
    total_time_us = end_time_us - start_time_us;
}

static void printStats() {
    setCpuFrequencyMhz(240);
    Serial.printf("CPU Frequency: %lu MHz\n", (unsigned long)requested_freq_mhz);
    Serial.printf("Total Time: %llu [us] (%.3f [ms])\n", total_time_us, (double)total_time_us / 1000.0);
    Serial.printf("Final Counter: %lu\n", (unsigned long)counter);
}

static void runAllBenchmarks() {
    setCpuFrequencyMhz(240);
    Serial.printf("Running %lu iterations for each supported frequency...\n", (unsigned long)DEFAULT_ITERATIONS);
    for (size_t i = 0; i < CPU_FREQ_COUNT; i++) {
        runBenchmark(CPU_FREQ_MHZ[i], DEFAULT_ITERATIONS);
        printStats();
    }
}

void setup() {
    setCpuFrequencyMhz(240);
    Serial.begin(115200);
    delay(1000);
    Serial.println("ESP32 automatic time benchmark");
    runAllBenchmarks();
}

void loop() {
    delay(1000);
}
```

Luego de ejecutar el siguiente código se obtiene la siguiente salida por consola:

```text
ESP32 automatic time benchmark
Running 70460000 iterations for each supported frequency...
CPU Frequency: 80 MHz
Total Time: 10004252 [us] (10004.252 [ms])
Final Counter: 70460000
CPU Frequency: 160 MHz
Total Time: 4921996 [us] (4921.996 [ms])
Final Counter: 70460000
CPU Frequency: 240 MHz
Total Time: 3264312 [us] (3264.312 [ms])
Final Counter: 70460000
```

Como una breve conclusión podemos decir entonces que tomando como referencia la ejecución a 80 [MHz] ($T_{80}=10.004252\ s$), los *speedups* medidos son:

$$
S_{160} = \frac{T_{80}}{T_{160}} = \frac{10.004252}{4.921996} \approx 2.03
$$

$$
S_{240} = \frac{T_{80}}{T_{240}} = \frac{10.004252}{3.264312} \approx 3.06
$$

Estos valores son muy cercanos al escalado ideal por frecuencia (2x y 3x), lo que indica que en este benchmark casi todo el trabajo se acelera al aumentar la frecuencia. Relacionándolo con la Ley de Amdahl:

$$
S(k)=\frac{1}{\alpha + \frac{1-\alpha}{k}}
$$

Donde $\alpha$ es la fracción no acelerable y $k$ el factor de mejora (en este caso, el factor de frecuencia). Los resultados sugieren $\alpha \approx 0$ dentro del error experimental, por eso el speedup observado queda prácticamente limitado por el valor ideal $k$ y no por una parte serial significativa.

## 2. Benchmarks

### 2.1. Propuestas de posibles benchmarks para tareas propias

Realizamos una tabla donde colocamos algunas de las tareas que realizamos con nuestra computadora y propusimos cuales pueden ser los benchmarks que se podrían utilizar para medir rendimiento basandose en las tareas listadas.

| Tarea | Benchmark propuesto |
| --- | --- |
| Juegos multijugador online | Prueba de red con `ping` y `tracert` a servidores de juego + captura de FPS/frametime (latencia promedio [ms], jitter [ms], pérdida de paquetes [%], FPS promedio y 1% low FPS). |
| Diseño 3D en Ultimaker Cura | Benchmark de slicing con modelos de distinta complejidad (tiempo de slicing [s], uso máximo de CPU [%], uso de RAM [GB]). |
| Diseño CAD en Fusion 360 | Prueba de abrir/editar/generar ensamblajes y exportar STL/STEP (tiempo de apertura [s], tiempo de regeneración [s], tiempo de exportación [s], uso de GPU [%]). |
| Programación de ESP32/Arduino | Compilación y carga repetida del mismo firmware con Arduino IDE/PlatformIO (tiempo de compilación [s], tiempo de carga [s], tamaño binario [KB], tiempo de ejecución del benchmark en placa [ms]). |
| Programación (Java, C/C++, Python) | Benchmark general de flujo de desarrollo: compilación/ejecución de proyecto representativo + ejecución de tests + profiling básico (tiempo de build limpio e incremental [s], tiempo de ejecución [ms], tests/s, uso de CPU/RAM, throughput [ops/s]). |
| Streaming de videos | Reproducción de video 1080p/4K y monitoreo de buffering (frames perdidos, tasa de buffering, bitrate sostenido [Mbps], uso de CPU/GPU [%]). |
| Control de impresora 3D y router CNC (firmware Marlin/Klipper) | Envío de G-code y ejecución de trayectorias estándar en ambos equipos, en vacío y bajo carga (frecuencia de pasos estable, latencia de comando [ms], pérdida de pasos, calidad/trayectoria final [mm], tiempo total de trabajo [min]). |

### 2.2. Rendimiento de CPUs en compilación de kernel

Analizando el comportamiento de los tres procesadores considerados (Intel Core i5-13600K, AMD Ryzen 9 5900X 12-Core y AMD Ryzen 9 7950X 16-Core), los tiempos de compilación del kernel son 846[s], 901[s] y 512[s], respectivamente. Si expresamos estos resultados como rendimiento (compilaciones por segundo), obtenemos:

- i5-13600K: $1/846 = 0.00118$ [compilaciones/s]
- Ryzen 9 5900X: $1/901 = 0.00111$ [compilaciones/s]
- Ryzen 9 7950X: $1/512 = 0.00195$ [compilaciones/s]

Con estos valores se observa que el i5-13600K rinde aproximadamente un 6.5% mejor que el Ryzen 9 5900X en este benchmark, pero el Ryzen 9 7950X supera al i5-13600K con una ventaja cercana al 65% (o, en términos de tiempo, completa la tarea en ~39.5% menos tiempo).

Podemos resumirlo en la siguiente tabla de *speedup* tomando al i5-13600K como referencia:

| CPU | Speedup |
| --- | --- |
| i5-13600K | 846/846 = 1.00 |
| Ryzen 9 5900X | 846/901 = 0.94 |
| Ryzen 9 7950X | 846/512 = 1.65 |

La compilación del kernel es un caso parcialmente paralelizable: gran parte del trabajo puede distribuirse entre varios núcleos, pero siguen existiendo etapas secuenciales, como el *linking* final y algunas dependencias entre archivos. Por eso, el tiempo total depende tanto del rendimiento multi-core como del desempeño por núcleo.

En este escenario, el i5-13600K se beneficia de un buen rendimiento por núcleo y logra un mejor tiempo que el Ryzen 9 5900X. Sin embargo, el Ryzen 9 7950X combina un muy buen rendimiento por núcleo con una mayor capacidad multi-core, y por eso obtiene el mejor tiempo total de los tres en la compilación del kernel.

### 2.3. Eficiencia por núcleos y eficiencia de costo

Para responder cuál hace un uso más eficiente de la cantidad de núcleos, tomamos la eficiencia paralela aproximada como:

$$
E = \frac{\text{speedup}}{n}
$$

Donde $n$ es la cantidad de núcleos del procesador.

| CPU | Speedup (base i5=1) | Núcleos | Eficiencia $E=speedup/n$ |
| --- | --- | --- | --- |
| i5-13600K | 1.00 | 14 | 0.071 |
| Ryzen 9 5900X | 0.94 | 12 | 0.078 |
| Ryzen 9 7950X | 1.65 | 16 | 0.103 |

Según esta métrica, el **Ryzen 9 7950X** es el que aprovecha mejor su cantidad de núcleos en la compilación del kernel, porque logra la mayor eficiencia relativa.

En términos de costo total (dinero y energía), la conclusión depende del criterio:

- **Rendimiento absoluto**: Ryzen 9 7950X (menor tiempo total).
- **Relación precio/rendimiento**: i5-13600K (muy buen desempeño con costo menor que el 7950X).
- **Rendimiento por Watt**: Ryzen 9 5900X (opción equilibrada con menor consumo relativo).

Por lo tanto, si el objetivo principal es terminar antes la compilación conviene el 7950X; si se prioriza costo-beneficio general conviene el i5-13600K; y si se prioriza consumo energético, el 5900X aparece como la alternativa más eficiente.

## 3. GNU GCC Profiling

Ahora en este apartado realizaremos la guía de Time profiling siguiendo los procedimientos propuestos.

### 3.1. Preparación y ejecución del programa instrumentado

Primero se compiló el programa con soporte de profiling usando `-pg`, enlazando ambos archivos fuente para generar el ejecutable `test_gprof`.

Comando utilizado:

```bash
gcc -Wall -pg test_gprof.c test_gprof_new.c -o test_gprof
```

![Compilación con -pg](attachments/Screenshot_20260329_214323%20%281%29.png)

Luego se verificó la generación del ejecutable y la presencia de los archivos en el directorio de trabajo.

```bash
ls
```

![Verificación de archivos](attachments/Screenshot_20260329_214506%20%282%29.png)

Después se ejecutó el binario para que se cree el archivo `gmon.out` con los datos de profiling.

```bash
./test_gprof
```

![Ejecución del binario](attachments/Screenshot_20260329_214728%20%283%29.png)

Finalmente se volvió a listar el directorio para confirmar la creación de `gmon.out`.

```bash
ls
```

![Generación de gmon.out](attachments/Screenshot_20260329_214848%20%284%29.png)

### 3.2. Análisis de resultados con gprof

En esta etapa se ejecutó `gprof` con distintas opciones, guardando cada salida en los logs numerados del 1 al 5.

#### Log 1 - Salida base de gprof

Comando:

```bash
gprof test_gprof gmon.out > analysis.txt
```

Captura:

![gprof salida base](attachments/Screenshot_20260329_215044%20%285%29.png)

Archivo asociado: `logs/analysis_1.txt`

Breve interpretación: en la corrida base, `func1` consume la mayor parte del tiempo de CPU, seguida por `func2`; además se observa el grafo de llamadas completo.

```text
Flat profile:

Each sample counts as 0.01 seconds.
    %   cumulative   self              self     total
 time   seconds   seconds    calls   s/call   s/call  name
 57.39      6.25     6.25        1     6.25     6.63  func1
 35.69     10.14     3.89        1     3.89     3.89  func2
    3.59     10.53     0.39                             main
    3.50     10.91     0.38        1     0.38     0.38  new_func1
```

#### Log 2 - Opción -a

Comando:

```bash
gprof -a test_gprof gmon.out > analysis.txt
```

Captura:

![gprof con -a](attachments/Screenshot_20260329_215925%20%286%29.png)

Archivo asociado: `logs/analysis_2.txt`

Breve interpretación: con `-a` se muestran conteos estáticos en el reporte; en esta salida predomina `func1` y aparece con 2 llamadas.

```text
Flat profile:

Each sample counts as 0.01 seconds.
    %   cumulative   self              self     total
 time   seconds   seconds    calls   s/call   s/call  name
 93.08     10.14    10.14        2     5.07     5.26  func1
    3.59     10.53     0.39                             main
    3.50     10.91     0.38        1     0.38     0.38  new_func1
```

#### Log 3 - Opción -b

Comando:

```bash
gprof -b test_gprof gmon.out > analysis.txt
```

Captura:

![gprof con -b](attachments/Screenshot_20260329_220210%20%287%29.png)

Archivo asociado: `logs/analysis_3.txt`

Breve interpretación: `-b` muestra una versión breve del reporte (sin textos explicativos extensos), manteniendo flat profile, call graph e índice.

```text
Flat profile:

Each sample counts as 0.01 seconds.
    %   cumulative   self              self     total
 time   seconds   seconds    calls   s/call   s/call  name
 57.39      6.25     6.25        1     6.25     6.63  func1
 35.69     10.14     3.89        1     3.89     3.89  func2
    3.59     10.53     0.39                             main
    3.50     10.91     0.38        1     0.38     0.38  new_func1
```

#### Log 4 - Opciones -p -b

Comando:

```bash
gprof -p -b test_gprof gmon.out > analysis.txt
```

Captura:

![gprof con -p -b](attachments/Screenshot_20260329_220406%20%288%29.png)

Archivo asociado: `logs/analysis_4.txt`

Breve interpretación: con `-p -b` se enfoca la salida en el flat profile (resumen por función), eliminando el call graph.

```text
Flat profile:

Each sample counts as 0.01 seconds.
    %   cumulative   self              self     total
 time   seconds   seconds    calls   s/call   s/call  name
 57.39      6.25     6.25        1     6.25     6.63  func1
 35.69     10.14     3.89        1     3.89     3.89  func2
    3.59     10.53     0.39                             main
    3.50     10.91     0.38        1     0.38     0.38  new_func1
```

#### Log 5 - Opciones -pfunc1 -b

Comando:

```bash
gprof -pfunc1 -b test_gprof gmon.out > analysis.txt
```

Captura:

![gprof filtrado por func1](attachments/Screenshot_20260329_220556%20%289%29.png)

Archivo asociado: `logs/analysis_5.txt`

Breve interpretación: se filtra el reporte para mostrar únicamente `func1`, lo cual permite aislar su tiempo de ejecución sin el resto de funciones.

```text
Flat profile:

Each sample counts as 0.01 seconds.
    %   cumulative   self              self     total
 time   seconds   seconds    calls   s/call   s/call  name
100.29      6.25     6.25        1     6.25     6.25  func1
```

### 3.3. Conclusión

El proceso de Time profiling permitió identificar rápidamente dónde se concentra el tiempo de CPU. En todos los reportes `func1` aparece como la función dominante, mientras que `func2` y `new_func1` tienen menor impacto relativo. Las distintas flags de `gprof` no cambian el comportamiento del programa, pero sí la forma en que se presenta la información, permitiendo pasar de un reporte completo a uno resumido o filtrado por función.
