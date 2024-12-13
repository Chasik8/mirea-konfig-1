import re
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify_xml(elem):
    """Возвращает строку с красиво отформатированным XML."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def parse_input(input_text):
    """Разбирает учебный конфигурационный текст."""
    constants = {}

    # def replace_constants(match):
    #     name = match.group(1)
    #     if name not in constants:
    #         raise ValueError(f"Undefined constant: @{name}")
    #     return str(constants[name])

    # Убираем комментарии
    input_text = re.sub(r"\|\|.*", "", input_text)

    # Обрабатываем объявления констант
    for const_decl in re.finditer(r"var\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?);", input_text):
        name, value = const_decl.groups()
        #value = re.sub(r"@\{([a-zA-Z_][a-zA-Z0-9_]*)\}", replace_constants, value.strip())
        try:
            constants[name] = eval(value)
        except Exception as e:
            raise ValueError(f"Error evaluating constant {name}: {e}")

    # Заменяем константы
    #input_text = re.sub(r"@\{([a-zA-Z_][a-zA-Z0-9_]*)\}", replace_constants, input_text)

    # Проверяем синтаксис
    if re.search(r"[^\s{}\[\]:,()\"'a-zA-Z0-9_\-]", input_text):
        raise ValueError("Invalid syntax detected")

    return input_text

def convert_to_xml(parsed_text):
    """Преобразует разобранный текст в XML."""

    def parse_value(value):
        value = value.strip()
        if value.startswith("list("):
            return parse_list(value)
        elif value.startswith("(["):
            return parse_dict(value)
        elif value.startswith("\"") and value.endswith("\""):
            return value[1:-1]
        else:
            try:
                return eval(value)
            except Exception:
                raise ValueError(f"Invalid value: {value}")

    def parse_list(value):
        values = re.findall(r"([^,]+)(?:,|$)", value[5:-1])
        list_elem = ET.Element("list")
        for val in values:
            item_elem = ET.SubElement(list_elem, "item")
            item_elem.text = str(parse_value(val))
        return list_elem

    def parse_dict(value):
        entries = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*):([^,]+)(?:,|$)", value[2:-2])
        dict_elem = ET.Element("dict")
        for key, val in entries:
            entry_elem = ET.SubElement(dict_elem, "entry", name=key)
            entry_elem.text = str(parse_value(val))
        return dict_elem

    root = ET.Element("root")
    for line in parsed_text.splitlines():
        line = line.strip()
        if line:
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                child = ET.SubElement(root, key)
                child.append(parse_value(value))
            else:
                raise ValueError(f"Invalid line: {line}")

    return prettify_xml(root)

if __name__ == "__main__":
    try:
        input_text = input()
        parsed_text = parse_input(input_text)
        xml_output = convert_to_xml(parsed_text)
        print(xml_output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)