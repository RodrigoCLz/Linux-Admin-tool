#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <errno.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: ps_kill <PID> [señal]\n");
        return 1;
    }

    int pid = atoi(argv[1]);
    if (pid <= 0) {
        fprintf(stderr, "PID inválido: %s\n", argv[1]);
        return 1;
    }

    int sig = SIGTERM;
    if (argc >= 3) {
        sig = atoi(argv[2]);
        if (sig <= 0) {
            fprintf(stderr, "Señal inválida: %s\n", argv[2]);
            return 1;
        }
    }

    if (kill(pid, sig) != 0) {
        perror("kill");
        return 1;
    }

    printf("OK: Señal %d enviada al PID %d\n", sig, pid);
    return 0;
}
