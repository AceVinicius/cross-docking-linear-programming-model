import numpy as np

from typing import Any


def read_data(filename: str) -> dict:
    def _skip_first_line(_file) -> None:
        _file.readline()  # title

    def _go_to_next_info(_file) -> None:
        _file.readline()  # empty line
        _file.readline()  # title

    def _read_line_as_string(_file) -> str:
        return _file.readline().strip()

    def _read_line_as_int(_file) -> int:
        _line: str = _read_line_as_string(_file)

        if not _line.isdecimal():
            raise ValueError("read_data_from_instance: input data is not an integer: %s" % _line)

        return int(_line)

    def _read_line_as_float(_file) -> float:
        _line: str = _read_line_as_string(_file)

        if not _line.replace('.', '', 1).isdecimal():
            raise ValueError("read_data_from_instance: input data is not a float: %s" % _line)

        return float(_line)

    def _read_line_as_list(_file) -> list[str]:
        return _read_line_as_string(_file).split()

    def _read_line_as_int_array(_file) -> np.ndarray[Any, np.dtype[int]]:
        _data: list[int] = list(map(int, _read_line_as_list(_file)))

        return np.array(_data, dtype=int)

    def _read_line_as_float_array(_file) -> np.ndarray[Any, np.dtype[float]]:
        _data: list[float] = list(map(float, _read_line_as_list(_file)))

        return np.array(_data, dtype=float)
    
    def _read_lines_as_int_matrix(_file, _i: int, _j: int) -> np.ndarray[Any, np.dtype[int]]:
        _matrix: np.ndarray[Any, np.dtype[int]] = np.empty((_i, _j), dtype=int)

        for _index in range(_i):
            _matrix[_index]: np.ndarray[Any, np.dtype[int]] = _read_line_as_int_array(_file)

        return _matrix

    def _read_lines_as_float_matrix(_file, _i: int, _j: int) -> np.ndarray[Any, np.dtype[float]]:
        _matrix: np.ndarray[Any, np.dtype[float]] = np.empty((_i, _j), dtype=float)

        for _index in range(_i):
            _matrix[_index]: np.ndarray[Any, np.dtype[float]] = _read_line_as_float_array(_file)

        return _matrix

    data: dict = dict()

    with open(filename, 'r') as file:
        _skip_first_line(file)
        data['seed']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['number_of_suppliers']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['inbound_docks']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['outbound_docks']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['vehicles']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['vehicle_capacity']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['number_of_customers']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['number_of_products']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['time_to_load_one_pallet']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['service_time_per_pallet']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['changeover_time']: int = _read_line_as_int(file)

        _go_to_next_info(file)
        data['processing_time_for_inbound_load']: np.ndarray[Any, np.dtype[int]] = _read_line_as_int_array(file)

        _go_to_next_info(file)
        _i: int = data['number_of_customers'] + 2
        _j: int = 2
        _time_window: np.ndarray[Any, np.dtype[int]] = np.transpose(_read_lines_as_int_matrix(file, _i, _j))
        data['time_window_start']: np.ndarray[Any, np.dtype[int]] = _time_window[0]
        data['time_window_end']: np.ndarray[Any, np.dtype[int]] = _time_window[1]

        _go_to_next_info(file)
        data['quantity_of_required_pallets_per_customer']: np.ndarray[Any, np.dtype[int]] = _read_line_as_int_array(file)

        _go_to_next_info(file)
        _i: int = data['number_of_products']
        _j: int = data['number_of_customers']
        data['quantity_of_required_products_per_customer']: np.ndarray[Any, np.dtype[int]] = _read_lines_as_int_matrix(file, _i, _j)

        _go_to_next_info(file)
        _i: int = data['number_of_products']
        _j: int = data['number_of_suppliers']
        data['number_of_each_product_into_inbound_loads']: np.ndarray[Any, np.dtype[int]] = _read_lines_as_int_matrix(file, _i, _j)

        _go_to_next_info(file)
        data['volume_of_each_product']: np.ndarray[Any, np.dtype[float]] = _read_line_as_float_array(file)

        _go_to_next_info(file)
        _i: int = data['number_of_customers'] + 2
        _j: int = data['number_of_customers'] + 2
        data['travel_time']: np.ndarray[Any, np.dtype[float]] = _read_lines_as_float_matrix(file, _i, _j)

        _go_to_next_info(file)
        data['number_to_update_the_time_windows']: float = _read_line_as_float(file)

        _go_to_next_info(file)
        data['instance']: str = _read_line_as_string(file)

    return data
