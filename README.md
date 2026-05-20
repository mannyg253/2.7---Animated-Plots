# Advanced Disease AI (Synthetic Bloodstream Analysis)

This project provides an educational AI pipeline that analyzes **synthetic bloodstream biomarker data** and predicts one of four states:

- Healthy
- Viral infection
- Bacterial sepsis
- Autoimmune flare

## What it does

1. Generates synthetic biomarker measurements.
2. Trains a neural network classifier.
3. Prints performance metrics.
4. Produces a simple feature-impact explanation for one prediction.

## Important safety disclaimer

This is **not** for clinical use and must not be used for diagnosis, triage, or treatment.

## Run

```bash
python3 advanced_disease_ai.py
```

## Dependencies

- numpy
- pandas
- scikit-learn
- tensorflow
