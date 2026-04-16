all: libgini.so

libgini.so: gini_calc.c
	gcc -shared -fPIC -o libgini.so gini_calc.c

clean:
	rm -f libgini.so