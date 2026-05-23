"""Exception classes for TTS functionality."""


class TTSException(Exception):
    """Base exception class for TTS-related errors."""


class TTSConfigurationError(TTSException):
    """Exception raised when a configuration value is invalid."""


class TTSValidationError(TTSException):
    """Exception raised when user input fails validation."""


class TTSRequestError(TTSException):
    """Exception raised when the remote request fails."""


class TTSAPIError(TTSException):
    """Exception raised when the provider returns an API error payload."""


class TTSOutputError(TTSException):
    """Exception raised when saving or preparing the output file fails."""
