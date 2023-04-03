#!/usr/bin/python3 python3.9

import sys
import model


if __name__ == '__main__':
    for i, instance in enumerate(sys.argv):
        if i == 0:
            continue

        print(f"\n\n---------------( Instance {i} )---------------\n")
        model.solve_cross_docking_model(instance)
