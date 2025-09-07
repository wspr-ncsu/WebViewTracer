# Fingerprinting Analysis

This directory contains the code required to conduct the fingerprinting analysis mentioned in the paper. Please make sure to run the `python3 ./scripts/wvt-cli.py results` command before running the project. To run the analysis:

- Run `celery -A tasks worker --loglevel=info -Q fingerprinting --concurrency $(nproc)`
- Run the cells in `fingerprinting.ipynb` in order.

