# Trabajo Practico N°1

## El Rendimiento de las Computadoras

### Relacion Tiempo y Frecuencia

> Dado un procesador al que se le pueda cambiar la frecuencia, ejecutamos un código que demore alrededor de 10 segundos.
> ¿Qué sucede con el tiempo del programa al duplicar (variar) la frecuencia ?

Para realizar esta experiencia se construyo un pequeño codigo que ejecuta una cantidad predeterminada de instrucciones "nop" ("no operation"), las cuales son instrucciones para la CPU que hacen nada mas que consumir un ciclo (o varios) de reloj. Son usualmente usadas para benchmarking. Se determino el numero de instrucciones a base de prueba y error para que demore precisamente diez segundos la ejecucion al setear el clock a 8 MHz.

```c
void setup() {
  Serial.begin(115200);
  delay(2000);

  uint32_t start = ESP.getCycleCount();

  for (uint32_t i = 0; i < 30410000; i++) {
    asm volatile ("nop");
  }

  uint32_t end = ESP.getCycleCount();

  uint32_t cycles = end - start;
  float seconds = (float)cycles / (getCpuFrequencyMhz() * 1000000.0);

  Serial.println(seconds);
}
```

Al duplicar la frecuencia del CPU, el tiempo de ejecución no se redujo exactamente a la mitad debido a que no todo el tiempo de ejecución depende de la velocidad del procesador, solo paso de 10s a 5.34s. Existe una fracción del tiempo correspondiente a overhead del sistema, temporizadores, simulador y otras operaciones que no escalan con la frecuencia. Por lo tanto, el tiempo total puede modelarse como T = A/f + B. Este comportamiento coincide con la Ley de Amdahl, donde la parte no acelerable limita el speedup máximo del sistema.

---

### Benchmarks

> Armar una lista de benchmarks
> ¿Cuales les serían más útiles a cada uno?
> ¿Cuáles podrían llegar a medir mejor las tareas que ustedes realizan a diario?
> Pensar en las tareas que cada uno realiza a diario y escribir en una tabla de dos entradas las tareas y que benchmark la representa mejor.

| Tarea                         | Benchmark                                 |
| ------------------------------------ | ------------------------------------------------------------------------------------- |
| Generación de código con Claude Code | Latencia de red (ms), ancho de banda de red (Mbps), tiempo de respuesta de API        |
| Ejecución de tests                   | Tiempo de ejecución de procesos, CPU time, benchmark de CPU multi-core                |
| Ejecuciones de pipelines CI/CD       | CPU multi-core performance, Disk I/O throughput (MB/s), Disk IOPS, Network throughput |
| Pruebas manuales con Postman         | Latencia de red (RTT), tiempo de respuesta del servidor, requests por segundo         |
| Búsquedas en bases de datos          | Disk IOPS, Disk latency, Memory latency, tiempo de ejecución de queries               |
| Streaming de películas               | Network throughput sostenido (Mbps), buffering rate, packet loss                      |
| Online gaming                        | Network latency (ping), jitter, packet loss, FPS                                      |
| Descargas de archivos                | Network throughput (Mbps), Disk write throughput (MB/s)                               |

> ¿Cual es el rendimiento de estos procesadores para compilar el kernel?
> Intel Core i5-13600K (base)
> AMD Ryzen 9 5900X 12-Core

El Intel Core i5-13600K demora 83 segundos en compilar el kernel, mientras que el AMD Ryzen 9 5900X 12-Core demora 97 segundos. Podemos entonces determinar que el procesador Intel tiene un rendimiento de 0.0120 compilaciones/s, mientras que el AMD tiene un rendimiento de 0.0103 compilaciones/s. Esto es una diferencia de alrededor 17% en favor del procesador Intel.

Pordemos ver esto expresado en la siguiente tabla:

| CPU           | Speedup      |
| ------------- | ------------ |
| i5-13600K     | 1            |
| Ryzen 9 5900X | 83/97 = 0.86 |

La compilación del kernel es una tarea parcialmente paralelizable. Durante la compilación, muchos archivos pueden compilarse en paralelo, lo que aprovecha múltiples núcleos del procesador. Sin embargo, existen etapas del proceso que deben ejecutarse de forma secuencial, como el linking final y algunas dependencias entre archivos. Debido a esto, el tiempo total de compilación depende tanto del rendimiento multi-core como del rendimiento single-core.

El Intel Core i5-13600K posee mayor frecuencia de reloj y mejor rendimiento por núcleo, lo que mejora las partes secuenciales del proceso. Por esta razón, a pesar de tener menos threads que el Ryzen 9 5900X, logra un menor tiempo total de compilación del kernel.

> ¿Cual es la aceleración cuando usamos un AMD Ryzen 9 7950X 16-Core?
> ¿Cual de ellos hace un uso más eficiente de la cantidad de núcleos que tiene?
> ¿Cuál es más eficiente en términos de costo (dinero y energía)?

El procesador AMD Ryzen 9 7950X 16-Core es ~1.6 veces más rápido que el i5-13600Ky ~1.87 veces más rápido que el Ryzen 9 5900X compilando el kernel.

En terminos del uso eficiente de sus nucleos, se obtuvieron los siguientes resultados:

| CPU           | Speedup      |
| ------------- | ------------ |
| i5-13600K     | 1            |
| Ryzen 9 5900X | 83/97 = 0.86 |
| Ryzen 9 7950X | 83/52 = 1.60 |

| CPU           | Speedup | Núcleos | Eficiencia |
| ------------- | ------- | ------- | ---------- |
| i5-13600K     | 1       | 14      | 0.071      |
| Ryzen 9 5900X | 0.86    | 12      | 0.072      |
| Ryzen 9 7950X | 1.60    | 16      | 0.100      |

Tomando como base el Intel Core i5-13600K, se calcula el speedup para los demás procesadores como la relación entre los tiempos de ejecución. El Ryzen 9 5900X presenta un speedup de 0.86, por lo que resulta más lento que el procesador base, mientras que el Ryzen 9 7950X presenta un speedup de 1.60, siendo aproximadamente un 60% más rápido.

La eficiencia se calcula como Speedup/n, donde n es la cantidad de núcleos. Al calcular la eficiencia para cada procesador, se observa que el Ryzen 9 7950X presenta la mayor eficiencia, lo que indica que es el procesador que mejor aprovecha la cantidad de núcleos en la compilación del kernel. Esto se debe a que la tarea es paralelizable pero no completamente, por lo que la eficiencia está limitada por las partes secuenciales del proceso.

En términos de rendimiento absoluto, el Ryzen 9 7950X es el más rápido para la compilación del kernel. Sin embargo, al analizar la eficiencia en términos de costo, se debe considerar el rendimiento por unidad de dinero y por consumo energético. El Ryzen 9 7950X posee el mayor rendimiento pero también el mayor costo y consumo energético. El Intel Core i5-13600K presenta un rendimiento cercano pero con menor costo, por lo que ofrece la mejor relación precio/rendimiento. Por otro lado, el Ryzen 9 5900X presenta menor rendimiento pero también menor consumo energético, por lo que puede considerarse eficiente en términos de rendimiento por watt. Por lo tanto, el procesador más eficiente depende del criterio: el 7950X en rendimiento absoluto, el i5-13600K en precio/rendimiento y el 5900X en eficiencia energética.

| CPU           | Rendimiento | Precio | Consumo | Eficiencia                 |
| ------------- | ----------- | ------ | ------- | -------------------------- |
| i5-13600K     | Alto        | Medio  | Medio   | Mejor precio/rendimiento   |
| Ryzen 9 5900X | Medio       | Medio  | Bajo    | Mejor rendimiento/W        |
| Ryzen 9 7950X | Muy alto    | Alto   | Alto    | Mejor rendimiento absoluto |


---

### GNU GCC Profiling

#### _Habilitamos creacion de perfiles durante la compilacion_

Dado el codigo en C:

```c
#include<stdio.h>

void new_func1(void);

void func1(void)
{
    printf("\n Inside func1 \n");
    int i = 0;

    for(;i<0xffffffff;i++);
    new_func1();

    return;
}

static void func2(void)
{
    printf("\n Inside func2 \n");
    int i = 0;

    for(;i<0xafffffff;i++);
    return;
}

int main(void)
{
    printf("\n Inside main()\n");
    int i = 0;

    for(;i<0xfffff11;i++);
    func1();
    func2();

    return 0;
}

```

```c
#include<stdio.h>

void new_func1(void)
{
    printf("\n Inside new_func1()\n");
    int i = 0;

    for(;i<0xffffffee;i++);

    return;
}
```

Nos aseguramos que la generacion de perfiles este habilitada a la hora de compilacion agregando la opcion `-pg`en el paso de compilacion:

`gcc -Wall -pg test_gprof.c test_gprof_new.c -o test_gprof`

<img width="2015" height="479" alt="image" src="https://github.com/user-attachments/assets/e2a8ede4-0d77-4121-b9e8-32bcf887dea9" />

#### _Ejecutamos el codigo_

Procedemos a ejecutar el archivo binario producido para generar la informacion de perfiles:

`./test_gprof`

Al ejecutar el binario vemos como se genera un nuevo archivo llamado `gmon.out` en el directorio de trabajo actual.

<img width="1615" height="200" alt="image" src="https://github.com/user-attachments/assets/d882daa5-db15-41d1-a68c-6a77ef4e9d58" />

#### _Ejecutamos gprof_

La herramienta se ejecuta con el nombre del ejecutable a analizar, y el archivo `gmon.out` producido anteriormente.

`gprof test_gprof gmon.out > analysis.txt`

Esto produce un archivo de analisis que contiene toda la informacion de perfil deseada `analysis.txt`.

<img width="1866" height="231" alt="image" src="https://github.com/user-attachments/assets/d48f110b-b5ac-42a3-a596-f3f327270238" />

#### _Interpretamos la informacion de perfil_

Analizamos el contenido del archivo generado:

```txt
Flat profile:

Each sample counts as 0.01 seconds.
  %   cumulative   self              self     total           
 time   seconds   seconds    calls   s/call   s/call  name    
 33.83      7.93     7.93        1     7.93    15.67  func1
 33.02     15.67     7.74        1     7.74     7.74  func2
 33.02     23.41     7.74        1     7.74     7.74  new_func1
  0.13     23.44     0.03                             main

granularity: each sample hit covers 4 byte(s) for 0.04% of 23.44 seconds

index % time    self  children    called     name
                                                 <spontaneous>
[1]    100.0    0.03   23.41                 main [1]
                7.93    7.74       1/1           func1 [2]
                7.74    0.00       1/1           func2 [3]
-----------------------------------------------
                7.93    7.74       1/1           main [1]
[2]     66.9    7.93    7.74       1         func1 [2]
                7.74    0.00       1/1           new_func1 [4]
-----------------------------------------------
                7.74    0.00       1/1           main [1]
[3]     33.0    7.74    0.00       1         func2 [3]
-----------------------------------------------
                7.74    0.00       1/1           func1 [2]
[4]     33.0    7.74    0.00       1         new_func1 [4]
-----------------------------------------------


Index by function name
   [2] func1                   [1] main
   [3] func2                   [4] new_func1
```

Podemos ver como el programa tardo un total de 23.44 segundos en ejecutarse, ey en la tabla podemos ver el tiempo que consumio cada funcion individualmente, incluyendo la ejecucion de su propio codigo, y el tiempo de las funciones que llama.

Interpretando el grafo vemos:
- main llama una vez a func1 y una vez a func2 --> su tiempo de ejecucion es casi todo de llamados
- func1 llama a new_func1 --> la mitad del tiempo es propio y la otra es de llamada
- func2 no llama a nadie --> todo su tiempo es propio
- new_func1 no llama a nadie --> todo su tiempo es propio

Podriamos decir que el punto de dolor mas grande aqui es func1 y su llamado a new_func1, ya que ocupan el 66% del tiempo de ejecucion.

#### _Customizando el output con flags_

Podemos suprimir la impresion de funciones declaradas estaticamente (privadas) con `-a`

`gprof -a test_gprof gmon.out > analysis.txt`

<img width="1901" height="210" alt="image" src="https://github.com/user-attachments/assets/1b8b2d0f-37cd-4080-82ed-daba0ab2f7d1" />

```txt
Flat profile:

Each sample counts as 0.01 seconds.
  %   cumulative   self              self     total           
 time   seconds   seconds    calls   s/call   s/call  name    
 time   seconds   seconds    calls   s/call   s/call  name    
 66.85     15.67    15.67        2     7.83    11.71  func1
 33.02     23.41     7.74        1     7.74     7.74  new_func1
  0.13     23.44     0.03                             main

granularity: each sample hit covers 4 byte(s) for 0.04% of 23.44 seconds

index % time    self  children    called     name
                                                 <spontaneous>
[1]    100.0    0.03   23.41                 main [1]
               15.67    7.74       2/2           func1 [2]
-----------------------------------------------
               15.67    7.74       2/2           main [1]
[2]     99.9   15.67    7.74       2         func1 [2]
                7.74    0.00       1/1           new_func1 [3]
-----------------------------------------------
                7.74    0.00       1/1           func1 [2]
[3]     33.0    7.74    0.00       1         new_func1 [3]
-----------------------------------------------
```

Podemos eliminar los textos detallados usando `-b`

`gprof -b test_gprof gmon.out > analysis.txt`

<img width="1897" height="754" alt="image" src="https://github.com/user-attachments/assets/e3ee623f-660a-425b-9735-8f9bf94e7fa9" />

Podemos imprimir solo el perfil plano usando `-p`

`gprof -p test_gprof gmon.out > analysis.txt`

<img width="1897" height="862" alt="image" src="https://github.com/user-attachments/assets/d7536bfb-b920-4c23-bd4d-e8f0d5b69d1b" />

Podemos imprimir informacion relacionada con funciones especificas en perfil plano con `-pfuncname`

`gprof -pfucn1 test_gprof gmon.out > analysis.txt`

<img width="1941" height="803" alt="image" src="https://github.com/user-attachments/assets/08b29648-f6f4-4c89-bf3e-4865a165c16a" />

#### _Generamos un grafico_

La herramienta `gprof2dot` nos permite generar una visualizacion de la salida de gprof.

<img width="2120" height="1184" alt="image" src="https://github.com/user-attachments/assets/658ffc45-e45e-4703-8470-fd63faf2284e" />

### Linux Perf

Es una pequeña herramienta que permite crear perfiles de programas. Esta utiliza perfiles estadisticos, donde sondea el programa y ve que funcion esta ejecutandose.

Es menos precisa pero tiene menos impacto en el rendimiento que otras opciones.

`sudo perf record ./examples/test_gprof`

`sudo perf report`

<img width="769" height="1386" alt="image" src="https://github.com/user-attachments/assets/b6d7ec88-183b-45bc-b997-f5ddc50f1453" />

---

### Conclusion

En este trabajo práctico se analizó el rendimiento de las computadoras considerando la relación entre frecuencia y tiempo de ejecución, la comparación de procesadores en tareas paralelizables y el uso de herramientas de profiling. Se observó que aumentar la frecuencia o la cantidad de núcleos no reduce el tiempo de ejecución de forma proporcional debido a las partes secuenciales del programa y al overhead del sistema, lo que se relaciona con la Ley de Amdahl. Además, se comprobó que el rendimiento no depende solo del hardware sino también de cómo se optimiza el software, ya que mediante profiling es posible identificar cuellos de botella y mejorar las partes críticas del programa. En conclusión, el rendimiento de un sistema es el resultado del equilibrio entre frecuencia, paralelismo, eficiencia y optimización del código.
