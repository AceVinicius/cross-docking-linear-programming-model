#!/usr/bin/python3 python3.9

import sys
import model


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(f"usage: {sys.argv[0]} [...instances]")
    else:
        for i, instance in enumerate(sys.argv):
            if i == 0:
                continue

            print(f"\n\n------------------------------( Instance {i} )------------------------------\n")

            m = model.CrossDockingModel(instance)
            m.solve_single_objective()
