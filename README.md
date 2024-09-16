# JSentinel

JSentinel is an automated script to help penetration testers and bug bounty hunters quickly discover subdomains, filter working domains, find JavaScript files, and check for secrets within those files.

## Features

- **Subdomain Discovery:** Uses [subfinder](https://github.com/projectdiscovery/subfinder) to find subdomains for the provided domain.
- **Domain Filtering:** Filters working subdomains using [httpx-toolkit](https://github.com/projectdiscovery/httpx).
- **JavaScript Files Discovery:** Uses [katana](https://github.com/projectdiscovery/katana) to find JavaScript files on working domains.
- **Secret Detection:** Checks for secrets in JavaScript files using [Mantra](https://github.com/MrEmpy/Mantra).

## Requirements

- [subfinder](https://github.com/projectdiscovery/subfinder)
- [httpx-toolkit](https://github.com/projectdiscovery/httpx)
- [katana](https://github.com/projectdiscovery/katana)
- [Mantra](https://github.com/MrEmpy/Mantra)

## Installation

To get started, clone this repository:

```bash
git clone https://github.com/DeveshAwadhiya/JSentinel.git
```
Install the required tools:

# Example installation steps for required tools
go install -v github.com/projectdiscovery/subfinder/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest

Install Mantra by following the instructions in the [Mantra Repository](https://github.com/MrEmpy/Mantra).

###Usage
Run the script by providing a domain:

```bash
python3 jsentinel.py
```


You'll be prompted to input the domain name, and the script will perform the following actions:

1.Discover subdomains.
2.Filter out working domains.
3.Find JavaScript files.
4.Search for secrets in the JavaScript files.

##Author
Devesh Awadhiya
[Github](https://github.com/DeveshAwadhiya)
