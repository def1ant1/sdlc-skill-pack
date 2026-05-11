import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMPILER_PATH = ROOT / "core" / "skill-compiler" / "compiler.py"


spec = importlib.util.spec_from_file_location("skill_compiler", COMPILER_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class CompilerTests(unittest.TestCase):
    def test_compile_is_deterministic(self):
        a = module.compile_skill("demo-skill", version="0.1.0")
        b = module.compile_skill("demo-skill", version="0.1.0")
        self.assertEqual(a, b)

    def test_write_output(self):
        compiled = module.compile_skill("demo")
        with tempfile.TemporaryDirectory() as td:
            out = module.write_compiled_skill(Path(td), compiled)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
