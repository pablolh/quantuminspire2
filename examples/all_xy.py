from pathlib import Path
from typing import Any, Dict, List

from quantuminspire.sdk.models.circuit import Circuit
from quantuminspire.sdk.models.hybrid_algorithm import HybridAlgorithm
from quantuminspire.util.api.local_runtime import LocalRuntime
from quantuminspire.util.api.quantum_interface import QuantumInterface

RUNTIME_TYPE_ID = 3

CIRCUITS = [
    ["X90", "mX90"],
    ["X180", "X180"],
    ["Y180", "Y180"],
    ["X180", "Y180"],
    ["Y180", "X180"],
    ["X90"],
    ["Y90"],
    ["X90", "Y90"],
    ["Y90", "X90"],
    ["X90", "Y180"],
    ["Y90", "X180"],
    ["X180", "Y90"],
    ["Y180", "X90"],
    ["X90", "X180"],
    ["X180", "X90"],
    ["Y90", "Y180"],
    ["Y180", "Y90"],
    ["X180"],
    ["Y180"],
    ["X90", "X90"],
    ["Y90", "Y90"],
]


def generate_circuit(circuit_string: List[str]) -> str:
    with Circuit(platform_name="spin-2", program_name="prgm1") as circuit:
        kernel = circuit.init_kernel("new_kernel", 2)
        for operation in circuit_string:
            if operation == "X90":
                kernel.rx90(0)
            elif operation == "mX90":
                kernel.mrx90(0)
            elif operation == "X180":
                kernel.x(0)
            elif operation == "Y90":
                kernel.ry90(0)
            elif operation == "Y180":
                kernel.y(0)
            else:
                raise Exception()
        if RUNTIME_TYPE_ID == 3:
            kernel.measure(0)

    return circuit.content


def execute(qi: QuantumInterface) -> None:
    """Run the classical part of the Hybrid Quantum/Classical Algorithm.

    Args:
        qi: A QuantumInterface instance that can be used to execute quantum circuits

    The qi object has a single method called execute_circuit, its interface is described below:

    qi.execute_circuit args:
        circuit: a string representation of a quantum circuit
        number_of_shots: how often to execute the circuit

    qi.execute_circuit return value:
        The results of executing the quantum circuit, this is an object with the following attributes
            results: The results from iteration n-1.
            shots_requested: The number of shots requested by the user for the previous iteration.
            shots_done: The number of shots actually run.
    """
    for string_circuit in CIRCUITS:
        circuit = generate_circuit(string_circuit)
        result = qi.execute_circuit(circuit, 1024)

        print(result.results)
        print(result.shots_requested)
        print(result.shots_done)


def finalize(list_of_measurements: Dict[int, List[Any]]) -> Dict[str, Any]:
    """Aggregate the results from all iterations into one final result.

    Args:
        list_of_measurements: List of all results from the previous iterations.

    Returns:
        A free-form result, with a `property`: `value` structure. Value can
        be everything serializable.
    """
    print(list_of_measurements)
    return {"results": list_of_measurements}


if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint
    from time import sleep

    import numpy as np

    import matplotlib.pyplot as plt

    from quantuminspire.sdk.models.hybrid_algorithm import HybridAlgorithm
    from quantuminspire.util.api.remote_runtime import RemoteRuntime

    import datetime

    from dateutil.tz import tzutc

    ONE = "0000000001" if RUNTIME_TYPE_ID == 3 else "00001"

    name = "all_xy"

    run_id = None  # = 741

    labels = [
        "I,I",
        "X180,X180",
        "Y180,Y180",
        "X180,Y180",
        "Y180,X180",
        "X90,I",
        "Y90,I",
        "X90,Y90",
        "Y90,X90",
        "X90,Y180",
        "Y90,X180",
        "X180,Y90",
        "Y180,X90",
        "X90,X180",
        "X180,X90",
        "Y90,Y180",
        "Y180,Y90",
        "X180,I",
        "Y180,I",
        "X90,X90",
        "Y90,Y90",
    ]

    runtime = RemoteRuntime()

    if not run_id:
        program = HybridAlgorithm(platform_name="spin-2", program_name=name)
        program.read_file(Path(f"{name}.py"))
        run_id = runtime.run(program, runtime_type_id=RUNTIME_TYPE_ID)
        print(f"Upload file with name: {name}")
        print(f"run_id {run_id}")

    results = None
    while results is None:
        results = runtime.get_results(run_id)
        print("No results.")
        sleep(5)

    pprint(results)

    l = [r.results.get(ONE, 0) / r.shots_done for r in results]

    plt.figure(1234)
    plt.clf()
    plt.plot(l, marker="x")
    plt.xticks(np.arange(len(labels)), labels, rotation=90)
    plt.ylabel(r"$P_{even}$")
    plt.ylim([-0.1, 1.1])

    plt.tight_layout()

    plt.show()
