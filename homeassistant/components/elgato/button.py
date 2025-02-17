"""Support for Elgato button."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from elgato import Elgato, ElgatoError

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ElgatoDataUpdateCoordinator
from .entity import ElgatoEntity


@dataclass
class ElgatoButtonEntityDescriptionMixin:
    """Mixin values for Elgato entities."""

    press_fn: Callable[[Elgato], Awaitable[Any]]


@dataclass
class ElgatoButtonEntityDescription(
    ButtonEntityDescription, ElgatoButtonEntityDescriptionMixin
):
    """Class describing Elgato button entities."""


BUTTONS = [
    ElgatoButtonEntityDescription(
        key="identify",
        name="Identify",
        icon="mdi:help",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda client: client.identify(),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elgato button based on a config entry."""
    coordinator: ElgatoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ElgatoButtonEntity(
            coordinator=coordinator,
            description=description,
        )
        for description in BUTTONS
    )


class ElgatoButtonEntity(ElgatoEntity, ButtonEntity):
    """Defines an Elgato button."""

    entity_description: ElgatoButtonEntityDescription

    def __init__(
        self,
        coordinator: ElgatoDataUpdateCoordinator,
        description: ElgatoButtonEntityDescription,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.info.serial_number}_{description.key}"
        )

    async def async_press(self) -> None:
        """Trigger button press on the Elgato device."""
        try:
            await self.entity_description.press_fn(self.coordinator.client)
        except ElgatoError as error:
            raise HomeAssistantError(
                "An error occurred while identifying the Elgato Light"
            ) from error
