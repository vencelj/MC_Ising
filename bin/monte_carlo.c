#include "monte_carlo.h"

void load_config(struct SimConfig *sim, const char *dirPath){
    char fullPath[1024];
    snprintf(fullPath, sizeof(fullPath), "%s/config.bin", dirPath);

    FILE *file = fopen(fullPath, "rb");
    if (file == NULL) {
        return;
    }

    fread(&sim->run_time, sizeof(unsigned long long), 1, file);
    fread(&sim->J, sizeof(float), 1, file);
    fread(&sim->T_min, sizeof(float), 1, file);
    fread(&sim->T_max, sizeof(float), 1, file);
    fread(&sim->L, sizeof(uint32_t), 1, file);
    fread(&sim->init, sizeof(enum InitMethod), 1, file);

    fclose(file);
}

void load_atoms(struct SimConfig *sim, int8_t *atoms, const char *dirPath){
    char fullPath[1024];
    snprintf(fullPath, sizeof(fullPath), "%s/atoms.bin", dirPath);

    FILE *file = fopen(fullPath, "rb");
    if (file == NULL) {
        return;
    }

    uint32_t L = sim->L;
    size_t total_elements = (size_t)L * L * L;

    fread(atoms, sizeof(int8_t), total_elements, file);

    fclose(file);
}

void save_atoms(struct SimConfig *sim, int8_t *atoms, const char *dirPath){
    char fullPath[1024];
    snprintf(fullPath, sizeof(fullPath), "%s/atoms.bin", dirPath);

    FILE *file = fopen(fullPath, "ab");
    if (file == NULL) {
        return;
    }

    uint32_t L = sim->L;
    size_t total_elements = (size_t)L * L * L;

    fwrite(atoms, sizeof(int8_t), total_elements, file);

    fclose(file);
}

void load_temps(struct SimConfig *sim, float *temps, const char *dirPath){
    char fullPath[1024];
    snprintf(fullPath, sizeof(fullPath), "%s/temp_cycle.bin", dirPath);

    FILE *file = fopen(fullPath, "rb");
    if (file == NULL) {
        return;
    }

    uint64_t N = sim->run_time;

    fread(temps, sizeof(float), N, file);

    fclose(file);
}

void save_measurment(struct SimConfig *sim, float *magnetization, float *energy, const char *dirPath){
    char fullPath[1024];
    snprintf(fullPath, sizeof(fullPath), "%s/measurment.bin", dirPath);

    FILE *file = fopen(fullPath, "wb");
    if (file == NULL) {
        return;
    }

    uint32_t N = sim->run_time;

    fwrite(magnetization, sizeof(float), N, file);
    fwrite(energy, sizeof(float), N, file);

    fclose(file);
}
