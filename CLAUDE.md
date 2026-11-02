# rtl-verification-lab

Módulos RTL en SystemVerilog verificados con cocotb (Python) e Icarus Verilog.

## Comandos
- `make setup`: crea `.venv` e instala dependencias
- `make test`: corre todos los testbenches
- `make test-fifo`, `make test-uart`, `make test-alu`: un solo diseño

## Estructura
- `rtl/<modulo>.sv`: un módulo por archivo. El comentario de cabecera es la spec.
- `tb/test_<modulo>.py`: tests cocotb con modelo de referencia en Python.
- `tb/test_runner.py`: lista `DESIGNS`. Agrega ahí cada módulo nuevo.

## Reglas
- SystemVerilog compatible con Icarus 12 (`-g2012`): sin clases, sin interfaces, sin `unique case`.
- Test-driven: primero el test y la spec en la cabecera del `.sv`, después el RTL.
- No cambiar un test para que pase. Si un test parece incorrecto, preguntar.
- Una tarea está terminada cuando `make test` pasa completo.
- **Git: el usuario hace todos los commits y push.** Claude solo sugiere los comandos.
