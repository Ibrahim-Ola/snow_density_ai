
from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]

PROJNAME = "sonw_density_ai"
DESCRIPTION = "A project that predicts snow density and SWE using machine learning models and statistical models."
with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
MAINTAINER = "Ibrahim Olalekan Alabi"
MAINTAINER_EMAIL = "ibrahimolalekana@u.boisestate.edu"
URL = "https://github.com/Ibrahim-Ola/snow_density_ai.git"
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/Ibrahim-Ola/snow_density_ai/issues",
    "Documentation": "https://github.com/Ibrahim-Ola/snow_density_ai/blob/main/README.md",
    "Source Code": "https://github.com/Ibrahim-Ola/snow_density_ai",
}
VERSION = "0.0.1"
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.9"


def setup_package():
    metadata = dict(
        name=PROJNAME,
        version=VERSION,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        url=URL,
        project_urls=PROJECT_URLS,
        license=LICENSE,
        python_requires=PYTHON_REQUIRES,
        packages=find_packages(),
        install_requires=parse_requirements('requirements.txt'),
        classifiers=[
            "Development Status :: Mature",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Topic :: Scientific/Engineering :: Hydrology",
        ],
        keywords=[
            "Artificial Intelligence",
            "SNOTEL",
            "Snow Density",
            "Snow",
            "Snow Depth",
            "Snow Water Equivalent",
            "Machine Learning"
        ],
    )

    setup(**metadata)

if __name__ == "__main__":
    setup_package()
    print("Setup Complete.")