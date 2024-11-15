import json
import struct
import re
import sys


def assemble_and_interpret(input_file, output_binary, log_file, result_file, memory_range):
    def assemble(lines):
        commands = []
        instructions = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):  # Пропускаем пустые строки и комментарии
                continue

            if line.startswith("LOAD_CONST"):
                _, b = line.split()
                b = int(b)
                command = (35 << 6) | (b & 0x1FFFF)
                instructions.append(command.to_bytes(3, byteorder='big'))
                commands.append({"command": "LOAD_CONST", "bytes": list(command.to_bytes(3, 'big')), "details": {"A": 35, "B": b}})
            elif line.startswith("READ_MEM"):
                command = 8
                instructions.append(command.to_bytes(1, byteorder='big'))
                commands.append({"command": "READ_MEM", "bytes": [8]})
            elif line.startswith("WRITE_MEM"):
                _, b = line.split()
                b = int(b)
                command = (44 << 6) | (b & 0x3FF)
                instructions.append(command.to_bytes(3, byteorder='big'))
                commands.append({"command": "WRITE_MEM", "bytes": list(command.to_bytes(3, 'big')), "details": {"A": 44, "B": b}})
            elif line.startswith("SHIFT_RIGHT"):
                _, b = line.split()
                b = int(b)
                command = (19 << 6) | (b & 0x3FF)
                instructions.append(command.to_bytes(3, byteorder='big'))
                commands.append({"command": "SHIFT_RIGHT", "bytes": list(command.to_bytes(3, 'big')), "details": {"A": 19, "B": b}})
        
        # Записываем бинарный файл
        with open(output_binary, 'wb') as f:
            for instruction in instructions:
                f.write(instruction)

        # Записываем JSON-лог
        with open(log_file, 'w') as f:
            json.dump(commands, f, indent=4)

    def interpret():
        # Читаем бинарный файл
        with open(output_binary, 'rb') as f:
            data = f.read()

        memory = [0] * 1024
        stack = []
        pc = 0

        while pc < len(data):
            opcode = data[pc]
            if opcode == 0x63:  # LOAD_CONST
                b = int.from_bytes(data[pc + 1:pc + 3], byteorder='big')
                stack.append(b)
                pc += 3
            elif opcode == 0x08:  # READ_MEM
                addr = stack.pop()
                stack.append(memory[addr])
                pc += 1
            elif opcode == 0x6C:  # WRITE_MEM
                b = int.from_bytes(data[pc + 1:pc + 3], byteorder='big')
                value = stack.pop()
                addr = stack.pop() + b
                memory[addr] = value
                pc += 3
            elif opcode == 0xD3:  # SHIFT_RIGHT
                b = int.from_bytes(data[pc + 1:pc + 3], byteorder='big')
                addr = stack.pop()
                value = memory[addr] >> b
                stack.append(value)
                pc += 3

        # Сохраняем диапазон памяти
        result = {
            "memory_range": memory_range,
            "values": memory[memory_range[0]:memory_range[1]]
        }

        with open(result_file, 'w') as f:
            json.dump(result, f, indent=4)

    # Читаем файл программы
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Ассемблируем и интерпретируем
    assemble(lines)
    interpret()


if __name__ == "__main__":
    # Входные параметры
    input_program = "prog.txt"  # Исходная программа
    binary_output = "bin.bin"   # Бинарный файл
    log_output = "log.json"     # Лог команд
    result_output = "result.json"  # Результат выполнения
    memory_range = (0, 16)  # Диапазон памяти для вывода

    # Выполнение
    assemble_and_interpret(input_program, binary_output, log_output, result_output, memory_range)
