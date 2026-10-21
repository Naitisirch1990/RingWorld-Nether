# RingWorld Nether — Forge 1.20.1

Proyecto **separado** del RingWorld del Overworld. El repositorio original `Naitisirch1990/RingWorld` **no se modifica**.

## Tres entregables

| Componente | Estado |
|---|---|
| **Mapa del Nether** | Primera versión experimental generada offline: 14.976 × 1.008 bloques, 6 sectores, camino cerrado, estructuras y 240 cofres; comprobación estática Anvil/NBT realizada. **No probado en Minecraft.** |
| **Addon `ringworld_nether`** | Código experimental para trabajar solo en `minecraft:the_nether`. **Todavía sin compilar ni probar.** |
| **Misiones** | Proyecto futuro independiente. No implementado. |

## Mapa

- Biomas en orden: Nether Wastes (spawn), Crimson Forest, Warped Forest, Soul Sand Valley, Basalt Deltas y Nether Wastes (fortaleza final).
- Camino de 7 bloques, iluminación temática, 5 bloques de altura libre.
- Muros laterales de bedrock de hasta 40 bloques y barreras. Exterior vacío. Sin techo de bedrock.
- 24 ubicaciones con construcciones y 10 cofres por ubicación. Incluye volcán y cuatro diseños aportados por el usuario.
- Punto de llegada propuesto: X=142, Y=84, Z=0. **La conexión con el portal existente requiere pruebas.**
- Los 60 archivos Anvil `.mca` del mapa y los esquemáticos de terceros **no se publican en GitHub** por tamaño/licencias. Se conservan en los paquetes entregados al propietario.

## Regla de seguridad

**Nunca sustituir `DIM-1` en el servidor principal para probar este proyecto.** Duplicar completamente servidor, mundo, `mods` y `datapacks`; probar en ese clon. La dimensión `DIM-1` corresponde al Nether, no al Overworld, pero sobrescribirla destruye el Nether existente.

El addon debe mantener el Overworld y End intactos: geometría, Atlas, portales y las 14 misiones. No utilizar un `.jar` experimental como reemplazo del RingWorld original. El addon necesita su propio mod id `ringworld_nether` y se instala solo después de superar compilación y pruebas.

## Compatibilidad

Objetivo: **Minecraft Java 1.20.1 / Forge 47.4.10 / Java 17**, con el `.jar` del RingWorld Forge 1.20.1 que actualmente funciona en el servidor. La rama principal moderna de RingWorld en GitHub corresponde a otra versión de Minecraft; no debe copiarse directamente.

## Organización

- `mapa/`: planificación, generación y verificaciones.
- `mod-ringworld-nether/`: addon Forge en desarrollo.
- `mod-misiones/`: alcance de misiones futuras.
- `docs/`: instalación segura y pruebas.

**Estado:** trabajo experimental; se han realizado pruebas de estructura de archivos, no pruebas en el motor de Minecraft. Ninguna modificación al servidor principal ni al repositorio RingWorld original.
