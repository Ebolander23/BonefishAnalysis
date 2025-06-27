# Import necessary standard Python libraries
import os  # For interacting with the file system paths, directories)
import subprocess  # For running external commands like BLAST from within Python
import tempfile  # For creating temporary files for storing intermediate BLAST results
import argparse  # For parsing command-line arguments provided by the user
import time # tracking how long script takes

# Define a function to run a BLASTn search
def run_blast(query_file, db_file):
    """
    Run BLAST search and return results as a string.

    Parameters:
    query_file (str): Path to the query FASTA file
    db_file (str): Path to the BLAST database

    Returns:
    str: BLAST results in tabular format
    """
    # Create a temporary file to store BLAST output
    # 'delete=False' prevents it from being auto-deleted so we can read it later
    # 'mode="w+"' allows reading and writing to the temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w+') as tmp:
        temp_output = tmp.name  # Store the path to the temp file

    # Construct the BLASTn command with desired parameters
    blast_command = [
        "blastn",  # Use BLASTN for nucleotide-nucleotide comparison
        "-query", query_file,  # The query FASTA file
        "-db", db_file,  # The BLAST-formatted database
        "-out", temp_output,  # Output will be written to the temporary file
        "-outfmt", "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore",  # Custom tabular output format
        "-evalue", "0.001",  # E-value threshold for significance
        "-num_alignments", "1"  # Only keep the top hit
    ]
    # Run the BLAST command using subprocess; 'check=True' raises error on failure
    subprocess.run(blast_command, check=True)

    # Open the temporary output file and read the entire content into a string
    with open(temp_output, "r") as f:
        blast_results = f.read()

    # Delete the temporary file to clean up after ourselves
    os.remove(temp_output)

    # Return the BLAST results as a string
    return blast_results

# Define a function to extract useful information from the BLAST output
def parse_blast_result(blast_result):
    """
    Parse BLAST result to extract percent identity and subject ID.

    Parameters:
    blast_result (str): BLAST output in tabular format

    Returns:
    tuple: (percent identity, subject ID)
    """
    # If the BLAST result string is empty or only whitespace, return None
    if not blast_result.strip():
        return None, None

    # Get the top BLAST hit (first line of output), split into columns by tab
    best_hit = blast_result.strip().split("\n")[0].split("\t")

    # Return percent identity (as float) and subject ID (as string)
    return float(best_hit[2]), best_hit[1]

# Define the main function to orchestrate the pipeline
def main():
    # Create an ArgumentParser to handle command-line arguments
    parser = argparse.ArgumentParser(description="Run BLAST for species identification.")

    # Define required input directory containing .fa files
    parser.add_argument("--input_dir", required=True, help="Directory containing FASTA files")

    # Define required BLAST databases, passed as a list of species_name:path_to_db entries
    parser.add_argument("--databases", required=True, nargs='+', help="Species databases in format species_name:path_to_db")

    # Optional output directory for storing BLAST results; default is 'blast_results'
    parser.add_argument("--output_dir", default="blast_results", help="Directory for output files")

    # Parse the arguments provided by the user
    args = parser.parse_args()

    # Store the input directory path
    fasta_directory = args.input_dir

    # Parse database inputs into a dictionary mapping species_name → path_to_db
    species_dbs = dict(pair.split(":") for pair in args.databases)

    # Store the output directory path
    output_dir = args.output_dir

    # Create the output directory if it doesn’t already exist
    os.makedirs(output_dir, exist_ok=True)

    # Define paths for the two output files: detailed results and species-level summary
    summary_output_file = os.path.join(output_dir, "blast_summary_results.txt")
    species_summary_file = os.path.join(output_dir, "species_summary.txt")

    # *** Start timer
    start_time = time.time()
    # *** Initialize sample counter
    sample_count = 0

    # Open both output files for writing (will be overwritten if they exist)
    with open(summary_output_file, "w") as summary_file, open(species_summary_file, "w") as species_file:
        # Write headers to the summary file
        summary_file.write("BLAST Summary Results\n=====================\n\n")
        summary_file.write("Query ID\tSubject ID\t% Identity\tAlignment Length\tMismatches\tGap Openings\tQuery Start\tQuery End\tSubject Start\tSubject End\tE-value\tBit Score\n")

        # Write headers to the species identification summary file
        species_file.write("Sample ID\tSpecies Identified\tPercent Identity\n")

        # Loop through each file in the input directory
        for fasta_file in os.listdir(fasta_directory):
            # Process only files ending in '.fa' (FASTA format)
            if fasta_file.endswith(".fa"):
                # Construct the full path to the current query file
                query_file = os.path.join(fasta_directory, fasta_file)

                # Dictionary to store BLAST results for all species for this sample
                results = {}
                for species, db_path in species_dbs.items():
                    # Inform the user which species and sample are being processed
                    print(f"Running BLAST for {fasta_file} against {species}...")

                    # Run BLAST and parse the result for percent identity
                    blast_result = run_blast(query_file, db_path)
                    identity, _ = parse_blast_result(blast_result)

                    # Store the identity and raw result for this species
                    results[species] = (identity, blast_result)

                # Filter out species with no valid hit (i.e., identity is None)
                valid_results = {sp: data for sp, data in results.items() if data[0] is not None}

                # If no valid BLAST hits found in any species database
                if not valid_results:
                    species_file.write(f"{fasta_file}\tNo Match\tN/A\n")
                    continue  # Skip to next sample

                # Identify the species with the highest percent identity match
                top_species, (top_identity, _) = max(valid_results.items(), key=lambda x: x[1][0])

                # Write top hit info to species summary file
                species_file.write(f"{fasta_file}\t{top_species}\t{top_identity:.3f}\n")

                # Write full BLAST output for each species to the summary file
                for species, (_, blast_output) in results.items():
                    summary_file.write(f"Results for {fasta_file} ({species}):\n{blast_output}\n")

                # Notify user that the sample has been processed
                print(f"Completed BLAST for {fasta_file}")

                # increment the sample count
                sample_count += 1

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nProcessed {sample_count} sample(s) in {total_time:.2f} seconds.")
# Ensure that main() is only called when the script is run directly
if __name__ == "__main__":
    main()
