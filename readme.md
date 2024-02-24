# Project Download
- Install git lfs (type "git lfs install" in git bash), which is used to download large files in the project\

  ```
  git lfs install
  ```

- type "git clone -b main  <repository_url>", download ActiveDNS project

  ```
  git clone -b main  <repository_url>
  ```

- Go to the repository directory and type "git lfs fetch" to download large files from the remote server

  ```
  git lfs fetch
  ```

- Type "git lfs checkout"  to checkout files to the working directory 

  ```
  git lfs checkout
  ```
# Project Introduction
## Related Technology Introduction

- **BIND** (Berkeley Internet Name Domain) is a widely used open source DNS server software. It is one of the most commonly used DNS servers on the Internet, and is used to resolve domain names to their corresponding IP addresses, as well as to provide other DNS-related functions.
- **DLZ** (Database Lookaside Zone) is a feature module of BIND that allows DNS data to be stored in external databases instead of traditional text files.DLZ provides a flexible way to manage DNS records, making it possible to store DNS data in various databases such as MySQL, PostgreSQL, etc. In ActiveDNS, **PostgreSQL** is used to accomplish the data storage. DLZ works by combining with the BIND plug-in to forward DNS queries to an external database and retrieve the corresponding DNS records from the database. This approach enables dynamic updating of DNS records, flexible data management and the ability to integrate with other applications.
- **Installation environment：** Ubuntu 22.04
# Project Installation
## 0. Installation of Python Related Modules
The modules in these libraries that need to be installed via pip:

- psycopg2: library for connecting to and manipulating PostgreSQL databases.

- datedays: python date tool.

- numpy: library for performing scientific calculations and array operations.

- ping3: library for performing network ping tests.

- requests: library for sending HTTP requests.

- dnspython: library for resolving and manipulating DNS.

Among these libraries, the following Python built-in modules are required:

- datetime: date and time processing module, no additional installation required.
- json: built-in module for processing JSON data.
- csv: built-in module for reading and writing CSV files.
- futures: provides the ability to execute tasks concurrently

These modules are all placed in the requirements.txt file.Please install yourself.

## 1.Installation & Configuration

Use the 'source' command to run the script **"install.sh"**,complete the installation and configuration of postgreSQL and BIND, and start the **‘named’** service. The **‘named’** service is the core component of the BIND service, and you can start the DNS server of BIND by running named (please use the 'source' command to exercise the environment variable to take effect).

```
source install.sh
```

## 2.Data Measurement & Database Updating

- Run the **scheduled_exec.sh** script file, which sets the measurement program, the database update program, and the clear expired IPs program to run regularly every day.This is mainly achieved through the two programs measure.sh and Monitor_ip.py.

  ```
  source  scheduled_exec.sh
  ```

- **measure.sh**: performs data measurements and completes database updates.

- **Monitor_ip.py**: clears expired IPs.