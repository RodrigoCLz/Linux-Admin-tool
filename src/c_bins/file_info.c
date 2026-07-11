#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>
#include <string.h>

void print_mode(mode_t mode, char *buf) {
    buf[0] = S_ISDIR(mode) ? 'd' : (S_ISLNK(mode) ? 'l' : '-');
    buf[1] = (mode & S_IRUSR) ? 'r' : '-';
    buf[2] = (mode & S_IWUSR) ? 'w' : '-';
    buf[3] = (mode & S_IXUSR) ? 'x' : '-';
    buf[4] = (mode & S_IRGRP) ? 'r' : '-';
    buf[5] = (mode & S_IWGRP) ? 'w' : '-';
    buf[6] = (mode & S_IXGRP) ? 'x' : '-';
    buf[7] = (mode & S_IROTH) ? 'r' : '-';
    buf[8] = (mode & S_IWOTH) ? 'w' : '-';
    buf[9] = (mode & S_IXOTH) ? 'x' : '-';
    buf[10] = '\0';
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: file_info <ruta> [ruta2 ...]\n");
        return 1;
    }

    // Header
    printf("RUTA\tTIPO\tTAMANIO\tPERMISOS\tPROPIETARIO\tGRUPO\tMODIFICACION\n");

    for (int i = 1; i < argc; i++) {
        struct stat st;
        if (lstat(argv[i], &st) != 0) {
            perror(argv[i]);
            continue;
        }

        char perms[11];
        print_mode(st.st_mode, perms);

        char *tipo;
        if (S_ISDIR(st.st_mode)) tipo = "directorio";
        else if (S_ISREG(st.st_mode)) tipo = "archivo";
        else if (S_ISLNK(st.st_mode)) tipo = "enlace";
        else if (S_ISCHR(st.st_mode)) tipo = "caracter";
        else if (S_ISBLK(st.st_mode)) tipo = "bloque";
        else if (S_ISFIFO(st.st_mode)) tipo = "fifo";
        else if (S_ISSOCK(st.st_mode)) tipo = "socket";
        else tipo = "desconocido";

        struct passwd *pw = getpwuid(st.st_uid);
        struct group *gr = getgrgid(st.st_gid);
        char *owner = pw ? pw->pw_name : "?";
        char *group = gr ? gr->gr_name : "?";

        char mtime[64];
        struct tm *tm = localtime(&st.st_mtime);
        strftime(mtime, sizeof(mtime), "%Y-%m-%d %H:%M:%S", tm);

        printf("%s\t%s\t%ld\t%s\t%s\t%s\t%s\n",
               argv[i], tipo, (long)st.st_size, perms, owner, group, mtime);
    }

    return 0;
}
