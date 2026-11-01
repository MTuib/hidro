import os
from pathlib import Path
from datetime import datetime
from uuid import uuid4


class Backup:
    def __init__(self, pendents_dir: Path | None = None):
        base_dir = Path(__file__).resolve().parent
        self.pendents_dir = pendents_dir or (base_dir / "pendents")
        self.pendents_dir.mkdir(exist_ok=True)

    def crear_backup(self, msg) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = msg.topic.replace("/", "_").replace(":", "_")
        contingut = msg.payload.decode(errors="ignore") + "\n"

        while True:
            identificador = uuid4().hex
            filename = self.pendents_dir / (
                f"{timestamp}_{safe_topic}_{identificador}.txt"
            )

            try:
                with open(filename, "x", encoding="utf-8") as f:
                    f.write(contingut)
            except FileExistsError:
                # Si el nom ja existeix, genera un altre UUID.
                continue

            print(f"Backup creat: {filename}")
            return filename

    @staticmethod
    def eliminar_backup(path: Path) -> bool:
        try:
            os.remove(path)
            print(f"Backup eliminat: {path}")
            return True
        except Exception as e:
            print(f"No s'ha pogut eliminar el backup {path}: {e}")
            return False
