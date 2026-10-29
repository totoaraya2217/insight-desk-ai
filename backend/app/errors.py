class NoEncontradoError(Exception):
    """El recurso solicitado no existe (HTTP 404)."""


class ReglaNegocioError(Exception):
    """La operación viola una regla de negocio (HTTP 409)."""
