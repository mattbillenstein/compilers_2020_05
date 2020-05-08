/* main.c */
#include <stdio.h>

extern int hello();

void _print_int(int x) {
    printf("out: %i\n", x);
}

int main() {
    printf("hello() returned %i\n", hello());
}
