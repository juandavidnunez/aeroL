"""
FlightNode: representa un vuelo individual dentro del árbol AVL.
Contiene toda la información del vuelo + atributos estructurales del árbol.
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
        Calcula el precio final del vuelo.

        Fórmula:
        precio_final = base_price + penalty - promotion

        Se asegura que el precio nunca sea negativo.
        """
        return max(self.base_price + self.penalty - self.promotion, 0.0)

    @property
    def profitability(self) -> float:
        """
        Calcula la rentabilidad del vuelo.

        Fórmula:
        rentabilidad = (pasajeros * precio_final) - promoción + penalización

        Esto permite saber qué tan rentable es un vuelo
        para tomar decisiones como eliminaciones o prioridades.
        """
        return self.passengers * self.final_price - self.promotion + self.penalty