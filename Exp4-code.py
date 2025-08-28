import requests
import sympy as sp
import time
import os
import warnings
import importlib.util

if not os.path.exists('module_laplace.so'):
    url = "https://github.com/Lab2Phys/module-laplace-inverse/raw/refs/heads/main/module_laplace.so"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open("module_laplace.so", "wb") as f:
            f.write(response.content)
        print("Downloaded module_laplace.so successfully")
    except requests.RequestException as e:
        print(f"Error downloading module_laplace.so: {e}")
        raise

spec = importlib.util.spec_from_file_location("module_laplace", "./module_laplace.so")
module_laplace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_laplace)

from module_laplace import (
    compute_voltages,
    create_symbolic_impedance_matrix,
    generate_time_points,
    create_precompiled_voltage_functions,
    generate_and_display_outputs
)


warnings.filterwarnings("ignore")
s, t = sp.symbols('s t', real=True, positive=True)

decimal_places = 4
num_loops = 5
num_nodes = 7

R = 113000
C = 470e-6
e1 = 9
e2 = 5
e3 = 12

r = 1 / (C * s)

edges = [
    (1, 2, R + r), (1, 3, R), (1, 6, R + r),
    (2, 3, R), (2, 5, R), (2, 7, R + r),
    (3, 4, R), (4, 5, R + r), (4, 6, R),
    (5, 7, R), (6, 7, R)
]

loops = [
    [1, 3, 4, 6], [4, 5, 6, 7], [2, 3, 4, 5],
    [1, 2, 3], [2, 5, 7]
]

capacitor_branches_map = {
    'v1': (1, 6), 'v2': (4, 5), 'v3': (1, 2),
    'v4': (2, 7), 
}

voltage_map = {
    'v1': {'label': 'Voltage V1', 'capacitor': 'C1', 'index': 0},
    'v2': {'label': 'Voltage V2', 'capacitor': 'C2', 'index': 1},
    'v3': {'label': 'Voltage V3', 'capacitor': 'C3', 'index': 2},
    'v4': {'label': 'Voltage V4', 'capacitor': 'C4', 'index': 3},
}

V = sp.Matrix([[e2 / s], [0], [0], [e1 / s], [e3 / s]])


# Start calculations 
Z, loop = create_symbolic_impedance_matrix(num_loops, edges, loops, s)
voltage_functions, symbolic_voltage_functions = create_precompiled_voltage_functions(
    Z, V, edges, loop, capacitor_branches_map, r, s
)

start_time_total = time.time()
t_vals = generate_time_points(0.1, 2000, 2000)
voltage_data, max_voltages, max_times = compute_voltages(
    t_vals, voltage_functions, voltage_map, decimal_places
)

if __name__ == '__main__':
    plot_filename, table_filename, max_voltage_table_filename = generate_and_display_outputs(
        t_vals, voltage_data, max_voltages, max_times, voltage_map, decimal_places, start_time_total, voltage_functions
    )
    print(f"\nReports generated:")
    if os.path.exists(plot_filename):
        print(f"Plots: {plot_filename} | Size: {os.path.getsize(plot_filename)/1024:.2f} KB")
    if os.path.exists(table_filename):
        print(f"Table (Threshold): {table_filename} | Size: {os.path.getsize(table_filename)/1024:.2f} KB")
    if os.path.exists(max_voltage_table_filename):
        print(f"Table (Max Voltages): {max_voltage_table_filename} | Size: {os.path.getsize(max_voltage_table_filename)/1024:.2f} KB")
    print(f"Total Computation Time: {time.time() - start_time_total:.2f} s")
