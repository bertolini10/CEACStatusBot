from cx_Freeze import setup, Executable

setup(
    name="CONSULAR",
    version="1.0",
    description="Consular Visa Checking",
    executables=[Executable(script="test.py")],
)