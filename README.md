# pumi-pic-spack (Spack repo)

This Spack repository provides recipes for:

- **PUMI-PiC**: [SCOREC/pumi-pic](https://github.com/SCOREC/pumi-pic)
- **OpenMC with PUMI‑Tally** (OpenMC fork integrating PUMI‑Tally):
  - **OpenMC fork**: [Fuad-HH/openmc](https://github.com/Fuad-HH/openmc) (upstream: [openmc-dev/openmc](https://github.com/openmc-dev/openmc))
  - **PUMI‑Tally**: [Fuad-HH/PumiUMTally](https://github.com/Fuad-HH/PumiUMTally)

## Installation

### 1. Install Spack
It is recommended to use the system-provided Spack if available. If not, follow the instructions below to install
Spack from source. Check the [Spack documentation](https://spack.readthedocs.io/en/latest/getting_started.html) 
for more details.

```bash
git clone --depth=2 https://github.com/spack/spack.git
. /your/path/to/spack/share/spack/setup-env.sh
```

### 2. Create a new environment and activate it
```bash
spack env create pumi-env
spack env activate pumi-env
```

### 3. Add this repository to Spack and update the `builtin` repository

```bash
git repo add https://github.com/Fuad-HH/pumi-pic-spack.git --name pumi-pic-spack
spack repo update builtin --branch releases/v2026.02
```
Now, if you do `spack config get repos` you should see the repositories added to the list.
And doing `spack info pumi-pic` should show the package.


### 4. Install Packages

```bash
spack add pumi-pic
```
or for OpenMC with PUMI-Tally:

```bash
spack add openmc-pumi +pumitally +dagmc ^kokkos+openmp+serial
```
and run `spack concretize` and `spack install` to install the packages.

> [!NOTE]
> PUMI-PiC also supports other Kokkos backends. Check available backends with `spack info kokkos`.

## Using OpenMC with PUMI-Tally
The case setup and run instructions are available here: [OpenMC with PUMI-Tally](https://github.com/Fuad-HH/openmc-pumi-tally-casehttps://gist.github.com/Fuad-HH/bf16253e70ae0122800f2128b9fd4a8f#create-mesh-and-run-case)
