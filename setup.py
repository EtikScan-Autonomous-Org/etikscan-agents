from setuptools import setup, find_packages

setup(
    name="etikscan-agents",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "autogen>=0.1.0",
    ],
    author="EtikScan Team",
    author_email="info@etikscan.io",
    description="Code source, outils et orchestration de la flotte d'agents IA (AutoGen)",
    keywords="ai, agents, autogen",
    python_requires=">=3.8",
)