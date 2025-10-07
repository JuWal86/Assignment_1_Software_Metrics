# Assignment_1_Software_Metrics
# Software Metrics Measurement Tool

This project is a Python-based tool for analyzing large-scale software systems using fundamental software metrics.  
It was developed as part of a software engineering course to explore size, complexity, and coupling across real-world projects such as the Linux kernel, JDK, and ITK.

## Overview

The tool measures and reports the following key software metrics:

- **Physical Lines of Code (PLOC)** – Counts all non-empty lines (including comments).
- **Logical Lines of Code (LLOC)** – Counts only lines contributing to program behavior.
- **Cyclomatic Complexity (CC)** – Measures decision points in control flow.
- **Fan-in** – Number of functions calling a given function.
- **Fan-out** – Number of functions called by a given function.

These metrics help assess size, complexity, coupling, modularity, and maintainability in large codebases.

## Supported Languages

- C / C++
- Java  
- (Experimental) Python – fan-in/fan-out detection is less reliable due to dynamic typing.

## Run

python3 src/measurement_tool.py --repo <path_to_repo> --out <output_csv>

