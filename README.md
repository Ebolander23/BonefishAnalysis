# BonefishAnalysis
Python Script using BLAST for automation of Bonefish Analysis.

# Bonefish Species Identification Pipeline

This repository contains a Python-based pipeline developed for the **Bonefish Genetics Project** at Bonefish & Tarpon Trust. It automates species identification by comparing sample DNA sequences to reference databases using BLAST. This tool was used to investigate the presence of *Albula goreensis* on flats previously dominated by *Albula vulpes*.

## Description

The pipeline was designed to assist with species-level identification of bonefish samples using genetic data. It helps differentiate *Albula vulpes* from *Albula goreensis* by automating BLAST comparisons and reporting the species with the highest sequence identity.

---

## 📁 Project Structure
```
bonefish-blast-dir/
│
├── fasta_files/ # Sample FASTA files (input)
├── blast_db/ # Preformatted BLAST databases (vulpes and goreensis)
├── blast_results/ # Output folder for summary files
│ ├── blast_summary_results.txt (BLAST standard format output) 
│ └── species_summary.txt (Excel styled output for easy use)
├── bonefish_blast.py # Main Python script
└── README.md # This file
```
---

## Dependencies

- Python 3.13.0
- [BLAST+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download) (must be installed and in your system path)

---

## Downloading Reference Sequences from NCBI

To build BLAST databases, you need FASTA-format reference sequences for the mitochondrial DNA of *Albula vulpes* and *Albula goreensis*. Here's how you can retrieve them:

1. Visit [NCBI Nucleotide Search](https://www.ncbi.nlm.nih.gov/nucleotide/).
2. Search for terms like:
   - `"Albula vulpes mitochondrion complete genome"`
   - `"Albula goreensis mitochondrion complete genome"`
3. Choose a sequence that matches your needs (complete genome or relevant mitochondrial gene region).
4. Click **"Send to" → "File"**, choose format **FASTA**, then click **"Create File"** to download.

Rename the downloaded files to:

- `albula_vulpes.fa`
- `albula_goreensis.fa`

Move them into the `blast_db/` directory.

---

## 🔧 Database Preparation

Once you have the reference FASTA files, create BLAST databases using these commands:

```bash
# Create Albula vulpes BLAST database
makeblastdb -in blast_db/albula_vulpes.fa -dbtype nucl -out blast_db/albula_vulpes_reference

# Create Albula goreensis BLAST database
makeblastdb -in blast_db/albula_goreensis.fa -dbtype nucl -out blast_db/albula_goreensis_reference
```
- `-in: Input Fasta File`
- `-dbtype nucl: Indicates we want nucleotide base type`
- `-out: Path for output files`

---

## How to Run

1. **Prepare your environment**:
    - Install BLAST+ if not already installed.
    - Place all `.fa` files (one per sample) in the `fasta_files/` directory.
    - Make sure you have two BLAST-formatted databases in the `blast_db/` folder:
        - `albula_vulpes_reference`
        - `albula_goreensis_reference`
     
2. **Database Creation**:
   

3. **Run the pipeline**:
    ```bash
    python3 bonefish_species_identifier.py
    ```

4. **Outputs**:
    - `blast_summary_results.txt`: Full raw BLAST results for both species per sample.
    - `species_summary.txt`: Tabulated species ID and percent identity per sample.

---

## 📊 Example Output

| Sample ID                  | Species Identified | Percent Identity |
|---------------------------|--------------------|------------------|
| BTT003_ALBA-3R_7984908_015 | Albula vulpes      | 97.89            |
| BTT060_ALBA-3R_7984908_013 | Albula vulpes      | 98.689           |
| ...                       | ...                | ...              |

---

## 🔄 Reproducibility & Versioning

- This codebase is version-controlled using Git.
- Code and data dependencies are described in this README.
- A GitHub release will be created for publication reference.

---

## 📜 Citation & Attribution

If this tool contributes to a publication, please cite:
> Bolander, E. et al. (2025). *Investigating Species Distribution in Bonefish Using Automated Genetic Analysis*. In Review.

---

## 🧠 Contact

For questions, collaborations, or reproducibility concerns, please contact:  
**Eric Bolander** – *ebolander@ucsd.edu*


