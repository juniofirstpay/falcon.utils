import json
from casbin.persist.adapter import load_policy_line
from casbin.persist.adapters import FileAdapter as _FileAdapter


class FileAdapter(_FileAdapter):

    def __init__(self, file_path):
        self._file_path: str = file_path

    def load_policy(self, model):
        if self._file_path.endswith(".json"):
            return self.load_policy_json(model)
        else:
            return super().load_policy(model)

    def load_policy_json(self, model):
        with open(self._file_path, "rb") as file:
            data = json.loads(file.read())
        for item in data:
            tokens = []
            ptype = "g" if item["type"] == "group" else "p"

            if ptype == "p":
                tokens.append(ptype)
                tokens.append(item["sub"])
                if item.get("dom"):
                    tokens.append(item["dom"])
                tokens.append(item["obj"])
                tokens.append(item["act"])
            elif ptype == "g":
                tokens.append(ptype)
                tokens.append(item["sub"])
                tokens.append(item["grp"])
                if item.get("dom"):
                    tokens.append(item["dom"])
            load_policy_line(", ".join(tokens), model)


__all__ = ("FileAdapter",)
