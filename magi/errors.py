"""Runtime error types and exit-code categories."""


class MagiError(Exception):
    """A deterministic contract or state transition failure."""


class ContractError(MagiError):
    """An artifact failed a closed contract."""


class StateError(MagiError):
    """A command is invalid for the current trial state."""


class AgentError(MagiError):
    """A configured model command failed or returned invalid output."""

