# opened or closed

Vamos a establecer dos sistemas de funcionamiento:

1. Todos los puertos abiertos (o delegar la gestión de esos puertos), especificando cuales se cierran

Si se opta por la primera opción, sólo cerraremos los que se especifiquen (con la opción `-p`)

2. Todos los puertos cerrados, especificando cuales se abren

Se optará por esta segunda siempre que no se especifique la opción `-p`. Con `-o` se indicará qué puertos deben seguir abiertos
