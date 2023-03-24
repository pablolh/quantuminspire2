from typing import Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from quantuminspire.sdk.circuit import Circuit

MOCK_QUANTUM_CIRCUIT = "quantum circuit"


@pytest.fixture
def openql(mocker: MockerFixture) -> Generator[MagicMock, None, None]:
    yield mocker.patch("quantuminspire.sdk.circuit.openql")


@pytest.fixture
def mock_file(mocker: MockerFixture) -> None:
    mocker.patch("quantuminspire.sdk.circuit.open", mocker.mock_open(read_data=MOCK_QUANTUM_CIRCUIT))
    mocker.patch("quantuminspire.sdk.circuit.Path.unlink")


def test_create(openql: MagicMock) -> None:
    _ = Circuit(platform_name="platform", program_name="program")
    openql.set_option.assert_called_once()


def test_get_program_name(openql: MagicMock, mock_file: None) -> None:
    with Circuit(platform_name="platform", program_name="program") as c:
        pass

    assert c.program_name == "program"


def test_create_empty_circuit(openql: MagicMock, mock_file: None) -> None:
    with Circuit(platform_name="platform", program_name="program") as c:
        pass

    openql.Program().compile.assert_called_once()
    assert c.qasm == MOCK_QUANTUM_CIRCUIT


def test_create_circuit_with_kernel(openql: MagicMock, mock_file: None) -> None:
    with Circuit(platform_name="platform", program_name="program") as c:
        k = c.init_kernel("kernel1", 2)
        k.x(0)

    openql.Program().add_kernel.assert_called_once()
    assert c.max_number_of_qubits == 2


def test_create_circuit_with_multiple_kernels(openql: MagicMock, mock_file: None) -> None:
    with Circuit(platform_name="platform", program_name="program") as c:
        k = c.init_kernel("kernel1", 2)
        k.x(0)
        _ = c.init_kernel("kernel2", 3)

    assert len(openql.Program().add_kernel.mock_calls) == 2
    assert c.max_number_of_qubits == 3


def test_create_circuit_reuse_kernel(openql: MagicMock, mock_file: None) -> None:
    with Circuit(platform_name="platform", program_name="program") as c:
        k = c.init_kernel("kernel1", 2)
        k.x(0)
        c.add_kernel(k)

    assert len(openql.Program().add_kernel.mock_calls) == 2