import os  # For file system operations
import subprocess  # To run BLAST as a system command

def run_blast(query_file, db_file):
    """
    Function to run BLAST search and return results as a string.

    Parameters:
    query_file (str): Path to the query FASTA file
    db_file (str): Path to the BLAST database

    Returns:
    str: The BLAST results in tabular format as a string
    """
    temp_output = "temp_blast_output.txt"
    blast_command = [
        "blastn",
        "-query", query_file,
        "-db", db_file,
        "-out", temp_output,
        "-outfmt", "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore",
        "-evalue", "0.001",
        "-num_alignments", "1"
    ]
    subprocess.run(blast_command, check=True)
    with open(temp_output, "r") as f:
        blast_results = f.read()
    os.remove(temp_output)
    return blast_results

def parse_blast_result(blast_result):
    """
    Parse BLAST result to extract percent identity and subject ID.

    Parameters:
    blast_result (str): BLAST output in tabular format

    Returns:
    tuple: (percent identity, subject ID)
    """
    if not blast_result.strip():
        return None, None  # No result found
    lines = blast_result.strip().split("\n")
    best_hit = lines[0].split("\t")  # Take the first (best) hit
    percent_identity = float(best_hit[2])
    subject_id = best_hit[1]
    return percent_identity, subject_id

def main():
    fasta_directory = "/mnt/c/Users/ericb/OneDrive/Documents/fasta_files/"    
    vulpes_db = "/mnt/c/Users/ericb/OneDrive/Documents/blast_db/albula_vulpes_reference"
    goreensis_db = "/mnt/c/Users/ericb/OneDrive/Documents/blast_db/albula_goreensis_reference"
    summary_output_file = "/mnt/c/Users/ericb/OneDrive/Documents/blast_results/blast_summary_results.txt"
    species_summary_file = "/mnt/c/Users/ericb/OneDrive/Documents/blast_results/species_summary.txt"

    # Initialize the output files
    with open(summary_output_file, "w") as summary_file, open(species_summary_file, "w") as species_file:
        summary_file.write("BLAST Summary Results\n")
        summary_file.write("=====================\n\n")
        summary_file.write("Query ID\tSubject ID\t% Identity\tAlignment Length\tMismatches\tGap Openings\tQuery Start\tQuery End\tSubject Start\tSubject End\tE-value\tBit Score\n")
        summary_file.write("---------\t----------\t-----------\t----------------\t-----------\t------------\t-----------\t---------\t-------------\t-----------\t-------\t---------\n\n")

        species_file.write("Sample ID\tSpecies Identified\tPercent Identity\n")
        species_file.write("---------\t------------------\t----------------\n")

        # Loop through all FASTA files in the directory
        for fasta_file in os.listdir(fasta_directory):
            if fasta_file.endswith(".fa"):
                query_file = os.path.join(fasta_directory, fasta_file)        

                # Run BLAST against both databases
                print(f"Running BLAST for {fasta_file} against Albula vulpes...")
                vulpes_result = run_blast(query_file, vulpes_db)
                vulpes_identity, _ = parse_blast_result(vulpes_result)        

                print(f"Running BLAST for {fasta_file} against Albula goreensis...")
                goreensis_result = run_blast(query_file, goreensis_db)        
                goreensis_identity, _ = parse_blast_result(goreensis_result)  

                # Determine which species has the higher percent identity     
                if vulpes_identity is None and goreensis_identity is None:
                    # No matches in either database
                    species_file.write(f"{fasta_file}\tNo Match\tN/A\n")
                    continue
                elif vulpes_identity is None:
                    # No match in vulpes database, use goreensis
                    top_species = "Albula goreensis"
                    top_identity = goreensis_identity
                elif goreensis_identity is None:
                    # No match in goreensis database, use vulpes
                    top_species = "Albula vulpes"
                    top_identity = vulpes_identity
                else:
                    # Both databases have matches; compare percent identities
                    if vulpes_identity >= goreensis_identity:
                        top_species = "Albula vulpes"
                        top_identity = vulpes_identity
                    else:
                        top_species = "Albula goreensis"
                        top_identity = goreensis_identity

                # Write to species summary file
                species_file.write(f"{fasta_file}\t{top_species}\t{top_identity:.3f}\n")

                # Append detailed BLAST results to summary file
                with open(summary_output_file, "a") as summary_file:
                    summary_file.write(f"Results for {fasta_file} (Albula vulpes):\n")
                    summary_file.write(vulpes_result + "\n")
                    summary_file.write(f"Results for {fasta_file} (Albula goreensis):\n")
                    summary_file.write(goreensis_result + "\n")
                    summary_file.write("\n")

                print(f"Completed BLAST for {fasta_file}")

if __name__ == "__main__":
    main()
