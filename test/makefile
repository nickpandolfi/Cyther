all: randomtreetest

randomtreetest: randomtreetest.o tree.o random.o
	gcc -g --std=gnu89 randomtreetest.o tree.o random.o -o randomtreetest

randomtreetest.o: randomtreetest.c tree.h random.h
	gcc -g -c --std=gnu89 randomtreetest.c


random.o: random.c random.h
	gcc -g -c random.c

tree.o: tree.c tree.h
	gcc -g -c tree.c



clean:
	rm -f randomtreetest
	rm -f *.o
