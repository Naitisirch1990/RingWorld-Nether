# Arquitectura segura — tres componentes

1. **Mapa:** archivos Anvil `DIM-1/region/*.mca` preconstruidos offline, estructuras y loot. No incluir en GitHub público los esquemáticos de terceros ni el mundo binario.
2. **Addon `ringworld_nether`:** usa su propio mod id y modifica solo las dimensiones y geometría que corresponden al Nether. Requiere el RingWorld original; NO sustituye su JAR.
3. **Mod de misiones:** un tercer mod aislado después de estabilizar la dimensión.

Especificación: circunferencia 14976, ancho 1008, seis tramos de 2496, camino Z=0, portal seguro (142,84,0), 24 ubicaciones, 240 cofres, volcán y mapa sin techo.

## Detalle del paquete de red

El constructor de `Forge1201SettingsPacket` del RingWorld 1.20.1 posee doce parámetros: `overworldWidth`, `overworldCircumference`, `netherWidth`, `netherCircumference`, `endWidth`, `endCircumference`, semilla y parámetros restantes. La inyección del addon solo reemplaza los índices **2** y **3**, correspondientes **exclusivamente** al Nether; Overworld y End no se alteran.

## Limitaciones

Los archivos de región se verificaron estáticamente, no en el motor. La compilación del addon, el rendering, los cambios de dimensiones, la conexión entre portales y la persistencia tras reinicio requieren prueba en un servidor completamente clonado.
