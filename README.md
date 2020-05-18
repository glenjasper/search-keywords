search-keywords
======================
[![License](https://poser.pugx.org/badges/poser/license.svg)](./LICENSE)

Script that searches for keywords in .txt files, in the "Materials &amp; Methods" section.

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
  $ sudo pip3 install pandas
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

  Script que faz a busca de palavras-chave em arquivos .txt, na seção 'Materials
  & Methods'

  optional arguments:
    -h, --help            show this help message and exit
    -ft FOLDER_TXT, --folder_txt FOLDER_TXT
                          Pasta que contem os arquivos .txt
    -fp FOLDER_PDF, --folder_pdf FOLDER_PDF
                          Pasta que contem os arquivos .pdf, usado no final da
                          busca para fazer uma copia dos .pdf que tem as
                          palavras-chave
    -kw KEYWORDS, --keywords KEYWORDS
                          Arquivo plano que contem as palavras-chave, uma
                          palavra-chave por linha
    -o OUTPUT, --output OUTPUT
                          Pasta de saida
    --version             show program's version number and exit

  Thank you!
```

## Author

* [Glen Jasper](https://github.com/glenjasper)

## Organization
* [Molecular and Computational Biology of Fungi Laboratory](http://lbmcf.pythonanywhere.com) (LBMCF, ICB - **UFMG**, Belo Horizonte, Brazil).

## License

Copyright (c) 2020 [Glen Jasper](https://github.com/glenjasper).

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

* Dr. Aristóteles Góes-Neto
* MSc. Rosimeire Floripes
* MSc. Joyce da Cruz Ferraz
