from scholaros.kernel import Kernel


def test_kernel_creation():
    kernel = Kernel()
    assert kernel.state.value == "created"