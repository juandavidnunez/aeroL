"""
FlightNode: represent one individual flight within the AVL tree.
Contains all the information about the flight + structural attributes of the tree.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FlightNode:
    # ── Identidad del vuelo ────────────────────────────────
    code: str          # Código único del vuelo (clave del árbol AVL)
    origin: str        # Ciudad de origen
    destination: str   # Ciudad de destino

    # ── Información económica ──────────────────────────────
    base_price: float  # Precio base del vuelo
    passengers: int    # Número de pasajeros

    promotion: float = 0.0  # Descuento aplicado al vuelo
    penalty: float = 0.0    # Penalización (recargo por condiciones especiales)

    # ── Estado del vuelo ──────────────────────────────────
    is_critical: bool = False   # Indica si el vuelo está en estado crítico
    priority: int = 1           # Nivel de prioridad (puede usarse para lógica del negocio)

    alerts: list = field(default_factory=list)  
    # Lista de alertas asociadas al vuelo (ej: retrasos, sobreventa, etc.)

    # ── Atributos del árbol AVL ───────────────────────────
    height: int = 1  
    # Altura del nodo dentro del árbol (clave para balanceo AVL)

    balance_factor: int = 0  
    # Factor de balance = altura izquierda - altura derecha
    # Debe estar entre -1 y 1 en un AVL correcto

    # Tree links
    left: Optional["FlightNode"] = field(default=None, repr=False)
    right: Optional["FlightNode"] = field(default=None, repr=False)

    @property
    def final_price(self) -> float:
        """
       Calculate the final price of the flight after applying promotion and penalty.
        Formula:
            final_price = max(base_price + penalty - promotion, 0)
            This ensures that the final price cannot be negative, which could happen if the promotion exceeds the sum of the base price and penalty.
        """
        return max(self.base_price + self.penalty - self.promotion, 0.0)

    @property
    def profitability(self) -> float:
        """
        Calculate the rentability of the flight based on passengers, final price, promotion, and penalty.

        FFormula:
        rentability = (passengers * final_price) - promotion + penalty

        This allows us to determine how profitable a flight is
        to make decisions such as eliminations or priorities.
        """
        return self.passengers * self.final_price - self.promotion + self.penalty