#ifndef MONTE_CARLO_H
#define MONTE_CARLO_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <time.h>
#include <stdbool.h>

enum InitMethod{
    RANDOM,
    WARM_UP,
};

struct SimConfig{
    uint64_t run_time; // iterations
    float J; // Exchange energy
    float T_min; // start temperature
    float T_max; // end temperature
    uint32_t L; // Lattice dimension
    int32_t init; // init
};

struct SimMeas{
    int8_t *atoms; // pointer in lattice
    float *temps;
    float *energy;
    int64_t *magnetization;
};

// rand between 0-1
#define PROB()(((float)rand())/((float)RAND_MAX))

static const double bolzmannConst = 1; // 8.617333262e-5 eV

// load config.txt
void load_config(struct SimConfig *sim, const char *dirPath);

// load temp_cycle.bin
void load_temps(struct SimConfig *sim, float *temps, const char *dirPath);

// load atoms.bin
void load_atoms(struct SimConfig *sim, int8_t *atoms, const char *dirPath);

// append atoms.bin
void save_atoms(struct SimConfig *sim, int8_t *atoms, const char *dirPath);

// save measurment.bin
void save_measurment(struct SimConfig *sim, int64_t *magnetization, float *energy, const char *dirPath);

#endif