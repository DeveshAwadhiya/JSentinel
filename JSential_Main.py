import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re
from tqdm import tqdm
import shutil
import threading

def run_command(command):
    """Run a shell command and return the output."""
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stderr:
        print(f"\033[91mError: {result.stderr}\033[0m")  # Print error in red
    return result.stdout.splitlines()

def strip_ansi_codes(text):
    """Remove ANSI escape codes from the text."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def find_subdomains(domain):
    """Find subdomains using subfinder and include the host domain."""
    print(f"Finding subdomains for {domain}...")
    subdomains = run_command(f"subfinder -d {domain} -silent")
    if domain not in subdomains:
        subdomains.append(domain)  # Ensure the host domain is included
    return subdomains

def filter_working_domains(domains, directory):
    """Filter working domains using httpx-toolkit."""
    print("Filtering working domains...")
    domains_file = os.path.join(directory, "domains.txt")
    with open(domains_file, "w") as f:
        f.write("\n".join(domains))
    run_command(f"httpx-toolkit -l {domains_file} -silent -o {os.path.join(directory, 'working_domains.txt')}")
    with open(os.path.join(directory, "working_domains.txt"), "r") as f:
        return f.read().splitlines()

def find_js_files(domain):
    """Find JavaScript files using katana."""
    print(f"Finding JavaScript files for {domain}...")
    return run_command(f"katana -u {domain} -jc -d 3 -silent")

def filter_js_urls(js_files, directory):
    """Filter and sort JavaScript URLs."""
    print("Filtering and sorting JavaScript URLs...")
    all_js_urls_file = os.path.join(directory, "all_js_urls.txt")
    with open(all_js_urls_file, "w") as f:
        f.write("\n".join(js_files))
    # Sort and filter to keep only .js files
    sorted_js_files = run_command(f"sort {all_js_urls_file} | grep '.js$'")
    filtered_js_urls_file = os.path.join(directory, "filtered_js_urls.txt")
    with open(filtered_js_urls_file, "w") as f:
        f.write("\n".join(sorted_js_files))
    return sorted_js_files

def check_secrets_in_js(directory):
    """Check for secrets in JavaScript files using Mantra."""
    print("Checking for secrets in JavaScript files...")
    filtered_js_urls_file = os.path.join(directory, 'filtered_js_urls.txt')
    
    # Run Mantra on the entire file of URLs
    result = run_command(f"cat {filtered_js_urls_file} | Mantra -s")
    cleaned_result = [strip_ansi_codes(line) for line in result]
    
    return cleaned_result

def prompt_user_for_existing_directory(directory):
    """Prompt the user about existing directory actions."""
    while True:
        choice = input(f"Directory '{directory}' already exists. Do you want to delete it and continue (d), create a new one separately (n), or exit (e)? ").strip().lower()
        if choice in ['d', 'n', 'e']:
            return choice
        print("Invalid choice. Please enter 'd', 'n', or 'e'.")

def prompt_user_for_deletion(directory):
    """Prompt the user to delete the directory with a timeout."""
    def delete_prompt():
        choice = input(f"Do you want to delete the generated files in '{directory}'? (y/n): ").strip().lower()
        if choice == 'y':
            shutil.rmtree(directory)
            print(f"Deleted directory '{directory}'.")
        elif choice == 'n':
            print(f"Files in '{directory}' are saved.")
        else:
            print("No valid input received. Files are saved.")

    timer = threading.Timer(7.0, lambda: print("\nNo response received. Files are saved."))
    timer.start()
    delete_prompt()
    timer.cancel()

def main(domain):
    # Create a directory for the domain with the current date
    date_str = datetime.now().strftime("%Y-%m-%d")
    directory = f"Folders/{domain}_{date_str}"

    if os.path.exists(directory):
        action = prompt_user_for_existing_directory(directory)
        if action == 'd':
            shutil.rmtree(directory)
            print(f"Deleted existing directory '{directory}'.")
        elif action == 'n':
            directory = f"Folders/{domain}_{date_str}_new"
        elif action == 'e':
            print("Exiting program.")
            return

    os.makedirs(directory, exist_ok=True)

    print("\nStarting subdomain discovery...")
    subdomains = find_subdomains(domain)
    if not subdomains:
        print(f"\033[91mNo subdomains found for {domain}.\033[0m")
        return

    print(f"Subdomains found: {subdomains}")

    print("\nFiltering working domains...")
    working_domains = filter_working_domains(subdomains, directory)
    if not working_domains:
        print(f"\033[91mNo working domains found for {domain}.\033[0m")
        return

    print(f"Working domains: {working_domains}")

    print("\nFinding JavaScript files...")
    js_files = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_domain = {executor.submit(find_js_files, domain): domain for domain in working_domains}
        for future in tqdm(as_completed(future_to_domain), total=len(working_domains), desc="Processing domains", unit="domain"):
            domain = future_to_domain[future]
            try:
                js_files.extend(future.result())
            except Exception as exc:
                print(f"\033[91m{domain} generated an exception: {exc}\033[0m")

    if not js_files:
        print(f"\033[91mNo JavaScript files found for {domain}.\033[0m")
        return

    print(f"JavaScript files found: {js_files}")

    print("\nFiltering JavaScript URLs...")
    filtered_js_files = filter_js_urls(js_files, directory)
    print(f"Filtered JavaScript URLs: {filtered_js_files}")

    print("\nChecking for secrets in JavaScript files...")
    secrets = check_secrets_in_js(directory)
    print(f"Secrets found: {secrets}")

    # Save results
    secrets_file = os.path.join(directory, "secrets.txt")
    with open(secrets_file, "w") as f:
        f.write("\n".join(secrets))

    # Clean and sort the secrets file
    run_command(f"sed -i '/Unable/d' {secrets_file}")
    run_command(f"sort -o {secrets_file} {secrets_file}")

    print(f"\nProcess completed. Check {secrets_file} for results.")

    # Prompt user to delete files
    prompt_user_for_deletion(directory)

if __name__ == "__main__":
    domain_input = input("Enter the domain: ")
    main(domain_input)
