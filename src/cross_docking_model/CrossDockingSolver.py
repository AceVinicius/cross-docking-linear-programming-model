from typing import List, Dict

import gurobipy as gp

from cross_docking_model.__conversions import create_label, create_dict_from_array, create_dict_from_2d_matrix, \
    create_dict_from_3d_matrix


class CrossDockingSolver:
    __modes: List = ["single", "multi", "msp", "r-e"]

    mode: str


    def __init__(self, data: Dict, mode: str, time_limit: float, time_unit: int, output: str, alpha: float = 0.5, epsilon: float = 0.5):
        if time_unit <= 0:
            raise ValueError("time_unit must be an integer greater than 0: " + str(time_unit))

        if mode not in self.__modes:
            raise ValueError("mode does not exist: " + mode)

        if alpha < 0 or alpha > 1:
            raise ValueError("alpha must be a float between 0.0 and 1.0:" + str(alpha))

        if epsilon < 0:
            raise ValueError("epsilon must a float greater than 0: " + str(epsilon))

        self.mode = mode

        self.__setup_solver(data, time_limit, output)
        self.__build_model(data, time_unit, alpha, epsilon)


    def __setup_solver(self, data: Dict, time_limit: float, output: str):
        self.model = gp.Model("Cross-Docking Model - " + self.mode)

        self.model.Params.TimeLimit = time_limit
        self.model.Params.LogFile = output + "/" + data["instance"] + ".txt"
        self.model.Params.LogToConsole = 0


    def __build_model(self, data: Dict, time_unit: int, alpha: float, epsilon: float):
        # Create labels
        products = create_label("product", data['number_of_products'])
        suppliers = create_label("supplier", data['number_of_suppliers'])
        inbound_docks = create_label("inbound_dock", data['inbound_docks'])
        outbound_docks = create_label("outbound_dock", data['outbound_docks'])
        customers = create_label("customer", data['number_of_customers'])
        customers.insert(0, "c_inbound_dock")
        customers.append("c_outbound_dock")

        # Create parameters
        PT = create_dict_from_array(data['processing_time_for_inbound_load'], suppliers)
        R = create_dict_from_2d_matrix(data['number_of_each_product_into_inbound_loads'], products, suppliers)
        D = create_dict_from_2d_matrix(data['quantity_of_required_products_per_customer'], products,
                                       customers[1:-1])
        Q = create_dict_from_array(data['quantity_of_required_pallets_per_customer'], customers[1:-1])
        ST = create_dict_from_array(data['quantity_of_required_pallets_per_customer'] * 2, customers[1:-1])
        TR = create_dict_from_3d_matrix(data['transfer_time_for_each_product'], products, inbound_docks,
                                        outbound_docks)
        TT = create_dict_from_2d_matrix(data['travel_time'], customers, customers)
        CT = create_dict_from_2d_matrix(data['travel_time'], customers, customers)
        A = create_dict_from_array(data['time_window_start'], customers)
        B = create_dict_from_array(data['time_window_end'], customers)

        CAP = data['vehicle_capacity']
        LT = data['time_to_load_one_pallet']
        CT_ = data['changeover_time']

        M = 1000
        CO = time_unit
        CE = time_unit
        CL = time_unit
        T_max = 400

        # Create variables
        z_in = self.model.addVars(suppliers, inbound_docks, name="z_in", vtype=gp.GRB.BINARY)
        z_out = self.model.addVars(customers, outbound_docks, name="z_out", vtype=gp.GRB.BINARY)
        w_in = self.model.addVars(suppliers, suppliers, name="w_in", vtype=gp.GRB.BINARY)
        w_out = self.model.addVars(customers, customers, name="w_out", vtype=gp.GRB.BINARY)
        y = self.model.addVars(suppliers, customers, name="y", vtype=gp.GRB.BINARY)
        x = self.model.addVars(customers, customers, name="x", vtype=gp.GRB.BINARY)
        v = self.model.addVars(customers, customers, name="v", vtype=gp.GRB.BINARY)

        ut = self.model.addVars(suppliers, name="ut", vtype=gp.GRB.CONTINUOUS)
        rt = self.model.addVars(customers, name="rt", vtype=gp.GRB.CONTINUOUS)
        dt = self.model.addVars(customers, name="dt", vtype=gp.GRB.CONTINUOUS)
        dt_max = self.model.addVar(name="dt_max", vtype=gp.GRB.CONTINUOUS)
        rho = self.model.addVars(products, suppliers, inbound_docks, customers, outbound_docks, name="rho",
                                 vtype=gp.GRB.CONTINUOUS)
        t = self.model.addVars(customers, name="t", vtype=gp.GRB.CONTINUOUS)
        t_np1 = self.model.addVar(name="t_n-plus-1", vtype=gp.GRB.CONTINUOUS)
        et = self.model.addVars(customers, name="et", vtype=gp.GRB.CONTINUOUS)
        lt = self.model.addVars(customers, name="lt", vtype=gp.GRB.CONTINUOUS)

        # Add constraints
        # Constraint 1: Each inbound load is assigned to one supplier
        self.model.addConstrs(
            (
                gp.quicksum(z_in[l, f] for f in inbound_docks) == 1
                for l in suppliers
            ),
            name="assign_inbound_load"
        )

        # Constraint 2: Ensure that inbound loads are sorted correctly
        self.model.addConstrs(
            (
                w_in[l, m] + w_in[m, l] >= z_in[l, f] + z_in[m, f] - 1
                for l in suppliers
                for m in suppliers
                if l < m
                for f in inbound_docks
            ),
            name="sort_inbound_loads"
        )

        # Constraint 3: The unloading time of a supplier is greater than or equal to its processing time
        self.model.addConstrs(
            (
                ut[l] >= PT[l]
                for l in suppliers
            ),
            name="unloading_time_gt_processing_time"
        )

        # Constraint 4: Unloading time of a supplier is greater than or equal to the unloading time of the previous
        # supplier plus processing time
        self.model.addConstrs(
            (
                ut[m] >= ut[l] + PT[m] - M * (1 - w_in[l, m])
                for l in suppliers
                for m in suppliers
                if l != m
            ),
            name="unloading_time_order"
        )

        #     ==========================
        self.model.addConstrs(
            (
                gp.quicksum(z_out[i, h] for h in outbound_docks) == x['c_inbound_dock', i]
                for i in customers[1:-1]
            ),
            name="5"
        )

        self.model.addConstrs(
            (
                w_out[i, j] + w_out[j, i] >= z_out[i, h] + z_out[j, h] - 1
                for i in customers[1:-1]
                for j in customers[1:-1]
                if i < j
                for h in outbound_docks
            ),
            name="6"
        )

        self.model.addConstrs(
            (
                dt_max >= dt[i]
                for i in customers[1:-1]
            ),
            name="7"
        )

        self.model.addConstrs(
            (
                dt[j]
                >=
                dt[i] + CT_ + LT * (
                        Q[j] * x['c_inbound_dock', j] + gp.quicksum(Q[n] * v[n, j] for n in customers[1:-1] if i != j)
                ) - M * (1 - w_out[i, j])
                for i in customers[1:-1]
                for j in customers[1:-1]
                if i != j
            ),
            name="8"
        )

        #     ==========================
        self.model.addConstrs(
            (
                gp.quicksum(rho[p, l, f, i, h] for i in customers[1:-1] for h in outbound_docks)
                ==
                R[p, l] * z_in[l, f]
                for p in products
                for l in suppliers
                for f in inbound_docks
            ),
            name="9"
        )

        self.model.addConstrs(
            (
                gp.quicksum(rho[p, l, f, i, h] for p in products for l in suppliers for f in inbound_docks)
                <=
                gp.quicksum(R[p, l] for p in products for l in suppliers) * z_out[i, h]
                for i in customers[1:-1]
                for h in outbound_docks
            ),
            name="10"
        )

        self.model.addConstrs(
            (
                gp.quicksum(rho[p, l, f, i, h] for p in products for f in inbound_docks for h in outbound_docks)
                <=
                gp.quicksum(R[p, l] for p in products) * y[l, i]
                for l in suppliers
                for i in customers[1:-1]
            ),
            name="11"
        )

        self.model.addConstrs(
            (
                rt[i]
                >=
                ut[l] + gp.quicksum(
                    TR[p, f, h] * rho[p, l, f, i, h] for p in products for f in inbound_docks for h in outbound_docks
                ) - M * (1 - y[l, i])
                for l in suppliers
                for i in customers[1:-1]
            ),
            name="12"
        )

        self.model.addConstrs(
            (
                t[i] >= dt[i] + TT['c_inbound_dock', i] - M * (1 - x['c_inbound_dock', i])
                for i in customers[1:-1]
            ),
            name="13"
        )

        self.model.addConstrs(
            (
                gp.quicksum(rho[p, l, f, i, h] for l in suppliers for f in inbound_docks for h in outbound_docks)
                ==
                D[p, i] * x['c_inbound_dock', i] + gp.quicksum(D[p, j] * v[j, i] for j in customers[1:-1] if j != i)
                for p in products
                for i in customers[1:-1]
            ),
            name="14"
        )

        self.model.addConstrs(
            (
                dt[i]
                >=
                rt[i] + LT * (
                        Q[i] * x["c_inbound_dock", i] + gp.quicksum(Q[j] * v[j, i] for j in customers[1:-1] if j != i)
                ) - M * (1 - x["c_inbound_dock", i])
                for i in customers[1:-1]
            ),
            name="15"
        )

        self.model.addConstrs(
            (
                gp.quicksum(x[i, j] for i in customers[:-1] if i != j) == 1
                for j in customers[1:-1]
            ),
            name="16"
        )

        self.model.addConstrs(
            (
                gp.quicksum(x[i, j] for j in customers[1:] if i != j) == 1
                for i in customers[1:-1]
            ),
            name="17"
        )

        self.model.addConstrs(
            (
                v[i, j] >= x["c_inbound_dock", j] - (1 - x[j, i])
                for i in customers[1:-1]
                for j in customers[1:-1]
                if i != j
            ),
            name="18"
        )

        self.model.addConstrs(
            (
                v[i, j] >= v[n, j] - (1 - x[i, n])
                for i in customers[1:-1]
                for j in customers[1:-1]
                for n in customers[1:-1]
                if i != j
                if i != n
                if j != n
            ),
            name="19"
        )

        self.model.addConstrs(
            (
                gp.quicksum(v[i, j] for j in customers[1:-1] if j != i) + x["c_inbound_dock", i] == 1
                for i in customers[1:-1]
            ),
            name="20"
        )

        self.model.addConstrs(
            (
                gp.quicksum(Q[i] * v[i, j] for i in customers[1:-1] if i != j) + Q[j] * x["c_inbound_dock", j]
                <=
                CAP * x["c_inbound_dock", j]
                for j in customers[1:-1]
            ),
            name="21"
        )

        self.model.addConstrs(
            (
                t[j] >= t[i] + ST[i] + TT[i, j] - M * (1 - x[i, j])
                for i in customers[1:-1]
                for j in customers[1:]
                if i != j
            ),
            name="22"
        )

        self.model.addConstrs(
            (
                A[i] - et[i] <= t[i]
                for i in customers[1:-1]
            ),
            name="23-1"
        )

        self.model.addConstrs(
            (
                t[i] <= B[i] + lt[i]
                for i in customers[1:-1]
            ),
            name="23-2"
        )

        self.model.addConstr(t_np1 <= T_max, name="24")


        # Set objective
        oc = gp.quicksum(CT[i, j] * x[i, j] for i in customers[:-1] for j in customers[1:] if i != j) + gp.quicksum(
            CE * et[i] for i in customers[1:-1]) + gp.quicksum(CL * lt[i] for i in customers[1:-1]) + CO * dt_max
        nv = gp.quicksum((CAP * x["c_inbound_dock", j] - gp.quicksum(
            Q[i] * v[i, j] for i in customers[1:-1] if i != j) + Q[j] * x["c_inbound_dock", j]) / CAP for j in
                            customers[1:-1])

        if self.mode == 'single':
            self.model.setObjective(oc, gp.GRB.MINIMIZE)

        elif self.mode == 'multi':
            self.model.ModelSense = gp.GRB.MINIMIZE

            self.model.setObjectiveN(oc, index=0, priority=1, name="CO")
            self.model.setObjectiveN(nv, index=1, priority=1, name="NV")

        elif self.mode == 'wsm':
            self.model.ModelSense = gp.GRB.MINIMIZE

            oc_best = 1  # solve for alpha = 1
            nv_best = 1  # solve for alpha = 0

            self.model.setObjectiveN(oc / oc_best, index=0, weight=(1 - alpha), priority=1, name="CO")
            self.model.setObjectiveN(nv / nv_best, index=1, weight=(alpha)    , priority=1, name="NV")

        elif self.mode == 'r-e':
            self.model.setObjective(oc, gp.GRB.MINIMIZE, name="CO")
            self.model.addConstr(oc <= 0 + epsilon, name="25")
            self.model.setObjective(nv, gp.GRB.MINIMIZE, name="NV")


    def solve(self) -> None:
        self.model.optimize()

        # Print solution
        if self.model.status == gp.GRB.OPTIMAL:
            print(f"Optimal objective value(s):")
            if self.mode == 'single':
                print(f"Objective 1: {self.model.objVal:.4f}")

            elif self.mode == 'multi':
                print(f"Objective 1: {self.model.getObjective(0).getValue():.4f}")
                print(f"Objective 2: {self.model.getObjective(1).getValue():.4f}")

            for v in self.model.getVars():
                print(f"{v.varName}: {v.x:.4f}")

        else:
            print("Optimization terminated with status " + str(self.model.status))


    def clear(self) -> None:
        self.model.dispose()