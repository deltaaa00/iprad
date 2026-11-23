![banner](assets/banner.png)
<p align="center">
  <img src="https://img.shields.io/github/license/deltaaa00/iprad?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/github/stars/deltaaa00/iprad?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/last-commit/deltaaa00/iprad?style=for-the-badge" alt="Last Commit">
  <img src="https://img.shields.io/pypi/v/iprad?color=00c853&style=for-the-badge" alt="pypi version">
  <img src="https://img.shields.io/pypi/dm/iprad?color=blue&style=for-the-badge" alt="downloads">
  <img src="https://img.shields.io/github/actions/workflow/status/deltaaa00/iprad/publish.yml?style=for-the-badge&label=build" alt="build status">
</p>

**iprad** - modular Python-based CLI utility designed for IP Lookup. Built with scalability in mind, it separates core logic into distinct modules for easier maintenance and expansion. 

# ❗️IP Type 
**iprad** supports IPv4, IPv6, and domain names such as `google.com`. Domain lookups prefer IPv4 and fall back to IPv6 for IPv6-only hosts. IPv6 addresses are normalized before lookup and caching.

# 💻 Architecture
* **Modular Design**: Core functionality is encapsulated within the `iprad/core` package.
* **Package Management**: Uses `pyproject.toml` for modern dependency management and entry point configuration.
* **Data Persistence**: Includes a local `.cache` directory for caching results.
# 🚀 Installation

Project uses `pyproject.toml`, you can install it as a package directly from the source.

### Standard installation

`iprad` can be installed with `pip`

### Windows
```bash
pip install iprad
```

### Linux/macOS
```bash
pip3 install iprad
```
Also you can install it via `git clone`
```bash
git clone https://github.com/deltaaa00/iprad.git
cd iprad
pip install .
```

### For Developers (Editable Mode)
If you plan to modify the code and want changes to take effect immediately:
```bash
git clone https://github.com/deltaaa00/iprad.git
cd iprad
pip install -e .
```

### API Keys 🔑
Some modules use API Keys. For example AbuseIPDB need it. Go to **iprad** directory *(can be user folder)*. And run this:

```bash
cp .env.example .env
```
Then, open it in your text editor and replace `YOUR_KEY` with your API KEY for module.

```text
ABUSEIPDB_API_KEY="YOUR KEY" <-- replace this
```

# Examples 💾

Let`s try
```bash
iprad check 1.1.1.1
```
And you`ll get this
![example_output](assets/example.png)
**iprad** has some modules, that require **sudo** mode, for opening raw socket, for example:

```bash
sudo iprad check 1.1.1.1 -pt
```

Also, you can check own IP with this command:

```bash
iprad check myip
```

`-pt` Enables ping and traceroute module. Here is output:

![output_pt](assets/output_pt.jpeg)

If you don't want to use API Keys you can run with `--nokeys`

```bash
iprad check 1.1.1.1 --nokeys
```

### Cache 🧹
**iprad** has cache function. If you want to clean cache run this:
```bash
iprad cache rm
```
You will get this message
```
Cache removed successfully
```
Also you can check cache size via this command:
```bash
iprad cache info
```
You will get this message similar to this:
```
Cache Size:  0.07MB
```

### Request retries and timeouts

Lookup requests retry transient connection/read failures and HTTP 429, 500, 502,
503, and 504 responses. The default is two retries after the initial attempt,
with exponential backoff. Other HTTP errors (such as 401 and 403) are not retried.
Each attempt has a 10-second connect/read timeout; this is not a total command deadline.

```bash
iprad check 1.1.1.1 --nokeys --retries 3 --timeout 5
iprad check 2606:4700:4700::1111 --nokeys
```

Use `--retries 0` to disable retries. These options apply to the `check` command's
API requests, including public address discovery with `myip`.

### Cache controls

Results are cached for 48 hours by default. Expired entries are fetched again.
`--refresh` bypasses existing entries and saves successful fresh results;
`--cache-ttl HOURS` changes the lifetime for that invocation. A TTL of zero always
fetches fresh data. A failed refresh reports the failure rather than displaying
old data. Existing `iprad cache info` and `iprad cache rm` commands still apply.

```bash
iprad check 1.1.1.1 --nokeys --refresh
iprad check 1.1.1.1 --nokeys --cache-ttl 6
```

IPv6 ping is available with `-pt` where raw ICMP permissions and connectivity
allow it. The current `icmplib` dependency supports IPv4 traceroute only, so IPv6
checks display the ping report and an explanation instead of attempting traceroute.

### Development checks

```bash
python -m unittest discover -s tests -v
python -m build
```

The tests use mocked API responses and a local HTTP server; no API key or external
network access is required.
