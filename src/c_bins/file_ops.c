#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

#define BUF_SIZE 65536

void copy_file(const char *src, const char *dst) {
    struct stat st;
    if (stat(src, &st) != 0) { perror(src); return; }

    int fd_src = open(src, O_RDONLY);
    if (fd_src < 0) { perror(src); return; }

    int fd_dst = open(dst, O_WRONLY | O_CREAT | O_TRUNC, st.st_mode & 0777);
    if (fd_dst < 0) { perror(dst); close(fd_src); return; }

    char buf[BUF_SIZE];
    ssize_t n;
    while ((n = read(fd_src, buf, sizeof(buf))) > 0) {
        if (write(fd_dst, buf, n) != n) {
            perror("write");
            close(fd_src);
            close(fd_dst);
            return;
        }
    }

    close(fd_src);
    close(fd_dst);
    printf("OK: copiado %s -> %s\n", src, dst);
}

void move_file(const char *src, const char *dst) {
    if (rename(src, dst) == 0) {
        printf("OK: movido %s -> %s\n", src, dst);
    } else {
        if (errno == EXDEV) {
            copy_file(src, dst);
            if (remove(src) == 0)
                printf("OK: movido %s -> %s\n", src, dst);
            else
                perror("remove");
        } else {
            perror("rename");
        }
    }
}

void delete_file(const char *path) {
    struct stat st;
    if (lstat(path, &st) != 0) { perror(path); return; }

    if (S_ISDIR(st.st_mode)) {
        fprintf(stderr, "Eliminar directorios no soportado: %s\n", path);
        return;
    }

    if (remove(path) == 0)
        printf("OK: eliminado %s\n", path);
    else
        perror("remove");
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Uso: file_ops <copy|move|delete> <src> [dst]\n");
        return 1;
    }

    if (strcmp(argv[1], "copy") == 0) {
        if (argc < 4) { fprintf(stderr, "copy requiere origen y destino\n"); return 1; }
        copy_file(argv[2], argv[3]);
    } else if (strcmp(argv[1], "move") == 0) {
        if (argc < 4) { fprintf(stderr, "move requiere origen y destino\n"); return 1; }
        move_file(argv[2], argv[3]);
    } else if (strcmp(argv[1], "delete") == 0) {
        delete_file(argv[2]);
    } else {
        fprintf(stderr, "Operación desconocida: %s (use copy, move, delete)\n", argv[1]);
        return 1;
    }

    return 0;
}
