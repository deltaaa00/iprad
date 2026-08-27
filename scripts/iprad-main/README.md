![banner](assets/banner.png)
<p align="center">
  <img src="https://img.shields.io/github/license/deltaaa00/iprad?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python Version">
  <img src="https://img.shields.io/github/stars/deltaaa00/iprad?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/github/last-commit/deltaaa00/iprad?style=flat-square" alt="Last Commit">
</p>

**iprad** - modular Python-based CLI utility designed for IP Lookup. Built with scalability in mind, it separates core logic into distinct modules for easier maintenance and expansion. 

# ❗️IP Type 
**iprad** supports only Ipv4 addresses. Also you can write domain, like `google.com` when using **iprad**. 

# 💻 Architecture
* **Modular Design**: Core functionality is encapsulated within the `src/iprad/core` package.
* **Package Management**: Uses `pyproject.toml` for modern dependency management and entry point configuration.
* **Data Persistence**: Includes a local `.cache` directory for caching results.
# 🚀 Installation

Project uses `pyproject.toml`, you can install it as a package directly from the source.

### Standard installation
```bash
git clone
cd iprad
pip install .
```
Now it is installed in your system

### Alternative method
You can run this commands for installation
```bash
#macOS or Linux
curl -L https://raw.githubusercontent.com/deltaaa00/iprad/refs/heads/main/scripts/install.sh | bash
```

```bash
curl -k -L https://raw.githubusercontent.com/deltaaa00/iprad/refs/heads/main/scripts/install.bat -o install.bat && install.bat
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

### Cache cleaning 🧹
**iprad** has cache function. If you want to clean cache run this:
```bash
iprad rmcache
```

You will get this message
```markdown
> Cache removed successfully
```