import gurobipy as gp
import numpy as np
import instance
import sys

from typing import Any


def solve_cross_docking_model(instance_file: str) -> None:
    data: dict = instance.read_data(instance_file)

    # Indexes
    l: int = data['number_of_suppliers']
    m: int = data['number_of_suppliers']

    p: int = data['number_of_products']

    i: int = data['number_of_customers'] + 2
    j: int = data['number_of_customers'] + 2
    n: int = data['number_of_customers'] + 2

    f: int = data['inbound_docks']

    h: int = data['outbound_docks']

    # Parameters

    # Not dynamic
    time_unit: int = 1

    PT: np.ndarray[Any, np.dtype[int]] = data['processing_time_for_inbound_load']

    R: np.ndarray[Any, np.dtype[int]] = data['number_of_each_product_into_inbound_loads']

    TR: np.ndarray[Any, np.dtype[float]] = -1

    # Not dynamic
    LT: int = 2 * time_unit

    # Not dynamic
    CT: int = 2 * time_unit

    CAP: int = data['vehicle_capacity']

    D: np.ndarray[Any, np.dtype[int]] = data['quantity_of_required_products_per_customer']

    Q: np.ndarray[Any, np.dtype[int]] = data['quantity_of_required_pallets_per_customer']

    # Not dynamic
    CO: int = 1

    TT: np.ndarray[Any, np.dtype[float]] = data['travel_time']

    CT_: np.ndarray[Any, np.dtype[float]] = data['travel_time']

    # Not dynamic
    CE: int = 1

    # Not dynamic
    CL: int = 1

    ST: np.ndarray[Any, np.dtype[float]] = -1

    A: np.ndarray[Any, np.dtype[int]] = data['time_window_start']
    B: np.ndarray[Any, np.dtype[int]] = data['time_window_end']

    T_max: int = B.max() + 10

    # Not dynamic
    M: int = 100

    try:
        # Create model with a context manager. Upon exit from this block,
        # model.dispose is called automatically, and memory consumed by the model
        # is released.
        #
        # The model is created in the default environment, which will be created
        # automatically upon model construction.  For safe release of resources
        # tied to the default environment, disposeDefaultEnv is called below.
        with gp.Model("cross-docking problem") as model:
            z_in = model.addVars(l, f, name="z_in", vtype=gp.GRB.BINARY)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))
    except AttributeError as e:
        print('Encountered an attribute error: ' + str(e))
    finally:
        # Safely release memory and/or server side resources consumed by
        # the default environment.
        gp.disposeDefaultEnv()
