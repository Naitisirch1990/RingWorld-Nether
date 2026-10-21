# Instalación SEGURA (solo servidor clonado)

1. Detener el servidor.
2. Duplicar **el servidor entero**: mods, world, datapacks y configuraciones.
3. En el CLON, respaldar la carpeta `world/DIM-1/region` del Nether.
4. Extraer exclusivamente `DIM-1/region/` del ZIP de mapa experimental en el Nether del CLON; **nunca** en producción.
5. Colocar el datapack de loot entregado junto al mapa en `world/datapacks/` del CLON.
6. Compilar el addon independiente `ringworld_nether` para Minecraft 1.20.1 Forge 47.4.10; todavía no está validado ni disponible como JAR listo para instalar.
7. Mantener el RingWorld original en `mods/`. El addon **no** lo reemplaza.
8. Verificar Overworld, End y las 14 misiones originales antes y después de la prueba; revisar las pruebas de aceptación.

La referencia original del portal Nether era X=15118, Y=85, Z=-549. El spawn nuevo se propone en X=142, Y=84, Z=0; su conexión segura necesita comprobación.

**Advertencia:** El mapa solo aporta los archivos de región del Nether, no un mundo completo ni su `level.dat`; copiar regiones encima de otras las reemplaza permanentemente. Guardar los backups.
