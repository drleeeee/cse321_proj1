# CSE321 Project #1: Implementation and Analysis of B-tree Index Structures

**Author:** Dongryeol Lee (Student ID: 20221288)
**Course:** CSE321 Database Systems, UNIST

---

## 1. Environment & Dependencies

This project is implemented strictly in pure Python without any external tree-based index structures, adhering to the project core requirements.

* **Programming Language:** Python 3.9+ (Python 3.10+ recommended)
* **OS Compatibility:** Cross-platform (Windows, macOS, Linux)
* **Standard Libraries Used:** `csv`, `time`, `random`, `argparse`, `os`, `sys`
* **Third-party Dependencies:** None. (No `pip install` required)

## 2. Directory Structure

Please ensure the project is unzipped and maintains the following structure before execution:

```text
cse321_proj1/
├── README.md               # This execution guide
├── main.py                 # Single entry point for all experiments
├── data/
│   └── students.csv        # 100,000 student records (Mandatory)
└── src/
    ├── btree.py            # B-tree implementation
    ├── bstar_tree.py       # B*-tree implementation (Redistribution & 2-to-3 Split)
    ├── bplus_tree.py       # B+-tree implementation (Leaf Linked List for Range Query)
    └── experiments.py      # Automated workload evaluator
```

## 3. Step-by-Step Execution Guide

This project features a fully automated Command Line Interface (CLI) to evaluate the fundamental workloads: Insertion, Point Search, Range Query, and Deletion.

### Step 3.1: Data Preparation
Ensure the provided `students.csv` file is located inside the `data/` directory. If the file is missing, the script will automatically generate 100,000 dummy records to prevent execution failure.

### Step 3.2: Running the Fundamental Workloads
Navigate to the root directory (`cse321_proj1/`) in your terminal and execute `main.py`. The default fan-out order (d) is set to 5.

```bash
python main.py
```

### Step 3.3: Parameter Tuning (Changing Tree Order)
To test the trees with a different fan-out order (e.g., d=10), use the `-d` or `--order` argument.

```bash
python main.py -d 10
```

### Step 3.4: [Bonus] Running Additional Edge Case Experiments
To evaluate the structural defense mechanisms of the B-tree and B*-tree against worst-case scenarios (Sequential Insertion), append the `--edge` flag.

```bash
python main.py -d 5 --edge
```

## 4. Workload Details

* **Insertion:** Measures the time to insert 100,000 records. B*-tree explicitly outputs the number of sibling redistributions.
* **Point Search:** Measures the average response time for 10,000 random key lookups.
* **Range Query:** Executes a custom analytical query tracking the linked-list traversal efficiency in the B+-tree compared to in-order traversals in others.
* **Deletion:** Evaluates the structural integrity by deleting a random 10% subset of the dataset and handling underflows natively.

---
*If you encounter any unexpected behaviors during execution, please check the Python version or contact me.*
