from typing import Dict, Any, Optional


class ConfigSection:
    def __init__(self, name: str, values: Dict[str, Any], comment: Optional[str] = None):
        self.name = name
        self.values = values
        self.comment = comment

    def dumps(self):
        headers = f'[{self.name}]\n'
        comment = f'# {self.comment}\n' if self.comment else ''
        content = '\n'.join(f'{k} = {v}' for k, v in self.values.items())
        return headers + comment + content


class WGConfig:
    def __init__(self):
        self.sections = []
        self.others = {}

    def add_section(self, section: ConfigSection):
        self.sections.append(section)

    def add_value(self, key: str, value: Any):
        self.others[key] = value

    def dumps(self):
        sections = '\n\n'.join(s.dumps() for s in self.sections)
        values = '\n'.join(f'{k} = {v}' for k, v in self.others.items())
        return sections + '\n\n' + values + '\n'
