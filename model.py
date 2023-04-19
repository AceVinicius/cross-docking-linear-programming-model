import gurobipy as gp
import numpy as np
import instance

from typing import List, Dict


class CrossDockingModel:
    def __init__(self, instance_file):
        self.__instance_file = instance_file

        self.__data: dict = instance.read_data(self.__instance_file)

        self.__create_labels()
        self.__create_parameters(1)

        self.__model = gp.Model("cross-docking problem")

        self.__create_binary_variables()
        self.__create_continuous_variables()
        self.__create_restrictions()

    def __enter__(self):
        return CrossDockingModel

    def __exit__(self, exc_type, exc_val, exc_tb):
        gp.disposeDefaultEnv()

    def __create_labels(self) -> None:
        self.__products = self.__create_label("product", self.__data['number_of_products'])
        self.__suppliers = self.__create_label("supplier", self.__data['number_of_suppliers'])
        self.__inbound_docks = self.__create_label("inbound_dock", self.__data['inbound_docks'])
        self.__outbound_docks = self.__create_label("outbound_dock", self.__data['outbound_docks'])
        self.__customers = self.__create_label("customer", self.__data['number_of_customers'])
        self.__customers.insert(0, "c_inbound_dock")
        self.__customers.append("c_outbound_dock")

    def __create_parameters(self, time_unit: int) -> None:
        self.__PT = self.__create_dict_from_array(self.__data['processing_time_for_inbound_load'], self.__suppliers)
        self.__R = self.__create_dict_from_matrix(self.__data['number_of_each_product_into_inbound_loads'],
                                                  self.__products, self.__suppliers)
        self.__D = self.__create_dict_from_matrix(self.__data['quantity_of_required_products_per_customer'],
                                                  self.__products, self.__customers[1:-1])
        self.__Q = self.__create_dict_from_array(self.__data['quantity_of_required_pallets_per_customer'],
                                                 self.__customers[1:-1])
        self.__ST = self.__create_dict_from_array(self.__data['quantity_of_required_pallets_per_customer'] * 2,
                                                  self.__customers[1:-1])
        self.__TR = self.__create_dict_from_3d_matrix(self.__data['transfer_time_for_each_product'],
                                                      self.__products, self.__inbound_docks, self.__outbound_docks)
        self.__TT = self.__create_dict_from_matrix(self.__data['travel_time'], self.__customers, self.__customers)
        self.__CT = self.__create_dict_from_matrix(self.__data['travel_time'], self.__customers, self.__customers)
        self.__A = self.__create_dict_from_array(self.__data['time_window_start'], self.__customers)
        self.__B = self.__create_dict_from_array(self.__data['time_window_end'], self.__customers)

        # Not dynamic
        self.__CAP = self.__data['vehicle_capacity']
        self.__LT = self.__data['time_to_load_one_pallet']
        self.__CT_ = self.__data['changeover_time']
        self.__M = 1000
        self.__CO = 1
        self.__CE = 1
        self.__CL = 1
        self.__T_max = 400

    def __create_binary_variables(self):
        self.__z_in = self.__model.addVars(self.__suppliers, self.__inbound_docks, name="z_in", vtype=gp.GRB.BINARY)
        self.__z_out = self.__model.addVars(self.__customers, self.__outbound_docks, name="z_out", vtype=gp.GRB.BINARY)
        self.__w_in = self.__model.addVars(self.__suppliers, self.__suppliers, name="w_in", vtype=gp.GRB.BINARY)
        self.__w_out = self.__model.addVars(self.__customers, self.__customers, name="w_out", vtype=gp.GRB.BINARY)
        self.__y = self.__model.addVars(self.__suppliers, self.__customers, name="y", vtype=gp.GRB.BINARY)
        self.__x = self.__model.addVars(self.__customers, self.__customers, name="x", vtype=gp.GRB.BINARY)
        self.__v = self.__model.addVars(self.__customers, self.__customers, name="v", vtype=gp.GRB.BINARY)

    def __create_continuous_variables(self):
        self.__ut = self.__model.addVars(self.__suppliers, name="ut", vtype=gp.GRB.CONTINUOUS)
        self.__rt = self.__model.addVars(self.__customers, name="rt", vtype=gp.GRB.CONTINUOUS)
        self.__dt = self.__model.addVars(self.__customers, name="dt", vtype=gp.GRB.CONTINUOUS)
        self.__dt_max = self.__model.addVar(name="dt_max", vtype=gp.GRB.CONTINUOUS)
        self.__rho = self.__model.addVars(self.__products, self.__suppliers, self.__inbound_docks, self.__customers,
                                          self.__outbound_docks, name="rho",
                                          vtype=gp.GRB.CONTINUOUS)
        self.__t = self.__model.addVars(self.__customers, name="t", vtype=gp.GRB.CONTINUOUS)
        self.__t_np1 = self.__model.addVar(name="t_n-plus-1", vtype=gp.GRB.CONTINUOUS)
        self.__et = self.__model.addVars(self.__customers, name="et", vtype=gp.GRB.CONTINUOUS)
        self.__lt = self.__model.addVars(self.__customers, name="lt", vtype=gp.GRB.CONTINUOUS)

    def __create_restrictions(self):
        self.__insert_designation_and_sorting_of_inbound_loads(self.__model)
        self.__insert_designation_and_sorting_of_outbound_loads(self.__model)
        self.__insert_connections_between_loads_and_routes(self.__model)
        self.__insert_route_definitions(self.__model)

    def __insert_designation_and_sorting_of_inbound_loads(self, m):
        # Constraint 1: Each inbound load is assigned to one supplier
        m.addConstrs(
            (
                gp.quicksum(self.__z_in[_l, _f] for _f in self.__inbound_docks) == 1
                for _l in self.__suppliers
            ),
            name="assign_inbound_load"
        )

        # Constraint 2: Ensure that inbound loads are sorted correctly
        m.addConstrs(
            (
                self.__w_in[_l, _m] + self.__w_in[_m, _l] >= self.__z_in[_l, _f] + self.__z_in[_m, _f] - 1
                for _l in self.__suppliers
                for _m in self.__suppliers
                if _l < _m
                for _f in self.__inbound_docks
            ),
            name="sort_inbound_loads"
        )

        # Constraint 3: The unloading time of a supplier is greater than or equal to its processing time
        m.addConstrs(
            (
                self.__ut[_l] >= self.__PT[_l]
                for _l in self.__suppliers
            ),
            name="unloading_time_gt_processing_time"
        )

        # Constraint 4: Unloading time of a supplier is greater than or equal to the unloading time of the previous
        # supplier plus processing time
        m.addConstrs(
            (
                self.__ut[_m] >= self.__ut[_l] + self.__PT[_m] - self.__M * (1 - self.__w_in[_l, _m])
                for _l in self.__suppliers
                for _m in self.__suppliers
                if _l != _m
            ),
            name="unloading_time_order"
        )

    def __insert_designation_and_sorting_of_outbound_loads(self, m):
        m.addConstrs(
            (
                gp.quicksum(self.__z_out[_i, _h] for _h in self.__outbound_docks) == self.__x['c_inbound_dock', _i]
                for _i in self.__customers[1:-1]
            ),
            name="5"
        )

        m.addConstrs(
            (
                self.__w_out[_i, _j] + self.__w_out[_j, _i] >= self.__z_out[_i, _h] + self.__z_out[_j, _h] - 1
                for _i in self.__customers[1:-1]
                for _j in self.__customers[1:-1]
                if _i < _j
                for _h in self.__outbound_docks
            ),
            name="6"
        )

        m.addConstrs(
            (
                self.__dt_max >= self.__dt[_i]
                for _i in self.__customers[1:-1]
            ),
            name="7"
        )

        m.addConstrs(
            (
                self.__dt[_j] >= self.__dt[_i] + self.__CT_ + self.__LT * (
                        self.__Q[_j] * self.__x['c_inbound_dock', _j] + gp.quicksum(
                            (self.__Q[_n] * self.__v[_n, _j]) for _n in self.__customers[1:-1] if _i != _j)) - self.__M
                * (1 - self.__w_out[_i, _j])
                for _i in self.__customers[1:-1]
                for _j in self.__customers[1:-1]
                if _i != _j
            ),
            name="8"
        )

    def __insert_connections_between_loads_and_routes(self, m):
        m.addConstrs(
            (
                gp.quicksum(
                    self.__rho[_p, _l, _f, _i, _h] for _i in self.__customers[1:-1] for _h in self.__outbound_docks) ==
                self.__R[_p, _l] *
                self.__z_in[_l, _f]
                for _p in self.__products
                for _l in self.__suppliers
                for _f in self.__inbound_docks
            ),
            name="9"
        )

        m.addConstrs(
            (
                gp.quicksum(
                    self.__rho[_p, _l, _f, _i, _h] for _p in self.__products for _l in self.__suppliers for _f in
                    self.__inbound_docks) <= (
                    gp.quicksum(self.__R[_p, _l] for _p in self.__products for _l in self.__suppliers)) * self.__z_out[
                    _i, _h]
                for _i in self.__customers[1:-1]
                for _h in self.__outbound_docks
            ),
            name="10"
        )

        m.addConstrs(
            (
                gp.quicksum(
                    self.__rho[_p, _l, _f, _i, _h] for _p in self.__products for _f in self.__inbound_docks for _h in
                    self.__outbound_docks) <= (
                    gp.quicksum(self.__R[_p, _l] for _p in self.__products)) * self.__y[_l, _i]
                for _l in self.__suppliers
                for _i in self.__customers[1:-1]
            ),
            name="11"
        )

        m.addConstrs(
            (
                self.__rt[_i] >= self.__ut[_l] + gp.quicksum(
                    self.__TR[_p, _f, _h] * self.__rho[_p, _l, _f, _i, _h] for _p in self.__products for _f in
                    self.__inbound_docks for _h in
                    self.__outbound_docks) - self.__M * (1 - self.__y[_l, _i])
                for _l in self.__suppliers
                for _i in self.__customers[1:-1]
            ),
            name="12"
        )

        m.addConstrs(
            (
                self.__t[_i] >= self.__dt[_i] + self.__TT['c_inbound_dock', _i] - self.__M * (
                        1 - self.__x['c_inbound_dock', _i])
                for _i in self.__customers[1:-1]
            ),
            name="13"
        )

        m.addConstrs(
            (
                gp.quicksum(
                    self.__rho[_p, _l, _f, _i, _h] for _l in self.__suppliers for _f in self.__inbound_docks for _h in
                    self.__outbound_docks) == self.__D[
                    _p, _i] * self.__x['c_inbound_dock', _i] + gp.quicksum(
                    self.__D[_p, _j] * self.__v[_j, _i] for _j in self.__customers[1:-1] if _j != _i)
                for _p in self.__products
                for _i in self.__customers[1:-1]
            ),
            name="14"
        )

        m.addConstrs(
            (
                self.__dt[_i] >= self.__rt[_i] + self.__LT * (
                    self.__Q[_i] * self.__x["c_inbound_dock", _i] + gp.quicksum(
                        self.__Q[_j] * self.__v[_j, _i] for _j in self.__customers[1:-1] if _j != _i)) - self.__M *
                (1 - self.__x["c_inbound_dock", _i])
                for _i in self.__customers[1:-1]
            ),
            name="15"
        )

    def __insert_route_definitions(self, m):
        m.addConstrs(
            (
                gp.quicksum(self.__x[_i, _j] for _i in self.__customers[:-1] if _i != _j) == 1
                for _j in self.__customers[1:-1]
            ),
            name="16"
        )

        m.addConstrs(
            (
                gp.quicksum(self.__x[_i, _j] for _j in self.__customers[1:] if _i != _j) == 1
                for _i in self.__customers[1:-1]
            ),
            name="17"
        )

        m.addConstrs(
            (
                self.__v[_i, _j] >= self.__x["c_inbound_dock", _j] - (1 - self.__x[_j, _i])
                for _i in self.__customers[1:-1]
                for _j in self.__customers[1:-1]
                if _i != _j
            ),
            name="18"
        )

        m.addConstrs(
            (
                self.__v[_i, _j] >= self.__v[_n, _j] - (1 - self.__x[_i, _n])
                for _i in self.__customers[1:-1]
                for _j in self.__customers[1:-1]
                for _n in self.__customers[1:-1]
                if _i != _j
                if _i != _n
                if _j != _n
            ),
            name="19"
        )

        m.addConstrs(
            (
                gp.quicksum(self.__v[_i, _j] for _j in self.__customers[1:-1] if _j != _i) + self.__x[
                    "c_inbound_dock", _i] == 1
                for _i in self.__customers[1:-1]
            ),
            name="20"
        )

        m.addConstrs(
            (
                gp.quicksum(self.__Q[_i] * self.__v[_i, _j] for _i in self.__customers[1:-1] if _i != _j) + self.__Q[
                    _j] * self.__x[
                    "c_inbound_dock", _j] <= self.__CAP * self.__x["c_inbound_dock", _j]
                for _j in self.__customers[1:-1]
            ),
            name="21"
        )

        m.addConstrs(
            (
                self.__t[_j] >= self.__t[_i] + self.__ST[_i] + self.__TT[_i, _j] - self.__M * (1 - self.__x[_i, _j])
                for _i in self.__customers[1:-1]
                for _j in self.__customers[1:]
                if _i != _j
            ),
            name="22"
        )

        m.addConstrs(
            (
                self.__A[_i] - self.__et[_i] <= self.__t[_i]
                for _i in self.__customers[1:-1]
            ),
            name="23-1"
        )

        m.addConstrs(
            (
                self.__t[_i] <= self.__B[_i] + self.__lt[_i]
                for _i in self.__customers[1:-1]
            ),
            name="23-2"
        )

        m.addConstr(self.__t_np1 <= self.__T_max, name="24")

    def __get_objective_functions(self):
        objective_1 = gp.quicksum(
            self.__CT[_i, _j] * self.__x[_i, _j] for _i in self.__customers[:-1] for _j in self.__customers[1:] if
            _i != _j) + gp.quicksum(
            self.__CE * self.__et[_i] for _i in self.__customers[1:-1]) + gp.quicksum(
            self.__CL * self.__lt[_i] for _i in self.__customers[1:-1]) + self.__CO * self.__dt_max

        objective_2 = gp.quicksum((self.__CAP * self.__x["c_inbound_dock", _j] - (
                gp.quicksum(self.__Q[_i] * self.__v[_i, _j] for _i in self.__customers[1:-1] if _i != _j) +
                self.__Q[_j] * self.__x[
                    "c_inbound_dock", _j])) / self.__CAP for _j in self.__customers[1:-1])

        return objective_1, objective_2

    def solve_single_objective(self):
        expr_1, expr_2 = self.__get_objective_functions()
        self.__model.setObjective(expr_1, sense=gp.GRB.MINIMIZE)

        self.__solve()

    def solve_bi_objective(self):
        expr_1, expr_2 = self.__get_objective_functions()

    def solve_weighted_sum_objective(self, alpha):
        expr_1, expr_2 = self.__get_objective_functions()

        self.solve_single_objective()

        mi = 0.1 * self.__model.obj

        self.__model.setObjective((1 - alpha) * expr_1 + alpha * mi * expr_2, sense=gp.GRB.MINIMIZE)

        self.__solve()

    def solve_restricted_epsilon_objective(self):
        expr_1, expr_2 = self.__get_objective_functions()

        self.__solve()

    def __solve(self):
        self.__model.optimize()

    @staticmethod
    def __create_label(label: str, size: int) -> List:
        """
        Returns a list of labels of a specified size, generated by concatenating the given string with a numerical index.

        Args:
            label: A string to be concatenated with a numerical index.
            size: The size of the resulting list of labels.

        Returns:
            A list of labels, generated by concatenating the given string with a numerical index.
        """
        return [f"{label}_{i}" for i in range(1, size + 1)]

    @staticmethod
    def __create_dict_from_array(array: np.ndarray, label: List) -> Dict:
        """
        Given a numpy array and corresponding labels, returns a dictionary
        mapping each label to its corresponding array value.

        Args:
            array (np.ndarray): A numpy array.
            label (List): A list of labels for the array.

        Returns:
            Dict: A dictionary mapping each label to its corresponding array value.

        Raises:
            ValueError: If the length of the label list does not match the shape of the array.
        """
        if len(label) != array.shape[0]:
            raise ValueError("Length of label list does not match shape of array")

        data = {}

        for index, value in enumerate(array):
            data[label[index]] = value

        return data

    @staticmethod
    def __create_dict_from_matrix(matrix: np.ndarray, label_i: List, label_j: List) -> Dict:
        """
        Create a dictionary from a 2D numpy array and two lists of row and column labels.

        Args:
            matrix (np.ndarray): A 2D numpy array.
            label_i (List): A list of row labels.
            label_j (List): A list of column labels.

        Returns:
            Dict: A dictionary where keys are tuples of row and column labels, and values are the corresponding values
                  in the matrix.

        Raises:
            ValueError: If the length of the label lists do not match the shape of the matrix.
        """
        if len(label_i) != matrix.shape[0] or len(label_j) != matrix.shape[1]:
            raise ValueError("Length of label lists does not match shape of matrix")

        data = {}

        for i, label1 in enumerate(label_i):
            for j, label2 in enumerate(label_j):
                data[label1, label2] = matrix[i, j]

        return data

    @staticmethod
    def __create_dict_from_3d_matrix(matrix: np.ndarray, label_i: List, label_j: List, label_k: List) -> Dict:
        """
        Given a 3D matrix and corresponding labels, returns a dictionary
        mapping each label triple to its corresponding matrix value.

        Args:
            matrix (np.ndarray): A 3D numpy array.
            label_i (List): A list of labels for the first dimension of the matrix.
            label_j (List): A list of labels for the second dimension of the matrix.
            label_k (List): A list of labels for the third dimension of the matrix.

        Returns:
            Dict: A dictionary mapping each label triple to its corresponding matrix value.

        Raises:
            ValueError: If the length of the label lists do not match the shape of the matrix.
        """
        if len(label_i) != matrix.shape[0] or len(label_j) != matrix.shape[1] or len(label_k) != matrix.shape[2]:
            raise ValueError("Length of label lists does not match shape of matrix")

        data = {}

        for i, label1 in enumerate(label_i):
            for j, label2 in enumerate(label_j):
                for k, label3 in enumerate(label_k):
                    data[label1, label2, label3] = matrix[i, j, k]

        return data
