import setuptools

setuptools.setup(
    name="yamconfig",
    version="0.1.0",
    install_requires=["pyyaml>=5"],
    python_requires="~=3.5",
    extras_require={"click": ["click>=7"]},
)
