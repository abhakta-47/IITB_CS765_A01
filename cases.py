from simulation import main
from config import Config, update_config

for z1 in range(0, 100, 10):
    for z2 in range(0, 100, 10):
        print("running for z1 %s z2 %s", z1, z2)
        CONFIG = Config()
        CONFIG.Z1 = z1 if z1 else 0.001
        CONFIG.Z2 = z2 if z2 else 0.001
        update_config(CONFIG)
        main()
        # break
