#include "monte_carlo.h"

float totalEnergy(struct SimConfig *sim, struct SimMeas *meas){
    float energyTotal = 0;
    uint32_t L = sim->L;
    float J = sim->J;

    float energyLUT[7]; 
    for (int s = -6; s <= 6; s += 2) {
        energyLUT[(s + 6) / 2] = -J/2.0f * (float)s;
    }

    for (uint64_t i=0;i<L;i++){
        for (uint64_t j=0;j<L;j++){
            for (uint64_t k=0;k<L;k++){
                int am = (i == 0) ? L - 1 : i - 1;
                int ap = (i == L - 1) ? 0 : i + 1;
                int bm = (j == 0) ? L - 1 : j - 1;
                int bp = (j == L - 1) ? 0 : j + 1;
                int cm = (k == 0) ? L - 1 : k - 1;
                int cp = (k == L - 1) ? 0 : k + 1;

                int8_t spin = meas->atoms[i*L*L + j*L + k];
                int8_t spinNeighbours = meas->atoms[am*L*L + j*L + k]
                                        + meas->atoms[ap*L*L + j*L + k]
                                        + meas->atoms[i*L*L + bm*L + k]
                                        + meas->atoms[i*L*L + bp*L + k]
                                        + meas->atoms[i*L*L + j*L + cm]
                                        + meas->atoms[i*L*L + j*L + cp];

                int8_t spinConfiguration = spin * spinNeighbours;
                energyTotal += energyLUT[(spinConfiguration + 6) / 2];
            }
        }
    }
    return energyTotal;
}

void monteCarlo(struct SimConfig *sim, struct SimMeas *meas, uint64_t iterCounter, bool savedMeas){
    uint32_t L = sim->L;
    float J = sim->J;
    uint64_t N = (uint64_t)L*L*L;
    float temp = meas->temps[iterCounter];
    float energyIter;
    int64_t magnetizationIter;
    
    if (iterCounter == 0){
        if (!savedMeas){
            energyIter = totalEnergy(sim, meas);
            magnetizationIter = 0;
            for (uint64_t i=0; i<N; i++){
                magnetizationIter += meas->atoms[i];
            }
        }
        else{
            energyIter = meas->energy[sim->run_time-1];
            magnetizationIter = meas->magnetization[sim->run_time-1];
        }
    }
    else{
        energyIter = meas->energy[iterCounter-1];
        magnetizationIter = meas->magnetization[iterCounter-1];
    }  

    float energyLUT[7]; 
    float probLUT[7]; 
    for (int s = -6; s <= 6; s += 2) {
        float deltaE = 2.0f * J * (float)s;
        probLUT[(s + 6) / 2] = 1.0f / (1.0f + exp(-deltaE/(bolzmannConst*temp)));
    }

    for (int8_t eq = 0; eq<10; eq++){
        for (uint64_t i=0; i<N;i++){
            uint32_t a = rand() % L; 
            uint32_t b = rand() % L; 
            uint32_t c = rand() % L;
    
            int am = (a == 0) ? L - 1 : a - 1;
            int ap = (a == L - 1) ? 0 : a + 1;
            int bm = (b == 0) ? L - 1 : b - 1;
            int bp = (b == L - 1) ? 0 : b + 1;
            int cm = (c == 0) ? L - 1 : c - 1;
            int cp = (c == L - 1) ? 0 : c + 1;
    
            int8_t spin = meas->atoms[a*L*L + b*L + c];
            int8_t spinNeighbours = meas->atoms[am*L*L + b*L + c]
                                    + meas->atoms[ap*L*L + b*L + c]
                                    + meas->atoms[a*L*L + bm*L + c]
                                    + meas->atoms[a*L*L + bp*L + c]
                                    + meas->atoms[a*L*L + b*L + cm]
                                    + meas->atoms[a*L*L + b*L + cp];
            
            
            if (PROB() < probLUT[(spinNeighbours + 6) / 2]) {
                meas->atoms[a*L*L + b*L + c] = 1;
            } else {
                meas->atoms[a*L*L + b*L + c] = -1;
            }
            
            if (spin != meas->atoms[a*L*L + b*L + c]){
                float dE = -J * (float)spinNeighbours * (float)(meas->atoms[a*L*L + b*L + c] - spin);
                energyIter += dE; 
                magnetizationIter += (meas->atoms[a*L*L + b*L + c] - spin);
            }
        }
    }

    meas->magnetization[iterCounter] = magnetizationIter;
    meas->energy[iterCounter] = energyIter;
}

int main(int argc, char **argv){
    srand(time(NULL));
    // check the number of args
    if (argc != 2){
        return 1;
    }

    // load path to dir
    const char *dirPath = argv[1];

    // configure simulation
    struct SimConfig sim;
    load_config(&sim, dirPath);

    // measured quantities
    struct SimMeas meas; 
    meas.temps = (float *)malloc(sim.run_time * sizeof(float));
    meas.magnetization = (int64_t *)malloc(sim.run_time * sizeof(int64_t));
    meas.energy = (float *)malloc(sim.run_time * sizeof(float));
    uint64_t total_elements = (uint64_t)sim.L * sim.L * sim.L;
    meas.atoms = (int8_t *)malloc(total_elements * sizeof(int8_t));

    load_atoms(&sim, meas.atoms, dirPath);

    if (sim.init == WARM_UP){
        load_temps(&sim, meas.temps, dirPath);
        float startTemp = 6.0f;
        float targetTemp = meas.temps[0];
        float step = (startTemp-targetTemp)/(float)sim.run_time;
        for (uint64_t i=0;i<sim.run_time;i++){
            meas.temps[i] = startTemp + i*step;
            monteCarlo(&sim, &meas, i, false);
        }
        load_temps(&sim, meas.temps, dirPath);
        for (uint64_t i=0;i<sim.run_time;i++){
            monteCarlo(&sim, &meas, i, true);
            if (i%10==0){
                save_atoms(&sim, meas.atoms, dirPath);
            }
        }
    }
    else{
        load_temps(&sim, meas.temps, dirPath);
        for (uint64_t i=0;i<sim.run_time;i++){
            monteCarlo(&sim, &meas, i, false);
            if (i%10==0){
                save_atoms(&sim, meas.atoms, dirPath);
            }
        }
    }
    
    save_measurment(&sim, meas.magnetization, meas.energy, dirPath);

    free(meas.atoms);
    free(meas.temps);
    free(meas.magnetization);
    free(meas.energy);
    return 0;
}