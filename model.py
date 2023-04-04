import gurobipy as gp
import numpy as np
import instance

from typing import Any


def solve_cross_docking_model(instance_file: str) -> None:
    def _create_label(label: str, size: int) -> list:
        return [f"{label}_{_i + 1}" for _i in range(size)]

    def _create_dict_from_array(array: np.ndarray[Any, np.dtype[int or float]], label: list) -> dict:
        _data: dict = dict()

        for _index, _value in enumerate(array):
            _data[label[_index]] = _value

        return _data
    
    def _create_dict_from_matrix(matrix: np.ndarray[Any, np.dtype[int or float]], label_i: list, label_j: list) -> dict:
        _data: dict = dict()

        for _i in range(matrix.shape[0]):
            for _j in range(matrix.shape[1]):
                _data[label_i[_i], label_j[_j]] = matrix[_i][_j]
        
        return _data

    def _create_dict_from_3d_matrix(matrix: np.ndarray[Any, np.dtype[int or float]], label_i: list, label_j: list, label_k: list) -> dict:
        _data: dict = dict()

        for _i in range(matrix.shape[0]):
            for _j in range(matrix.shape[1]):
                for _k in range(matrix.shape[2]):
                    _data[label_i[_i], label_j[_j], label_k[_k]] = matrix[_i][_j][_k]

        return _data

    data: dict = instance.read_data(instance_file)

    # Labels
    suppliers: list = _create_label("supplier", data['number_of_suppliers'])

    products: list = _create_label("product", data['number_of_products'])

    customers: list = _create_label("customer", data['number_of_customers'])
    customers.insert(0, "inbound_dock")
    customers.append("outbound_dock")

    inbound_docks: list = _create_label("inbound_dock", data['inbound_docks'])

    outbound_docks: list = _create_label("outbound_dock", data['outbound_docks'])

    # Parameters

    # Not dynamic
    time_unit: int = 1

    PT: dict = _create_dict_from_array(data['processing_time_for_inbound_load'], suppliers)

    R: dict = _create_dict_from_matrix(data['number_of_each_product_into_inbound_loads'], products, suppliers)

    # Not dynamic
    TR: dict = _create_dict_from_3d_matrix(np.ones(shape=(len(inbound_docks), len(outbound_docks), len(products)), dtype=float), inbound_docks, outbound_docks, products)

    # Not dynamic
    LT: int = 2 * time_unit

    # Not dynamic
    CT_: int = 2 * time_unit

    CAP: int = data['vehicle_capacity']

    D: dict = _create_dict_from_matrix(data['quantity_of_required_products_per_customer'], products, customers)

    Q: dict = _create_dict_from_array(data['quantity_of_required_pallets_per_customer'], customers)

    # Not dynamic
    CO: int = 1

    TT: dict = _create_dict_from_matrix(data['travel_time'], customers, customers)

    CT: dict = _create_dict_from_matrix(data['travel_time'], customers, customers)

    # Not dynamic
    CE: int = 1

    # Not dynamic
    CL: int = 1

    # Not dynamic
    ST: dict = _create_dict_from_array(np.ones(shape=len(customers), dtype=float), customers)

    A: dict = _create_dict_from_array(data['time_window_start'], _create_label("start", len(customers)))
    B: dict = _create_dict_from_array(data['time_window_end'], _create_label("end", len(customers)))

    T_max: int = 400 * time_unit

    # Not dynamic
    M: int = 100

    try:
        with gp.Model("cross-docking problem") as model:
            z_in = model.addVars(suppliers, inbound_docks, name="z_in", vtype=gp.GRB.BINARY)

            z_out = model.addVars(customers, outbound_docks, name="z_out", vtype=gp.GRB.BINARY)

            w_in = model.addVars(suppliers, suppliers, name="w_in", vtype=gp.GRB.BINARY)

            w_out = model.addVars(customers, customers, name="w_out", vtype=gp.GRB.BINARY)

            y = model.addVars(suppliers, customers, name="y", vtype=gp.GRB.BINARY)

            x = model.addVars(customers, customers, name="x", vtype=gp.GRB.BINARY)

            v = model.addVars(customers, customers, name="v", vtype=gp.GRB.BINARY)

            ut = model.addVars(suppliers, name="ut", vtype=gp.GRB.CONTINUOUS)

            rt = model.addVars(customers, name="rt", vtype=gp.GRB.CONTINUOUS)

            dt = model.addVars(customers, name="dt", vtype=gp.GRB.CONTINUOUS)

            dt_max = model.addVar(1, name="dt_max", vtype=gp.GRB.CONTINUOUS)

            rho = model.addVars(products, suppliers, inbound_docks, customers, outbound_docks, name="rho", vtype=gp.GRB.CONTINUOUS)

            t = model.addVars(customers, name="i", vtype=gp.GRB.CONTINUOUS)

            t_np1 = model.addVar(1, name="t_N+1", vtype=gp.GRB.CONTINUOUS)

            et = model.addVars(customers, name="et", vtype=gp.GRB.CONTINUOUS)

            lt = model.addVars(customers, name="lt", vtype=gp.GRB.CONTINUOUS)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))
    except AttributeError as e:
        print('Encountered an attribute error: ' + str(e))
    finally:
        gp.disposeDefaultEnv()
