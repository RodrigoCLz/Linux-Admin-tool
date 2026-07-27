#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <ctype.h>
#include <unistd.h>
#include <pwd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define BUF_SIZE 4096
#define PROC_DIR "/proc"

long get_total_ram_kb() {
    FILE *fp = fopen("/proc/meminfo", "r");
    if (!fp) return -1;
    char line[256];
    long total = -1;
    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "MemTotal: %ld kB", &total) == 1) break;
    }
    fclose(fp);
    return total;
}

long get_process_ram_kb(int pid) {
    char path[256];
    snprintf(path, sizeof(path), "/proc/%d/status", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;
    char line[256];
    long rss = -1;
    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "VmRSS: %ld kB", &rss) == 1) break;
    }
    fclose(fp);
    return rss;
}

int read_stat_file(int pid, unsigned long long *utime, unsigned long long *stime, int *ppid, char *state, int state_size __attribute__((unused)), char *comm, int comm_size) {
    char path[256];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;

    char buf[BUF_SIZE];
    if (!fgets(buf, sizeof(buf), fp)) { fclose(fp); return -1; }
    fclose(fp);

    // Format: pid (comm) state ppid pgrp session tty_nr tpgid flags min flt cminflt majflt cmajflt utime stime ...
    char *close_paren = strrchr(buf, ')');
    if (!close_paren) return -1;
    *close_paren = '\0';
    char *open_paren = strchr(buf, '(');
    if (!open_paren) return -1;
    strncpy(comm, open_paren + 1, comm_size - 1);
    comm[comm_size - 1] = '\0';

    char *rest = close_paren + 2; // skip ') '
    if (sscanf(rest, "%c", state) != 1) return -1;

    // Parse utime and stime (fields 11 and 12 after state)
    // Fields after state (space-separated):
    // 1:ppid 2:pgrp 3:session 4:tty 5:tpgid 6:flags 7:minflt 8:cminflt 9:majflt 10:cmajflt 11:utime 12:stime 13:cutime 14:cstime
    unsigned long long vals[15];
    char *p = rest;
    for (int i = 0; i < 15; i++) {
        while (*p == ' ') p++;
        if (*p == '\0') break;
        vals[i] = strtoull(p, &p, 10);
    }

    *ppid = (int)vals[0];
    *utime = vals[11];
    *stime = vals[12];
    return 0;
}

unsigned long long get_total_cpu_jiffies() {
    FILE *fp = fopen("/proc/stat", "r");
    if (!fp) return 0;
    char line[256];
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return 0; }
    fclose(fp);

    unsigned long long user, nice, sys, idle, iowait, irq, softirq, steal;
    if (sscanf(line, "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
               &user, &nice, &sys, &idle, &iowait, &irq, &softirq, &steal) < 4)
        return 0;

    return user + nice + sys + idle + iowait + irq + softirq + steal;
}

char *get_username(uid_t uid) {
    struct passwd *pw = getpwuid(uid);
    if (pw) return pw->pw_name;
    return "unknown";
}

struct proc_sample {
    int pid;
    int ppid;
    unsigned long long utime;
    unsigned long long stime;
    char comm[256];
    char state;
    uid_t uid;
    long ram_kb;
};

int collect_sample(struct proc_sample *samples, int max_count) {
    int count = 0;
    DIR *dir = opendir(PROC_DIR);
    if (!dir) return 0;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL && count < max_count) {
        if (!isdigit(entry->d_name[0])) continue;
        int pid = atoi(entry->d_name);

        struct proc_sample *s = &samples[count];
        s->pid = pid;
        if (read_stat_file(pid, &s->utime, &s->stime, &s->ppid, &s->state, sizeof(s->state), s->comm, sizeof(s->comm)) != 0)
            continue;

        s->ram_kb = get_process_ram_kb(pid);

        char status_path[256];
        snprintf(status_path, sizeof(status_path), "/proc/%d/status", pid);
        FILE *sfp = fopen(status_path, "r");
        s->uid = 0;
        if (sfp) {
            char sline[256];
            while (fgets(sline, sizeof(sline), sfp)) {
                if (sscanf(sline, "Uid: %u", &s->uid) == 1) break;
            }
            fclose(sfp);
        }

        count++;
    }

    closedir(dir);
    return count;
}

int main() {
    long total_ram = get_total_ram_kb();

    int max_procs = 4096;
    struct proc_sample *s1 = malloc(max_procs * sizeof(struct proc_sample));
    struct proc_sample *s2 = malloc(max_procs * sizeof(struct proc_sample));
    if (!s1 || !s2) { fprintf(stderr, "malloc failed\n"); return 1; }

    int count1 = collect_sample(s1, max_procs);
    unsigned long long total1 = get_total_cpu_jiffies();
    usleep(100000);
    unsigned long long total2 = get_total_cpu_jiffies();
    int count2 = collect_sample(s2, max_procs);

    printf("PID\tNOMBRE\tCPU_PCT\tMEM_PCT\tESTADO\tUSUARIO\tPPID\n");

    for (int i = 0; i < count1 && i < count2; i++) {
        if (s1[i].pid != s2[i].pid) continue;

        unsigned long long proc_delta = (s2[i].utime + s2[i].stime) - (s1[i].utime + s1[i].stime);
        unsigned long long total_delta = total2 - total1;
        double cpu_pct = (total_delta > 0) ? (100.0 * proc_delta) / total_delta : 0.0;

        double mem_pct = (total_ram > 0 && s1[i].ram_kb > 0) ? (100.0 * s1[i].ram_kb) / total_ram : 0.0;

        char *user = get_username(s1[i].uid);

        for (char *p = s1[i].comm; *p; p++) {
            if (*p == '\t' || *p == '\n') *p = ' ';
        }

        char state_str[4];
        switch (s1[i].state) {
            case 'R': strcpy(state_str, "RUN"); break;
            case 'S': strcpy(state_str, "SLP"); break;
            case 'D': strcpy(state_str, "DIS"); break;
            case 'Z': strcpy(state_str, "ZOM"); break;
            case 'T': strcpy(state_str, "STP"); break;
            default:  snprintf(state_str, sizeof(state_str), "%c", s1[i].state); break;
        }

        printf("%d\t%s\t%.1f\t%.1f\t%s\t%s\t%d\n",
               s1[i].pid, s1[i].comm, cpu_pct, mem_pct, state_str, user, s1[i].ppid);
    }

    free(s1);
    free(s2);
    return 0;
}
