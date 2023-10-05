#!/usr/bin/python3 python3.11

import argparse
import os
from pathlib import Path

from cross_docking_model import (
    instance as Instance,
    CrossDockingSolver as Model
)


def main(args):
    for instance in args.instances:
        data = Instance.read_data(instance)

        for mode in args.mode:
            if mode == 'wsm':
                for alpha in args.alpha:
                    output = f'{args.output_dir}/{mode}/alpha/{alpha}/{instance}'

                    model = Model.CrossDockingSolver(
                        data=data,
                        mode=mode,
                        alpha=alpha,
                        time_limit=args.time_limit,
                        time_unit=args.time_unit
                    )

                    model.solve()
                    model.print_solution()
                    model.clear()

                    write_instance_to_file(output)

            elif mode == 'r-e':
                for epsilon in args.epsilon:
                    output = f'{args.output_dir}/{mode}/epsilon/{epsilon}'

                    model = Model.CrossDockingSolver(
                        data=data,
                        mode=mode,
                        epsilon=epsilon,
                        time_limit=args.time_limit,
                        time_unit=args.time_unit
                    )

                    model.solve()
                    model.print_solution()
                    model.clear()

                    write_instance_to_file(output)

            else:
                output = f'{args.output_dir}/{mode}'

                model = Model.CrossDockingSolver(
                    data=data,
                    mode=mode,
                    time_limit=args.time_limit,
                    time_unit=args.time_unit
                )

                model.solve()
                model.print_solution()
                model.clear()

                write_instance_to_file(output)


def write_instance_to_file(filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(log_file_path, 'r') as log_file:
        with open(filename, 'w') as output_file:
            for line in log_file:
                output_file.write(line)

    try:
        os.remove(log_file_path)
    except OSError:
        pass


def get_cli_args():
    parser = argparse.ArgumentParser(
        prog='Cross Docking Linear Model',
        description='Optimize a specific instance of cross-docking',
        epilog='And that\'s how you\'d foo a bar'
    )

    parser.add_argument(
        '-t',
        '--time-limit',
        default=float('+Inf'),
        type=float,
        help='Max amount of time an instance can run in seconds'
    )
    parser.add_argument(
        '-u',
        '--time-unit',
        default=1,
        type=int,
        help='Time unit value'
    )
    parser.add_argument(
        '-o',
        '--output-dir',
        default='solution',
        type=str,
        help='Output directory of the solution'
    )
    parser.add_argument(
        '-m',
        '--mode',
        choices=['single', 'multi', 'wsm', 'r-e'],
        default=['single'],
        nargs='*',
        type=str,
        help='Select the desired solution method'
    )
    parser.add_argument(
        '-a',
        '--alpha',
        default=[0.5],
        nargs='*',
        type=float,
        help='When \'wsm\' mode is selected, it will balance how much we prioritize one objective function over another'
    )
    parser.add_argument(
        '-e',
        '--epsilon',
        default=[0.5],
        nargs='*',
        type=float,
        help='When \'r-e\' mode is selected, it will adjust the gap on the objective function result when it turns into a restriction'
    )
    parser.add_argument(
        'instances',
        nargs='+',
        type=str,
        help='Instances to optimize'
    )

    return parser.parse_args()


log_file_path: str = 'grbtune.log'


if __name__ == '__main__':
    try:
        os.remove(log_file_path)
    except OSError:
        pass

    args = get_cli_args()
    main(args)
