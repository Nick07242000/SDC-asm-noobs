# Trabajo Práctico N°1

## El Rendimiento de las Computadoras

---

## Consigna 1

> Ejecutar un código que demore alrededor de 10 segundos. Puede ser un bucle for con sumas de enteros por un lado y otro con suma de floats por otro lado.  
> ¿Qué sucede con el tiempo del programa al duplicar (variar) la frecuencia?

Para la prueba se ejecutó en una ESP32 un ciclo for que solo incrementa una variable count.

```c
void setup() {

 Serial.begin(115200);

 setCpuFrequencyMhz(5);
 uint32_t start = ESP.getCycleCount();

 //contador
 volatile uint32_t count = 0;
 for (uint32_t i = 0; i < 14000000; i++) {
   count++;
 }

 uint32_t end = ESP.getCycleCount();
 uint32_t cycles = end - start;
 float seconds = (float)cycles / (getCpuFrequencyMhz() * 1000000.0);

 Serial.print("Frequency CPU: ");
 Serial.print(getCpuFrequencyMhz());
 Serial.println(" MHz");
 Serial.print("Cycles: ");
 Serial.println(cycles);
 Serial.print("Seconds: ");
 Serial.println(seconds);
}

void loop() {
}
```

Se inició con una frecuencia de CPU en 5 Mhz y se fue duplicando la frecuencia en cada prueba, cambiandola a 10, 20, 40, 80 y 160 Mhz.

Obteniendo estos resultados:

```
Frequency CPU: 5 MHz
Cycles: 53802920
Seconds: 10.76

Frequency CPU: 10 MHz
Cycles: 89240386
Seconds: 8.92

Frequency CPU: 20 MHz
Cycles: 164456311
Seconds: 8.22

Frequency CPU: 40 MHz
Cycles: 316481643
Seconds: 7.91

Frequency CPU: 80 MHz
Cycles: 621203227
Seconds: 7.77

Frequency CPU: 160 MHz
Cycles: 1230990822
Seconds: 7.69
```

Al ir aumentando la frecuencia de CPU el tiempo de ejecución del programa fue disminuyendo. Por ende, mejoró el rendimiento.  
Al hacer una comparación de desempeño (speedup), vemos que tiende a despreciarse a medida que se aumenta la frecuencia.

- Speedup de 5 a 10 Mz → 10.76/8.92 = **1.206**  
- Speedup de 10 a 20 Mz → 8.92/8.22 = **1.085**  
- Speedup de 20 a 40 Mz → 8.22/7.91 = **1.039**  
- Speedup de 40 a 80 Mz → 7.91/7.77 = **1.018**  
- Speedup de 80 a 160 Mz → 7.77/7.69 = **1.01**  

---

## Consigna 2

> Armar una lista de benchmarks, ¿cuales les serían más útiles a cada uno ?  
> ¿Cuáles podrían llegar a medir mejor las tareas que ustedes realizan a diario ?  
> Pensar en las tareas que cada uno realiza a diario y escribir en una tabla de dos entradas las tareas y que benchmark la representa mejor.

| Tarea                         | BenchMark                                                                 |
|------------------------------|---------------------------------------------------------------------------|
| Compilar proyectos en Java / C | Tiempo total de compilación (s), CPU multi-core utilization (%), Disk I/O throughput (MB/s), uso de memoria (MB) |
| Uso de IDE (IntelliJ, VSCode) | Consumo de RAM (MB), tiempo de apertura(ms) |
| Uso de navegador             | Tiempo de apertura(ms), tiempo de renderizado (ms), CPU usage (%), consumo de memoria (MB) |
| Transferencia de archivos    | Disk read/write throughput (MB/s), latencia de acceso (ms), latencia de descarga (ms) |
| Streaming (Netflix, Youtube) | Network throughput (Mbps), packet loss (%) |
| Anotaciones en .txt          | Tiempo de apertura de archivo (ms), tiempo de guardado (ms) |

---

> ¿Cuál es el rendimiento de estos procesadores para compilar el kernel?

> Intel Core i5-13600K (base)  
> AMD Ryzen 9 5900X 12-Core  

Datos obtenidos en https://openbenchmarking.org/test/pts/build-linux-kernel-1.15.0 :

| Procesador            | Seconds (Average) | Core’s |
|----------------------|------------------|--------|
| Intel Core i5-13600K | 72 +/- 5 s       | 14     |
| AMD Ryzen 9 5900X    | 76 +/- 8 s       | 12     |
| AMD Ryzen 9 7950X    | 50 +/- 6 s       | 16     |

El procesador Intel Core i5-13600K y el AMD Ryzen 9 5900X 12-Core tardan en promedio 72  y 76 segundos respectivamente en compilar el kernel.  
El rendimiento es la inversa de esos tiempos.

Rendimiento Intel Core i5-13600K = 1/72 = **0,013889**  
Rendimiento AMD Ryzen 9 5900X 12-Core = 1/76 = **0,013158**  

---


> Cual es la aceleración cuando usamos un AMD Ryzen 9 7950X 16-Core, cual de ellos hace un uso más eficiente de la cantidad de núcleos que tiene?

El procesador AMD Ryzen 9 7950X 16-Core tarda en promedio 50 s en compilar el kernel.  
Para encontrar la aceleración con respecto a los anteriores comparamos el desempeño.

- Speedup Intel Core i5-13600K vs AMD Ryzen 9 7950X  = 72/50 = **1.44**  
- Speedup AMD Ryzen 9 5900X  vs AMD Ryzen 9 7950X  = 76/50 = **1.52**  

Para comparar la eficiencia se tomó como pivote el AMD Ryzen 9 5900X.

| Procesador            | Speedup | Cores | Eficiencia |
|----------------------|--------|-------|-----------|
| AMD Ryzen 9 5900X    | **1**      | 12    | 1/12 = **0,0833** |
| Intel Core i5-13600K | 76/72 = **1,0555** | 14 | 1,0555/14 = **0,0754** |
| AMD Ryzen 9 7950X    | 76/50 = **1.52** | 16 | 1.52/16 = **0,095** |

El AMD Ryzen 9 7950X hace un uso más eficiente de sus núcleos, si bien tiene más de ellos el Speedup en comparación a los otros procesadores es superior.  
Es 52% más rápido que el AMD Ryzen 9 5900X y 44% más rápido que el Intel Core i5-13600K.

---

> ¿Cuál es más eficiente en términos de costo (dinero y energía)?

| Procesador            | Precio aprox. (us$) | Consumo (watts) | Efic./precio (*10^3) | Efic./consumo (*10^3) |
|----------------------|--------------------|----------------|---------------------|----------------------|
| AMD Ryzen 9 5900X    | 270                | 105            | 0,308519            | 0,7933               |
| Intel Core i5-13600K | 275                | 125            | 0,274182            | 0,6032               |
| AMD Ryzen 9 7950X    | 480                | 170            | 0,197917            | 0,5588               |

En términos de energía y dinero en comparación con la eficiencia de cada procesador, el AMD Ryzen 9 5900X es el que mejor relación Eficiencia/Precio y Eficiencia/Consumo tiene, y en último lugar al AMD Ryzen 9 7950X.

Conclusión: El AMD Ryzen 9 7950X maximiza rendimiento y eficiencia paralela, pero ese rendimiento adicional tiene mayor costo económico y energético.

---

## Consigna 3

> Mostrar con capturas de pantalla la realización del tutorial descripto en time profiling adjuntando las conclusiones sobre el uso del tiempo de las funciones.

### GNU GCC Profiling (gprof)

Paso 1: creación de perfiles habilitada durante la compilación  

En bash se compila con:

```bash
gcc -Wall -pg test_gprof.c test_gprof_new.c -o test_gprof
```

y se obtiene el ejecutable `test_gprof`

<img width="866" height="321" alt="image1" src="https://github.com/user-attachments/assets/0c323900-3610-474d-8258-536c506f9208" />

---

Paso 2: Ejecutar el código  

```bash
./test_gprof
```

Se obtiene `gmon.out`

<img width="866" height="453" alt="image9" src="https://github.com/user-attachments/assets/066d274e-1c32-47a9-8ed7-4df5999bda60" />

---

Paso 3: Ejecutar gprof  

```bash
gprof test_gprof gmon.out > analysis.txt
```

Se genera un archivo .txt con la información de perfil.

<img width="866" height="321" alt="image7" src="https://github.com/user-attachments/assets/84c4387b-2272-488e-bb13-86d3fc1fdab9" />

---

### Comprensión de la información de perfil

```txt
Flat profile:

Each sample counts as 0.01 seconds.
  %   cumulative   self              self     total           
 time   seconds   seconds    calls   s/call   s/call  name    
 54.50      9.14     9.14        1     9.14     9.71  func1
 38.76     15.64     6.50        1     6.50     6.50  func2
  3.40     16.21     0.57        1     0.57     0.57  new_func1
  3.34     16.77     0.56                             main

granularity: each sample hit covers 4 byte(s) for 0.06% of 16.77 seconds

index % time    self  children    called     name
                                                 <spontaneous>
[1]    100.0    0.56   16.21                 main [1]
                9.14    0.57       1/1           func1 [2]
                6.50    0.00       1/1           func2 [3]
-----------------------------------------------
                9.14    0.57       1/1           main [1]
[2]     57.9    9.14    0.57       1         func1 [2]
                0.57    0.00       1/1           new_func1 [4]
-----------------------------------------------
                6.50    0.00       1/1           main [1]
[3]     38.8    6.50    0.00       1         func2 [3]
-----------------------------------------------
                0.57    0.00       1/1           func1 [2]
[4]      3.4    0.57    0.00       1         new_func1 [4]
-----------------------------------------------


Index by function name

   [2] func1                   [1] main
   [3] func2                   [4] new_func1

```

Vemos que el programa tardó 16.77s en ejecutar, también cuánto tiempo tardó cada función por separado y su respectivo porcentaje con respecto al total.
Luego se ve el grafo de llamadas, con los tiempos que tardaron las funciones en ejecutarse con los tiempos que tardaron sus hijos, representando el total de la ejecución de la función padre.
Se puede ver que ‘func1’ es la que más tarda, representando un 57.9% del tiempo de ejecución.




### Customize gprof output using flags

**1. Suprima la impresión de funciones declaradas estáticamente (privadas) usando -a**
```bash
$ gprof -a test_gprof gmon.out > analysis.txt
```

```txt
Flat profile:

Each sample counts as 0.01 seconds.
  %   cumulative   self              self     total           
 time   seconds   seconds    calls   s/call   s/call  name    
 93.26     15.64    15.64        2     7.82     8.11  func1
  3.40     16.21     0.57        1     0.57     0.57  new_func1
  3.34     16.77     0.56                             main

granularity: each sample hit covers 4 byte(s) for 0.06% of 16.77 seconds

index % time    self  children    called     name
                                                 <spontaneous>
[1]    100.0    0.56   16.21                 main [1]
               15.64    0.57       2/2           func1 [2]
-----------------------------------------------
               15.64    0.57       2/2           main [1]
[2]     96.7   15.64    0.57       2         func1 [2]
                0.57    0.00       1/1           new_func1 [3]
-----------------------------------------------
                0.57    0.00       1/1           func1 [2]
[3]      3.4    0.57    0.00       1         new_func1 [3]
-----------------------------------------------


Index by function name

   [2] func1                   [1] main                    [3] new_func1

```
Vemos como desaparece func2, que es una función estática.

**2. Elimine los textos detallados usando -b**
```bash
$ gprof -b test_gprof gmon.out > analysis.txt
```
<img width="1300" height="717" alt="image2" src="https://github.com/user-attachments/assets/e7ace0c6-d7ae-4a02-a425-64c1473d918f" />

Desaparecen todos los textos que explican cada columna en las tablas.

**3. Imprima solo perfil plano usando -p**
```bash
$ gprof -p -b test_gprof gmon.out > analysis.txt
```

<img width="1290" height="700" alt="image5" src="https://github.com/user-attachments/assets/38d7fcdf-8b36-4867-a5f5-cc153d69d6ad" />

**4. Imprimir información relacionada con funciones específicas en perfil plano**
```bash
$ gprof -pfunc1 -b test_gprof gmon.out > analysis.txt
```
<img width="1290" height="700" alt="image6" src="https://github.com/user-attachments/assets/771ac8af-86ae-4f64-a5c6-04ee7d4aec86" />


### Genere un gráfico con gprof2dot 
```bash
$ gprof ./test_gprof gmon.out | gprof2dot |dot -Tpng -o img.png
```
<img width="1304" height="674" alt="image8" src="https://github.com/user-attachments/assets/d586564d-1090-41d5-b5d9-6e5aef093b93" />

## Profiling con linux perf
```bash
$ sudo perf record ./test_gprof
```
<img width="936" height="431" alt="image4" src="https://github.com/user-attachments/assets/e9a7637b-0889-4c24-897b-3369bcc51c6b" />


```bash
$ sudo perf report
```
<img width="866" height="761" alt="image3" src="https://github.com/user-attachments/assets/cd1962b9-94ab-4efd-80fc-3e179e175931" />
