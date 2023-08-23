#!/usr/bin/python3 python3.11

import sys

from cross_docking_model import instance, CrossDockingSolver


def main():
    if len(sys.argv) == 1:
        print(f"usage: {sys.argv[0]} [...instances]")
    else:
        for i, filename in enumerate(sys.argv):
            if i == 0:
                continue

            print(f"\n\n------------------------------( Instance {i} )------------------------------\n")

            data = instance.read_data(filename)
            m = CrossDockingSolver.CrossDockingSolver(data, mode="single", log="solution/50clientes")
            m.solve()
            m.clear()


if __name__ == '__main__':
    main()