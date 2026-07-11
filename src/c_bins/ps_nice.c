#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <errno.h>

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Uso: ps_nice <PID> <nice_valor>\n");
        return 1;
    }

    int pid = atoi(argv[1]);
    int nice_val = atoi(argv[2]);

    if (pid <= 0) {
        fprintf(stderr, "PID inválido: %s\n", argv[1]);
        return 1;
    }

    if (nice_val < -20 || nice_val > 19) {
        fprintf(stderr, "Nice inválido (debe ser -20 a 19): %d\n", nice_val);
        return 1;
    }

    int old_nice = getpriority(PRIO_PROCESS, pid);
    if (old_nice == -1 && errno != 0) {
        perror("getpriority");
        return 1;
    }

    if (setpriority(PRIO_PROCESS, pid, nice_val) != 0) {
        perror("setpriority");
        return 1;
    }

    printf("OK: Prioridad del PID %d cambiada de %d a %d\n", pid, old_nice, nice_val);
    return 0;
}
