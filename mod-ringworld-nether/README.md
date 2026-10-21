# Addon RingWorld Nether — Forge 1.20.1

**Código experimental; NO compilado ni probado dentro del juego.**

El mod independiente utiliza mod id `ringworld_nether`; requiere el RingWorld 1.20.1 sin modificar y no sustituye el mod del Overworld.

Objetivos:
- Exclusivamente dimensión `minecraft:the_nether`.
- Anillo 14.976 × 1.008 bloques.
- Muros de 40 bloques y techo abierto en mapa preconstruido.
- Paquete de sincronización con campos separados para Overworld, Nether y End.
- Puerta de entrada al spawn X142.5/Y84/Z0.5.

Los puntos de inyección (mixins) dependen de las clases internas del JAR Forge 1.20.1 aportado por el usuario y pueden fallar con otras versiones. No se ha comprobado todavía si el renderizado del Atlas funciona con esta geometría ni si los portales sobreviven el teletransporte.

## Compilación prevista
Java 17 y ForgeGradle 6. Copia **tu JAR original** a `libs/ringworld-original.jar`; no se publica por ser binario de terceros. Ejecuta `gradle build` con acceso a las dependencias de Forge. No instales el resultado en producción sin pruebas.

El RingWorld moderno visible en `Naitisirch1990/RingWorld` usa un Minecraft distinto: este addon se basa en el JAR específico para 1.20.1.
