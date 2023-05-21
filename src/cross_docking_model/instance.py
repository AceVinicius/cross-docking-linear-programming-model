import numpy as np
from typing import Any, Dict, List, TextIO


def skip_first_line(file: TextIO) -> None:
    """
    Skips the first line of the file.

    Args:
        file (TextIO): The file to read from.
    """
    title = file.readline().strip()
    if title == "":
        raise ValueError("Expected a title for next section")


def go_to_next_info(file: TextIO) -> None:
    """
    Goes to the next section of the file.

    Args:
        file (TextIO): The file to read from.

    Raises:
        ValueError: If an empty line is not found after the previous section.
        ValueError: if a title is not found for the next section.
    """
    empty_line = file.readline().strip()
    if empty_line != "":
        raise ValueError("Expected an empty line after previous section")

    title = file.readline().strip()
    if title == "":
        raise ValueError("Expected a title for next section")


def read_line_as_string(file: TextIO) -> str:
    """
    Reads a line from the file and returns it as a string.

    Args:
        file (TextIO): The file to read from.

    Returns:
        The line read from the file as a string.

    Raises:
        ValueError: If the file is closed.
        ValueError: If the read operation fails.
    """
    try:
        line = file.readline().strip()
        if not line:
            raise ValueError("Empty line read from file.")
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Error reading line from file: {e}")

    return line


def read_line_as_int(file: TextIO) -> int:
    """
    Reads a line from the file and returns it as an integer.

    Args:
        file (TextIO): The file to read from.

    Returns:
        int: The line read from the file as an integer.

    Raises:
        ValueError: If the input data is not an integer.
    """
    line = read_line_as_string(file)

    if not line.isdecimal():
        raise ValueError(f"Input data is not an integer: {line}")

    return int(line)


def read_line_as_float(file: TextIO) -> float:
    """
    Reads a line from the file handler and returns it as a float.

    Args:
        file (TextIO): The file to read from.

    Returns:
        float: The line read from the file as a float.

    Raises:
        ValueError: If the input data is not a float.
    """
    line: str = read_line_as_string(file)

    if not line.replace('.', '', 1).isdecimal():
        raise ValueError(f"Input data is not a float: {line}")

    return float(line)


def read_line_as_list(file: TextIO) -> List[str]:
    """
    Reads a line from the file and returns it as a list of strings.

    Args:
        file (TextIO): The file to read from.

    Returns:
        List[str]: The line read from the file as a list of strings.
    """
    return read_line_as_string(file).split()


def read_line_as_int_array(file: TextIO) -> np.ndarray[np.int64]:
    """
    Reads a line from a file handler and returns it as a NumPy array of integers.

    Args:
        file (TextIO): The file to read from.

    Returns:
        np.ndarray[np.int64]: A NumPy integer array containing the read values.

    Raises:
        ValueError: If the line contains non-integer values.
    """
    try:
        data = np.array([int(x) for x in read_line_as_list(file)], dtype=int)
    except ValueError as e:
        raise ValueError("Error reading line as integer array") from e
    return data


def read_line_as_float_array(file: TextIO) -> np.ndarray[np.float64]:
    """
    Reads a line of floating-point numbers from a file and returns a NumPy float array.

    Args:
        file (TextIO): The file to read from.

    Returns:
        np.ndarray[np.float64]: A NumPy float array containing the read values.

    Raises:
        ValueError: If the line contains non-numeric values.
    """
    try:
        data = np.array([float(x) for x in read_line_as_list(file)], dtype=np.float64)
    except ValueError as e:
        raise ValueError(f"Error reading line as float array: {e}") from e

    return data


def read_lines_as_int_matrix(file: TextIO, rows: int, cols: int) -> np.ndarray[np.int64]:
    """
    Reads a matrix of integers from the given file.

    Args:
        file (TextIO): The file to read from.
        rows (int): The number of rows in the matrix.
        cols (int): The number of columns in the matrix.

    Returns:
        np.ndarray[np.int64]: The matrix of integers read from the file.

    Raises:
        ValueError: If the matrix shape does not match the expected shape.
        ValueError: If there is an error reading a line as an integer array.
    """
    matrix = np.empty((rows, cols), dtype=np.int64)

    for row_index in range(rows):
        try:
            matrix[row_index] = np.array(read_line_as_int_array(file), dtype=np.int64)
        except ValueError as e:
            raise ValueError(f"Error reading line {row_index + 1} as integer array: {e}") from e

    if matrix.shape != (rows, cols):
        raise ValueError(f"Matrix shape {matrix.shape} does not match expected shape ({rows}, {cols})")

    return matrix


def read_lines_as_float_matrix(file: TextIO, rows: int, cols: int) -> np.ndarray[np.float64]:
    """
    Reads a matrix of floats from the given file.

    Args:
        file (TextIO): A text file to read from.
        rows (int): The number of rows in the matrix.
        cols (int): The number of columns in the matrix.

    Returns:
        np.ndarray[np.float64]: The matrix of floats as a numpy array.

    Raises:
        ValueError: If the matrix shape does not match the expected shape.
        ValueError: If there is an error reading a line as a float array.
    """
    matrix = np.empty((rows, cols), dtype=np.float64)

    for row_index in range(rows):
        try:
            matrix[row_index] = np.array(read_line_as_float_array(file), dtype=np.float64)
        except ValueError as e:
            raise ValueError(f"Error reading line {row_index + 1} as float array: {e}") from e

    if matrix.shape != (rows, cols):
        raise ValueError(f"Matrix shape {matrix.shape} does not match expected shape ({rows}, {cols})")

    return matrix


def read_data(filename: str) -> Dict[str, Any]:
    """
    Reads data from a file and returns a dictionary.

    Args:
        filename (str): The name of the file to read data from.

    Returns:
        A dictionary containing the data read from the file.
    """
    data = {}

    with open(filename, 'r') as file:
        skip_first_line(file)
        data['seed'] = read_line_as_int(file)

        go_to_next_info(file)
        data['number_of_suppliers'] = read_line_as_int(file)

        go_to_next_info(file)
        data['inbound_docks'] = read_line_as_int(file)

        go_to_next_info(file)
        data['outbound_docks'] = read_line_as_int(file)

        go_to_next_info(file)
        data['vehicles'] = read_line_as_int(file)

        go_to_next_info(file)
        data['vehicle_capacity'] = read_line_as_int(file)

        go_to_next_info(file)
        data['number_of_customers'] = read_line_as_int(file)

        go_to_next_info(file)
        data['number_of_products'] = read_line_as_int(file)

        go_to_next_info(file)
        data['time_to_load_one_pallet'] = read_line_as_int(file)

        go_to_next_info(file)
        data['service_time_per_pallet'] = read_line_as_int(file)

        go_to_next_info(file)
        data['changeover_time'] = read_line_as_int(file)

        go_to_next_info(file)
        data['processing_time_for_inbound_load'] = read_line_as_int_array(file)

        go_to_next_info(file)
        rows, cols = data['number_of_customers'] + 2, 2
        time_window = np.transpose(read_lines_as_int_matrix(file, rows, cols))
        data['time_window_start'] = time_window[0]
        data['time_window_end'] = time_window[1]

        go_to_next_info(file)
        data['quantity_of_required_pallets_per_customer'] = read_line_as_int_array(file)

        go_to_next_info(file)
        rows, cols = data['number_of_products'], data['number_of_customers']
        data['quantity_of_required_products_per_customer'] = read_lines_as_int_matrix(file, rows, cols)

        go_to_next_info(file)
        rows, cols = data['number_of_products'], data['number_of_suppliers']
        data['number_of_each_product_into_inbound_loads'] = read_lines_as_int_matrix(file, rows, cols)

        go_to_next_info(file)
        data['volume_of_each_product'] = read_line_as_float_array(file)

        go_to_next_info(file)
        rows, cols = data['number_of_customers'] + 2, data['number_of_customers'] + 2
        data['travel_time'] = read_lines_as_float_matrix(file, rows, cols)

        go_to_next_info(file)
        data['number_to_update_the_time_windows'] = read_line_as_float(file)

        go_to_next_info(file)
        data['instance'] = read_line_as_string(file)

        matrix = 0.4 * data['volume_of_each_product'][:, np.newaxis, np.newaxis] * (
                    10 + 2 * (np.arange(data['inbound_docks'])[:, np.newaxis] - np.arange(data['outbound_docks'])))
        data['transfer_time_for_each_product'] = matrix.astype(np.float64)

    return data
