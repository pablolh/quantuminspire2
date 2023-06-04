from typing import Any, Dict, List

from quantuminspire.sdk.models.circuit import Circuit
from quantuminspire.sdk.stop_execution import StopExecution

import copy
import numpy as np




class Optimizer:
    def __init__(self):
        self._x_start= []
        self._step = 1.0
        self.no_improve_thr = 10e-6
        self.no_improv_break = 10
        self.max_iter = 0
        self.alpha = 1.
        self.gamma = 2.
        self.rho = -0.5
        self.sigma = 0.5
        self._optimizer_state = ""
        self._no_improv = 0
        self._res = None
        self._dim = 0
        self._x = None
        self._i = 0
        self._stopcriterium = False
        self._iteration_state = ""
        self._res = None
        self._iters = 0
        self._best: float = None
        self._prev_best: float = None
        self._x0 = None

    def initialise(self) -> Dict[str, Any]:
        """
        Do whatever is necessary to initialise the optimizer
        Update optimization_state
        Returns:
             the initial quantum circuit
        """

        self._dim = len(self._x_start)

        # "prev_best = f(x_start)"
        # generate quantum circuit to compute start value
        with Circuit(platform_name="spin-2", program_name="prgm1") as circuit:
            kernel = circuit.init_kernel("new_kernel", 2)
            kernel.hadamard(0)
            kernel.cnot(0, 1)

        self._optimizer_state = "init_1"

        return {"shots_requested": 1024, "circuit": circuit.content}

    def iterate(self, results: Dict[str, float], shots_requested: int, shots_done: int) -> Dict[str, Any]:
        """Execute the next step of the optimization algorithm

        Returns:
            the next quantum circuit

        """
        self._quantum_result = process_quantum_result(results, shots_requested, shots_done)

        match self._optimizer_state:
            case "init_1":
                self._prev_best = self._quantum_result
                self._no_improv = 0
                self._res = [[self._x_start, self._prev_best]]
                self._i = 0
                self._x = copy.copy(self._x_start)
                self._x[self._i] = self._x[self._i] + self._step
                # Generate next quantum circuit
                self._optimizer_state = "init_2"
                return {"shots_requested": 1024, "circuit": "the next quantum circuit"}
            case "init_2":
                self._prev_best = self._res.append([self._x, self._score])
                self._i += 1
                if self._i < self._dim:
                    self._x = copy.copy(self._x_start)
                    self._x[self._i] = self._x[self._i] + self._step
                    # Generate next quantum circuit
                    self._optimizer_state = "init_2"
                    return {"shots_requested": 1024, "circuit": "the next quantum circuit"}

                self._iters = 0

                self._continue_iter = False
                while True:
                    self._iterate()  # this will generate the next quantum circuit, set the self._stop_criterium, or
                                     # reenter the while. It notes its state in self._iteration state
                    if self._loop_criterium== "continue":
                            continue
                    else:
                        break

                return
                self._res.sort(key=lambda x: x[1])
                self._best = self._res[0][1]

                # break after max_iter
                if self._max_iter and self._iters >= self._max_iter:
                    self._stopcriterium = True
                    return {}
                self._iters += 1

                # break after no_improv_break iterations with no improvement
                # print('...best so far:', best)

                if self._best < self._prev_best - self._no_improve_thr:
                    self._no_improv = 0
                    self._prev_best = self._best
                else:
                    self._no_improv += 1

                if self._no_improv >= self._no_improv_break:
                    self._stopcriterium = True
                    return {}

                # centroid
                self._x0 = [0.] * self._dim
                for tup in self._res[:-1]:
                    for i, c in enumerate(self._tup[0]):
                        self._x0[i] += c / (len(self._res) - 1)

    def finalise(self) -> Any:
        pass

    def stopcriterium(self):
        return self._stopcriterium

optimizer = Optimizer()


def initialize() -> Dict[str, Any]:
    """Generate the first iteration of the classical part of the Hybrid Quantum/Classical Algorithm.

    Returns:
        cQASM string representing the test algorithm.
    """
    return optimizer.initialise()


def execute(results: Dict[str, float], shots_requested: int, shots_done: int) -> Dict[str, Any]:
    """Run the next 2-n iterations of the classical part of the Hybrid Quantum/Classical Algorithm.

    Args:
        results: The results from iteration n-1.
        shots_requested: The number of shots requested by the user for the previous iteration.
        shots_done: The number of shots actually run.

    Compute the next quantum circuit, based on the outcome in results. The state of the optimizer is in
    optimization_state.
    When done, raise StopExecution

    Returns:
        cQASM string representing the test algorithm.
    """
    print(results)
    print(shots_requested)

    quantum_circuit = optimizer.iterate(process_quantum_result, results, shots_requested, shots_done)

    if optimizer.stopcriterium():
        raise StopExecution

    print(shots_done)
    return quantum_circuit


def finalize(list_of_measurements: Dict[int, List[Any]]) -> Dict[str, Any]:
    """Aggregate the results from all iterations into one final result.

    Args:
        list_of_measurements: List of all results from the previous iterations.

    Returns:
        A free-form result, with a `property`: `value` structure. Value can
        be everything serializable.
    """
    print(list_of_measurements)
    return {}


def process_quantum_result(results: Dict[str, float], shots_requested: int, shots_done: int) -> Any:
    # process the quantum result into something the optimizer algorithm needs
    pass


if __name__ == "__main__":
    # Run the individual steps for debugging
    print("=== Ansatz ===\n", initialize())
    print("=== Next iteration ===\n", execute({"01": 0.5, "10": 0.5}, 1024, 1024))
