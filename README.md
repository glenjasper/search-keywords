search-keywords
======================
[![License](https://poser.pugx.org/badges/poser/license.svg)](./LICENSE)

This script searches for the keywords, found in a .txt file, in the "Materials and Methods" section of each .txt file (created from .pdf files).

## Table of content

- [Pre-requisites](#pre-requisites)
    - [Python libraries](#python-libraries)
- [Installation](#installation)
    - [Clone](#clone)
    - [Download](#download)
- [How To Use](#how-to-use)
- [Author](#author)
- [Organization](#organization)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Pre-requisites

### Python libraries

```sh
  $ sudo apt install -y python3-pip
  $ sudo pip3 install --upgrade pip
```

```sh
  $ sudo pip3 install argparse
  $ sudo pip3 install xlsxwriter
  $ sudo pip3 install numpy
  $ sudo pip3 install pandas
  $ sudo pip3 install colorama
```

## Installation

### Clone

To clone and run this application, you'll need [Git](https://git-scm.com) installed on your computer. From your command line:

```bash
  # Clone this repository
  $ git clone https://github.com/glenjasper/search-keywords.git

  # Go into the repository
  $ cd search-keywords

  # Run the app
  $ python3 search_keywords.py --help
```

### Download

You can [download](https://github.com/glenjasper/search-keywords/archive/master.zip) the latest installable version of _search-keywords_.

## How To Use

```sh  
  $ python3 search_keywords.py --help
  usage: search_keywords.py [-h] -ft FOLDER_TXT -fp FOLDER_PDF -kw KEYWORDS
                            [-o OUTPUT] [--version]

  This script searches for the keywords, found in a .txt file, in the 'Materials
  and Methods' section of each .txt file (created from .pdf files).

  optional arguments:
    -h, --help            show this help message and exit
    -ft FOLDER_TXT, --folder_txt FOLDER_TXT
                          Folder containing the .txt files
    -fp FOLDER_PDF, --folder_pdf FOLDER_PDF
                          Folder containing .pdf files, used at the end of the
                          search to make copies of .pdf files that meet the
                          condition in the 'Materials and Methods' section
    -kw KEYWORDS, --keywords KEYWORDS
                          .txt file containing keywords, there must be one
                          keyword for each line
    -o OUTPUT, --output OUTPUT
                          Output folder
    --version             show program's version number and exit

  Thank you!
```

## Author

* [Glen Jasper](https://github.com/glenjasper)

## Organization
* [Molecular and Computational Biology of Fungi Laboratory](https://sites.icb.ufmg.br/lbmcf/index.html) (LBMCF, ICB - **UFMG**, Belo Horizonte, Brazil).

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Mandatory Attribution

**Any use, distribution, or modification of this software must include the following attribution:**

> This software was developed by Glen Jasper (https://github.com/glenjasper), originally available at https://github.com/glenjasper/search-keywords
