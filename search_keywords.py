#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import shutil
import argparse
import traceback
import xlsxwriter
import numpy as np
import pandas as pd
from colorama import init
init()

def menu():
    parser = argparse.ArgumentParser(description = "This script searches for the keywords, found in a .txt file, in the 'Materials and Methods' section of each .txt file (created from .pdf files).", epilog = "Thank you!")
    parser.add_argument("-ft", "--folder_txt", required = True, help = "Folder containing the .txt files")
    parser.add_argument("-fp", "--folder_pdf", required = True, help = "Folder containing .pdf files, used at the end of the search to make copies of .pdf files that meet the condition in the 'Materials and Methods' section")
    parser.add_argument("-kw", "--keywords", required = True, help = ".txt file containing keywords, there must be one keyword for each line")
    parser.add_argument("-o", "--output", help = "Output folder")
    parser.add_argument("--version", action = "version", version = "%s %s" % ('%(prog)s', osk.VERSION))
    args = parser.parse_args()

    folder_name = os.path.basename(args.folder_txt)
    folder_path = os.path.dirname(args.folder_txt)
    if folder_path is None or folder_path == "":
        folder_path = os.getcwd().strip()

    osk.FOLDER_TXT = os.path.join(folder_path, folder_name)
    if not osk.check_path(osk.FOLDER_TXT):
        osk.show_print("%s: error: the folder '%s' doesn't exist" % (os.path.basename(__file__), osk.FOLDER_TXT), showdate = False, font = osk.YELLOW)
        osk.show_print("%s: error: the following arguments are required: -ft/--folder_txt" % os.path.basename(__file__), showdate = False, font = osk.YELLOW)
        exit()

    folder_name = os.path.basename(args.folder_pdf)
    folder_path = os.path.dirname(args.folder_pdf)
    if folder_path is None or folder_path == "":
        folder_path = os.getcwd().strip()

    osk.FOLDER_PDF = os.path.join(folder_path, folder_name)
    if not osk.check_path(osk.FOLDER_PDF):
        osk.show_print("%s: error: the folder '%s' doesn't exist" % (os.path.basename(__file__), osk.FOLDER_TXT), showdate = False, font = osk.YELLOW)
        osk.show_print("%s: error: the following arguments are required: -fp/--folder_pdf" % os.path.basename(__file__), showdate = False, font = osk.YELLOW)
        exit()

    # osk.SECTION = args.section

    kw_file_name = os.path.basename(args.keywords)
    kw_file_path = os.path.dirname(args.keywords)
    if kw_file_path is None or kw_file_path == "":
        kw_file_path = os.getcwd().strip()

    osk.KEYWORDS = os.path.join(kw_file_path, kw_file_name)
    if not osk.check_path(osk.KEYWORDS):
        osk.show_print("%s: error: the file '%s' doesn't exist" % (os.path.basename(__file__), osk.KEYWORDS), showdate = False, font = osk.YELLOW)
        osk.show_print("%s: error: the following arguments are required: -kw/--keywords" % os.path.basename(__file__), showdate = False, font = osk.YELLOW)
        exit()

    if args.output is not None:
        output_name = os.path.basename(args.output)
        output_path = os.path.dirname(args.output)
        if output_path is None or output_path == "":
            output_path = os.getcwd().strip()

        osk.OUTPUT_PATH = os.path.join(output_path, output_name)
        created = osk.create_directory(osk.OUTPUT_PATH)
        if not created:
            osk.show_print("%s: error: Couldn't create folder '%s'" % (os.path.basename(__file__), osk.OUTPUT_PATH), showdate = False, font = osk.YELLOW)
            exit()
    else:
        osk.OUTPUT_PATH = os.getcwd().strip()
        osk.OUTPUT_PATH = os.path.join(osk.OUTPUT_PATH, 'output_searchkw')
        osk.create_directory(osk.OUTPUT_PATH)

class SearchKW:

    def __init__(self):
        self.VERSION = 1.0

        self.KEYWORDS = None
        self.FOLDER_TXT = None
        self.FOLDER_PDF = None
        self.SECTION = None
        self.OUTPUT_PATH = None
        self.OUTPUT_PDF = 'PDFs'

        self.ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
        self.LOG_NAME = "run_%s_%s.log" % (os.path.splitext(os.path.basename(__file__))[0], time.strftime('%Y%m%d'))
        self.LOG_FILE = None

        # Xls Summary
        self.XLS_FILE_CONVERTED = 'summary_converted.xlsx'
        self.XLS_FILE = 'kw_search_result.xlsx'
        self.XLS_SHEET_UNIQUE = 'Unique'
        self.XLS_SHEET_SELECTED = 'Selected'
        self.XLS_SHEET_NPAPERS_BY_KWS = '# Papers by KWs'

        # Xls Columns
        self.xls_col_item = 'Item'
        self.xls_col_title = 'Title'
        self.xls_col_abstract = 'Abstract'
        self.xls_col_year = 'Year'
        self.xls_col_doi = 'DOI'
        self.xls_col_document_type = 'Document Type'
        self.xls_col_languaje = 'Language'
        self.xls_col_cited_by = 'Cited By'
        self.xls_col_repository = 'Repository'
        self.xls_col_txt_name = 'TXT Name'
        self.xls_col_converted = 'Status'

        self.xls_col_kw = 'Keyword'
        self.xls_col_npapers = '# Papers'

        self.xls_columns = [self.xls_col_item]

        self.xls_columns_kws = [self.xls_col_item,
                                self.xls_col_kw,
                                self.xls_col_npapers]

        # Sections
        self.SECTION_ABSTRACT = 'ABSTRACT'
        self.SECTION_KEYWORDS = 'KEYWORDS'
        self.SECTION_INTRODUCTION = 'INTRODUCTION'
        self.SECTION_LITERATURE_REVIEW = 'LITERATURE_REVIEW'
        self.SECTION_METHODS = 'METHODS'
        self.SECTION_RESULTS = 'RESULTS'
        self.SECTION_RESULTS_DISCUSSION = 'RESULTS_DISCUSSION'
        self.SECTION_DISCUSSION = 'DISCUSSION'
        self.SECTION_CONCLUSIONS = 'CONCLUSIONS'
        self.SECTION_DISCUSSION_CONCLUSIONS = 'DISCUSSION_CONCLUSIONS'
        self.SECTION_SUMMARY = 'SUMMARY'
        self.SECTION_RECOMMENDATIONS = 'RECOMMENDATIONS'
        self.SECTION_ACKNOWLEDGEMENTS = 'ACKNOWLEDGEMENTS'
        self.SECTION_REFERENSES = 'REFERENSES'

        self.AFTER_METHOD = [self.SECTION_RESULTS,
                             self.SECTION_RESULTS_DISCUSSION,
                             self.SECTION_DISCUSSION,
                             self.SECTION_CONCLUSIONS,
                             self.SECTION_DISCUSSION_CONCLUSIONS,
                             self.SECTION_SUMMARY,
                             self.SECTION_RECOMMENDATIONS,
                             self.SECTION_ACKNOWLEDGEMENTS,
                             self.SECTION_REFERENSES]

        self.STATUS_OK = 'Ok'

        # Fonts
        self.RED = '\033[31m'
        self.GREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BIRED = '\033[1;91m'
        self.BIGREEN = '\033[1;92m'
        self.END = '\033[0m'

    def show_print(self, message, logs = None, showdate = True, font = None, end = None):
        msg_print = message
        msg_write = message

        if font is not None:
            msg_print = "%s%s%s" % (font, msg_print, self.END)

        if showdate is True:
            _time = time.strftime('%Y-%m-%d %H:%M:%S')
            msg_print = "%s %s" % (_time, msg_print)
            msg_write = "%s %s" % (_time, message)

        print(msg_print, end = end)
        if logs is not None:
            for log in logs:
                if log is not None:
                    with open(log, 'a', encoding = 'utf-8') as f:
                        f.write("%s\n" % msg_write)
                        f.close()

    def start_time(self):
        return time.time()

    def finish_time(self, start, message = None):
        finish = time.time()
        runtime = time.strftime("%H:%M:%S", time.gmtime(finish - start))
        if message is None:
            return runtime
        else:
            return "%s: %s" % (message, runtime)

    def create_directory(self, path):
        output = True
        try:
            if len(path) > 0 and not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            output = False
        return output

    def check_path(self, path):
        _check = False
        if path is not None:
            if len(path) > 0 and os.path.exists(path):
                _check = True
        return _check

    # https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
    def walklevel(self, some_dir, level = 1):
        some_dir = some_dir.rstrip(os.path.sep)
        assert os.path.isdir(some_dir)
        num_sep = some_dir.count(os.path.sep)
        for root, dirs, files in os.walk(some_dir):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs[:]

    def count_files(self, directory, extension = 'pdf'):
        count = 0
        for root, dirnames, filenames in self.walklevel(directory):
            for filename in filenames:
                if re.search('\.(%s)$' % extension, filename):
                    count += 1
        return count

    def read_xls(self):
        dict_txt = {}
        if self.check_path(self.XLS_FILE_CONVERTED):
            df = pd.read_excel(io = self.XLS_FILE_CONVERTED, sheet_name = self.XLS_SHEET_UNIQUE)
            # df = df.where(pd.notnull(df), None)
            df = df.replace({np.nan: None})

            for idx, row in df.iterrows():
                if row[self.xls_col_converted] == self.STATUS_OK:
                    collect = {}
                    collect[self.xls_col_title] = row[self.xls_col_title]
                    collect[self.xls_col_abstract] = row[self.xls_col_abstract]
                    collect[self.xls_col_year] = row[self.xls_col_year]
                    collect[self.xls_col_doi] = row[self.xls_col_doi]
                    collect[self.xls_col_document_type] = row[self.xls_col_document_type]
                    collect[self.xls_col_languaje] = row[self.xls_col_languaje]
                    collect[self.xls_col_cited_by] = row[self.xls_col_cited_by]
                    collect[self.xls_col_repository] = row[self.xls_col_repository]
                    collect[self.xls_col_txt_name] = row[self.xls_col_txt_name]
                    dict_txt.update({row[self.xls_col_txt_name]: collect})

        return dict_txt

    def read_kws(self):
        kws = []
        with open(self.KEYWORDS, 'r') as fr:
            for line in fr:
                line = line.strip()
                if line != '':
                    kws.append(line)
        fr.close()

        return kws

    def t2r(self, text, dot = '[⋅]?', opcional = False):
        text_re = ''
        for character in text.strip():
            if len(character.strip()) == 0:
                text_re += '[⋅]'
            elif character == '-':
                text_re += '[-]?'
            else:
                if opcional:
                    text_re += '[%s%s]?%s' % (character.upper(), character.lower(), dot)
                else:
                    text_re += '[%s%s]%s' % (character.upper(), character.lower(), dot)
        if text != '' and dot != '':
            text_re = text_re[:-len(dot)]
        return text_re

    def t2r_kw(self, text):
        # special_left = '(?<!\w|\-|[!@#$%^&*+%=—])'
        # special_right = '(?!\w|\-|[!@#$%^&*+%=—])'
        # options = ['^<text>$',
        #            '^<text>%s' % special_right,
        #            '%s<text>$' % special_left,
        #            '%s<text>%s' % (special_left, special_right)]

        special_left = '(?<!\w|[!@#$%^&*+%=])'
        special_right = '(?!\w|[!@#$%^&*+%=])'
        options = ['%s<text>%s' % (special_left, special_right)]

        text_re = ''
        for character in text.strip():
            if len(character.strip()) == 0:
                text_re += '[\s]'
            elif character.isalpha():
                text_re += '[%s%s]' % (character.upper(), character.lower())
            else:
                text_re += '[%s]' % character

        options_re = []
        for item in options:
            options_re.append(item.replace('<text>', text_re))

        return options_re

    def re_search_sections_file(self, section, file, order):
        begin = '((\d\d?|[Ii][Xx]|[Ii][Vv]|[Vv]?[Ii]{0,3}|[Aa]|[Bb]|[Cc]|[Dd]|[Ee]|[Ff]|[Gg]|[Hh])(?!\w).{0,3}[⋅]{0,2})?'
        end = '(:|\.|-|—)?'
        ands = '[⋅]?([Aa][⋅]?[Nn][⋅]?[Dd]|[&]|[\/])[⋅]?'

        if section == self.SECTION_ABSTRACT:
            block1 = '^{abstract}{end}$'.format(end = end, abstract = self.t2r('abstract'))
            block2 = '^{abstract}(?!\)|[a-z]|[A-Z])'.format(abstract = self.t2r('abstract'))
            block3 = '^[S][⋅]?{ummary}{end}$'.format(end = end, ummary = self.t2r('ummary'))

            regexs = [block1, block2, block3]
        elif section == self.SECTION_KEYWORDS:
            block1 = '^{keyword}[⋅]?[Ss]?{end}$'.format(end = end, keyword = self.t2r('key-word'))
            block2 = '^{keyword}[⋅]?[Ss]?{end}'.format(end = end, keyword = self.t2r('key-word'))
            block3 = '^[I][⋅]?{ndex}[⋅]?[-]?{term}[⋅]?[Ss]?{end}'.format(end = end, ndex = self.t2r('ndex'), term = self.t2r('term'))

            regexs = [block1, block2, block3]
        elif section == self.SECTION_INTRODUCTION:
            block1 = '^{begin}[I][⋅]?{ntroduction}[⋅]?[Ss]?({ands}({project})?[⋅]?{background})?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ntroduction = self.t2r('ntroduction'),
                                project = self.t2r('project'),
                                background = self.t2r('background'))
            block2 = '^{begin}([T][⋅]?{heoretical}[⋅][Bb]|[B])?[⋅]?{ackground}({ands}{motivation})?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                heoretical = self.t2r('heoretical'),
                                ackground = self.t2r('ackground'),
                                motivation = self.t2r('motivation'))

            regexs = [block1, block2]
        elif section == self.SECTION_LITERATURE_REVIEW:
            block1 = '^{begin}{literature}[⋅]{review}([:][⋅]{experimental}|{ands}{data}[⋅]{collection})?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                literature = self.t2r('literature'),
                                review = self.t2r('review'),
                                experimental = self.t2r('experimental'),
                                data = self.t2r('data'),
                                collection = self.t2r('collection'))

            regexs = [block1]
        elif section == self.SECTION_METHODS:
            block1 = '^{begin}([E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅][Mm]|[R][⋅]?{esearch}[⋅][Mm]|[M])?[⋅]?{aterial}[⋅]?[Ss]?{ands}({experiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?|{test})?[⋅]?({method}[⋅]?[Ss]?|{methodology})[⋅]?({of_research}|{of_invest})?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                esearch = self.t2r('esearch'),
                                aterial = self.t2r('aterial'),
                                method = self.t2r('method'),
                                methodology = self.t2r('methodology'),
                                experiment = self.t2r('experiment'),
                                test = self.t2r('test'),
                                of_research = self.t2r('of research'),
                                of_invest = self.t2r('of investigations'))
            block2 = '^{begin}' \
                     '([M]{ethod}[⋅]?[Ss]?[⋅]?({ands}|[,])[⋅]?{material}[⋅]?[Ss]?({ands}{result}[⋅]?[Ss]?)?|' \
                     '([E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?({tion})?|[R][⋅]?{esearch})[⋅]?({ands})?({method}[⋅]?[Ss]?|{methodology})({ands}({material}[⋅]?[Ss]?|{result}[⋅]?[Ss]?))?)' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ethod = self.t2r('ethod'),
                                material = self.t2r('material'),
                                result = self.t2r('result'),
                                xperiment = self.t2r('xperiment'),
                                tion = self.t2r('tion'),
                                esearch = self.t2r('esearch'),
                                method = self.t2r('method'),
                                methodology = self.t2r('methodology'))
            block3 = '^{begin}[M][⋅]?{ethod}[⋅]?[Ss]?([⋅]{of}[⋅]|{ands})({instrumental}[⋅])?({investigation}|{research}|{study}|{analysis}|{test}[⋅]?[Ss]?|{standard}[⋅]?[Ss]?|{technique}[⋅]?[Ss]?){end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ethod = self.t2r('ethod'),
                                of = self.t2r('of'),
                                instrumental = self.t2r('instrumental'),
                                investigation = self.t2r('investigation'),
                                research = self.t2r('research'),
                                study = self.t2r('study'),
                                analysis = self.t2r('analysis'),
                                test = self.t2r('test'),
                                standard = self.t2r('standard'),
                                technique = self.t2r('technique'))
            block4 = '^{begin}[M][⋅]?{ethodology}([⋅]{of}[⋅]|{ands})?[⋅]?({description}|{application}|({the}[⋅])?{experiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?([⋅]{work})?|{inspection}|{analysis}){end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ethodology = self.t2r('ethodology'),
                                of = self.t2r('of'),
                                description = self.t2r('description'),
                                application = self.t2r('application'),
                                the = self.t2r('the'),
                                experiment = self.t2r('experiment'),
                                work = self.t2r('work'),
                                inspection = self.t2r('inspection'),
                                analysis = self.t2r('analysis'))
            block5 = '^{begin}' \
                     '([E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]({method}[⋅]?[Ss]?{ands}({condition}[⋅]?[Ss]?|{discussion})|({condition}[⋅]?[Ss]?[⋅])?{ands}({measuring}[⋅]?)?{method}[⋅]?[Ss]?)|' \
                     '[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?({tion})?[⋅]({apparatus}|{sample}[⋅]?[Ss]?)[⋅]{ands}{methodology}|' \
                     '([T][⋅]?{heory}|[M][⋅]?{odelling})[⋅]({ands})?{methodology})' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                method = self.t2r('method'),
                                condition = self.t2r('condition'),
                                discussion = self.t2r('discussion'),
                                measuring = self.t2r('measuring'),
                                tion = self.t2r('tion'),
                                apparatus = self.t2r('apparatus'),
                                sample = self.t2r('sample'),
                                methodology = self.t2r('methodology'),
                                heory = self.t2r('heory'),
                                odelling = self.t2r('odelling'))
            block6 = '^{begin}[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?[⋅]' \
                     '(({test}[⋅]?[Ss]?|{method}[⋅]?[Ss]?)?[⋅]?({ands})?{setup}[⋅]?[Ss]?[⋅]?({ands}({calculation})?[⋅]?({procedure}[⋅]?[Ss]?|{condition}[⋅]?[Ss]?|{apparatus}|{design}[⋅]?[Ss]?|{instrumentation}[⋅]?[Ss]?))?|' \
                     '({equipment}[⋅]?[Ss]?)?[⋅]?{ands}({test})?[⋅]?{method}[⋅]?[Ss]?)' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                test = self.t2r('test'),
                                method = self.t2r('method'),
                                setup = self.t2r('set-up'),
                                calculation = self.t2r('calculation'),
                                procedure = self.t2r('procedure'),
                                condition = self.t2r('condition'),
                                apparatus = self.t2r('apparatus'),
                                design = self.t2r('design'),
                                instrumentation = self.t2r('instrumentation'),
                                equipment = self.t2r('equipment'))
            block7 = '^{begin}[M][⋅]?{aterial}[⋅]?[Ss]?{ands}({procedure}[⋅]?[Ss]?|{experiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?)[⋅]?({of})?[⋅]?({research}|{investigation}[⋅]?[Ss]?|{experiment}[⋅]?[Ss]?|{procedure}[⋅]?[Ss]?|{condition}[⋅]?[Ss]?|{technique}[⋅]?[Ss]?|{work}[⋅]?[Ss]?)?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                aterial = self.t2r('aterial'),
                                procedure = self.t2r('procedure'),
                                experiment = self.t2r('experiment'),
                                of = self.t2r('of'),
                                research = self.t2r('research'),
                                investigation = self.t2r('investigation'),
                                condition = self.t2r('condition'),
                                technique = self.t2r('technique'),
                                work = self.t2r('work'))
            block8 = '^{begin}[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?[⋅]' \
                     '(({test}[⋅]?[Ss]?|{apparatus}|{condition}[⋅]?[Ss]?|{detail}[⋅]?[Ss]?|{equipment}[⋅]?[Ss]?|{material}[⋅]?[Ss]?)?[⋅]?({ands})?{procedure}[⋅]?[Ss]?[⋅]?({ands}{result}[⋅]?[Ss]?)?|' \
                     '({device}[⋅]?[Ss]?|{technique}[⋅]?[Ss]?|{work}[⋅]?[Ss]?)?[⋅]?({ands})?{material}[⋅]?[Ss]?)' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                test = self.t2r('test'),
                                apparatus = self.t2r('apparatus'),
                                condition = self.t2r('condition'),
                                detail = self.t2r('detail'),
                                equipment = self.t2r('equipment'),
                                material = self.t2r('material'),
                                procedure = self.t2r('procedure'),
                                result = self.t2r('result'),
                                device = self.t2r('device'),
                                technique = self.t2r('technique'),
                                work = self.t2r('work'))
            block9 = '^{begin}' \
                     '[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?[⋅]?' \
                     '({ands}({apparatus}|{application}[⋅]?[Ss]?|{result}[⋅]?[Ss]?|({simulation}[⋅]?[Ss]?)?[⋅]?{technique}[⋅]?[Ss]?)|' \
                     '{technique}[⋅]?[Ss]?|{apparatus}|{approach}|{background}|{condition}[⋅]?[Ss]?|{detail}[⋅]?[Ss]?|{development}|{investigation}[⋅]?[Ss]?|{outline}|{part}|{proced}|' \
                     '{program}[⋅]?[Mm]?[⋅]?[Ee]?[⋅]?[Ss]?|{research}|{scheme}|{section}[⋅]?[Ss]?|{setting}|{step}[⋅]?[Ss]?|{system}[⋅]?[Ss]?|{work}[⋅]?[Ss]?|{stud}[⋅]?[Ii]?[⋅]?[Ee]?[⋅]?[Ss]?[⋅]?[Yy]?({ands})?({analysis})?)' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                apparatus = self.t2r('apparatus'),
                                application = self.t2r('application'),
                                result = self.t2r('result'),
                                simulation = self.t2r('simulation'),
                                technique = self.t2r('technique'),
                                approach = self.t2r('approach'),
                                background = self.t2r('background'),
                                condition = self.t2r('condition'),
                                detail = self.t2r('detail'),
                                development = self.t2r('development'),
                                investigation = self.t2r('investigation'),
                                outline = self.t2r('outline'),
                                part = self.t2r('part'),
                                proced = self.t2r('proced'),
                                program = self.t2r('program'),
                                research = self.t2r('research'),
                                scheme = self.t2r('scheme'),
                                section = self.t2r('section'),
                                setting = self.t2r('setting'),
                                step = self.t2r('step'),
                                system = self.t2r('system'),
                                work = self.t2r('work'),
                                stud = self.t2r('stud'),
                                analysis = self.t2r('analysis'))
            block10 = '^{begin}' \
                      '([M][⋅]?{odel}[⋅]?({ling})?[⋅]?({development}|{strategy})[⋅]?[Ss]?|' \
                      '[M][⋅]?{ethod}[⋅]?({ical}[⋅]?[Ss]?|{ological}[⋅]?[Ss]?)?[⋅]?({study}|{approaches}|{procedure}[⋅]?[Ss]?)|' \
                      '[M][⋅]?{aterial}[⋅]?[Ss]?{ands}{testing}[⋅]{method}[⋅]?[Ss]?|' \
                      '[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?{ands}{simulation}[⋅]{methodolog}[⋅]?[Yy]?{ies}|' \
                      '[B][⋅]?{ackground}{ands}{method}[⋅]?[Ss]?|' \
                      '[R][⋅]?{esearch}[⋅]{technique}[⋅]?[Ss]?|' \
                      '[S][⋅]?{tudy}[⋅]{area}{ands}{method}[⋅]?[Ss]?|' \
                      '[T][⋅]?{esting}[⋅]{methodolog}[⋅]?([Yy]|{ies}))' \
                      '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                odel = self.t2r('odel'),
                                ling = self.t2r('ling'),
                                development = self.t2r('development'),
                                strategy = self.t2r('strategy'),
                                ethod = self.t2r('ethod'),
                                ical = self.t2r('ical'),
                                ological = self.t2r('ological'),
                                study = self.t2r('study'),
                                approaches = self.t2r('approaches'),
                                procedure = self.t2r('procedure'),
                                aterial = self.t2r('aterial'),
                                testing = self.t2r('testing'),
                                method = self.t2r('method'),
                                xperiment = self.t2r('xperiment'),
                                simulation = self.t2r('simulation'),
                                methodolog = self.t2r('methodolog'),
                                ies = self.t2r('ies'),
                                ackground = self.t2r('ackground'),
                                esearch = self.t2r('esearch'),
                                technique = self.t2r('technique'),
                                tudy = self.t2r('tudy'),
                                area = self.t2r('area'),
                                esting = self.t2r('esting'))
            block11 = '^{begin}([M][⋅]?{ethod}[⋅]?[Ss]?({olog})?[⋅]?[Yy]?({ies})?|[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?([Ll]|{tion})?[⋅]?[Ss]?){end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ethod = self.t2r('ethod'),
                                olog = self.t2r('olog'),
                                ies = self.t2r('ies'),
                                xperiment = self.t2r('xperiment'),
                                tion = self.t2r('tion'))

            regexs = [block1, block2, block3, block4, block5, block6, block7, block8, block9, block10, block11]
        elif section == self.SECTION_RESULTS:
            block1 = '^{begin}[R][⋅]?{esult}[⋅]?[Ss]?[⋅]?({ands}|{of})?[⋅]?' \
                     '({analysis}|{analyze}|{consideration}[⋅]?[Ss]?|{conclusion}[⋅]?[Ss]?|{comment}[⋅]?[Ss]?|{comparison}[⋅]?[Ss]?|{inference}[⋅]?[Ss]?|{interpretation}[⋅]?[Ss]?|' \
                     '{obtained}|{summary}|{presentation})?[⋅]?({of})?[⋅]?({the})?[⋅]?({experiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?)?[⋅]?({analysis}|{test}[⋅]?[Ss]?|{research}|{investigation})?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                esult = self.t2r('esult'),
                                of = self.t2r('of'),
                                analysis = self.t2r('analysis'),
                                analyze = self.t2r('analyze'),
                                consideration = self.t2r('consideration'),
                                conclusion = self.t2r('conclusion'),
                                comment = self.t2r('comment'),
                                comparison = self.t2r('comparison'),
                                inference = self.t2r('inference'),
                                interpretation = self.t2r('interpretation'),
                                obtained = self.t2r('obtained'),
                                summary = self.t2r('summary'),
                                presentation = self.t2r('presentation'),
                                the = self.t2r('the'),
                                experiment = self.t2r('experiment'),
                                test = self.t2r('test'),
                                research = self.t2r('research'),
                                investigation = self.t2r('investigation'),
                                )
            block2 = '^{begin}' \
                     '([E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?|[T][⋅]?{est}[⋅]?[Ss]?|[A][⋅]?{nalysis}|[A][⋅]?{nalytical}|[A][⋅]?{pproach}|[V][⋅]?{erification})' \
                     '[⋅]?({ands}|{of})?[⋅]?{result}[⋅]?[Ss]?({ands})?[⋅]?({analysis}|{observation}[⋅]?[Ss]?)?' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                est = self.t2r('est'),
                                nalysis = self.t2r('nalysis'),
                                nalytical = self.t2r('nalytical'),
                                pproach = self.t2r('pproach'),
                                erification = self.t2r('erification'),
                                of = self.t2r('of'),
                                result = self.t2r('result'),
                                analysis = self.t2r('analysis'),
                                observation = self.t2r('observation'))
            block3 = '^{begin}([E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?[⋅]({validation}|{verification})[⋅]?[Ss]?|[O][⋅]?{utcome}[⋅]{of_the_study}){end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                xperiment = self.t2r('xperiment'),
                                validation = self.t2r('validation'),
                                verification = self.t2r('verification'),
                                utcome = self.t2r('utcome'),
                                of_the_study = self.t2r('of the study'))

            regexs = [block1, block2, block3]
        elif section == self.SECTION_RESULTS_DISCUSSION:
            block1 = '^{begin}[D][⋅]?{iscussion}[⋅]?[Ss]?[⋅]?({ands}|{of}|{on})[⋅]?({the}[⋅])?{result}[⋅]?[Ss]?({ands}{conclusion}[⋅]?[Ss]?)?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                iscussion = self.t2r('iscussion'),
                                of = self.t2r('of'),
                                on = self.t2r('on'),
                                the = self.t2r('the'),
                                result = self.t2r('result'),
                                conclusion = self.t2r('conclusion'))
            block2 = '^{begin}([R][⋅]?{esult}[⋅]?[Ss]?|[A][⋅]?{nalysis}|[T][⋅]?{est}[⋅]?[Ss]?|[E][⋅]?{xperiment}[⋅]?[Aa]?[⋅]?[Ll]?[⋅]?[Ss]?)[⋅]?[,]?[⋅]?({analysis}|{result}[⋅]?[Ss]?)?{ands}{discussion}[⋅]?[Ss]?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                esult = self.t2r('esult'),
                                nalysis = self.t2r('nalysis'),
                                est = self.t2r('est'),
                                xperiment = self.t2r('xperiment'),
                                analysis = self.t2r('analysis'),
                                result = self.t2r('result'),
                                discussion = self.t2r('discussion'))

            regexs = [block1, block2]
        elif section == self.SECTION_DISCUSSION:
            block1 = '^{begin}[D][⋅]?{iscussion}[⋅]?[Ss]?[⋅]?' \
                     '({ands}({analysis}|{summary}|{concluding}[⋅]{remark}[⋅]?[Ss]?|{future}[⋅]({work}[⋅]?[Ss]?|{direction}[⋅]?[Ss]?)))?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                iscussion = self.t2r('iscussion'),
                                of = self.t2r('of'),
                                on = self.t2r('on'),
                                analysis = self.t2r('analysis'),
                                summary = self.t2r('summary'),
                                concluding = self.t2r('concluding'),
                                remark = self.t2r('remark'),
                                future = self.t2r('future'),
                                work = self.t2r('work'),
                                direction = self.t2r('direction'),
                                the = self.t2r('the'),
                                result = self.t2r('result'),
                                conclusion = self.t2r('conclusion'))
            block2 = '^{begin}([I][⋅]?{nterpretation}[⋅]?[Ss]?|[S][⋅]?{ummary}){ands}({analysis}|{discussion}[⋅]?[Ss]?){end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                nterpretation = self.t2r('nterpretation'),
                                ummary = self.t2r('ummary'),
                                analysis = self.t2r('analysis'),
                                discussion = self.t2r('discussion'))

            regexs = [block1, block2]
        elif section == self.SECTION_CONCLUSIONS:
            block1 = '^{begin}' \
                     '[C][⋅]?{onclusion}[⋅]?[Ss]?(({ands})?({future})?[⋅]?' \
                     '({work}[⋅]?[Ss]?|{direction}[⋅]?[Ss]?|{outlook}[⋅]?[Ss]?|{perspective}[⋅]?[Ss]?|{prospect}[⋅]?[Ss]?|{remark}[⋅]?[Ss]?|{scope}[⋅]?[Ss]?|' \
                     '{challenge}[⋅]?[Ss]?|{countermeasure}[⋅]?[Ss]?|{implication}[⋅]?[Ss]?|{recommendation}[⋅]?[Ss]?([⋅]{for_improvement})?|{suggestion}[⋅]?[Ss]?|{understanding}|' \
                     '{acknowledg}[⋅]?{ement}[⋅]?[Ss]?|{research}[⋅]{trend}[⋅]?[Ss]?|{practical}[⋅]{application}[⋅]?[Ss]?|{further}[⋅]{observation}[⋅]?[Ss]?))?' \
                     '{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                onclusion = self.t2r('onclusion'),
                                future = self.t2r('future'),
                                work = self.t2r('work'),
                                direction = self.t2r('direction'),
                                outlook = self.t2r('outlook'),
                                perspective = self.t2r('perspective'),
                                prospect = self.t2r('prospect'),
                                remark = self.t2r('remark'),
                                scope = self.t2r('scope'),
                                challenge = self.t2r('challenge'),
                                countermeasure = self.t2r('countermeasure'),
                                implication = self.t2r('implication'),
                                recommendation = self.t2r('recommendation'),
                                for_improvement = self.t2r('for improvement'),
                                suggestion = self.t2r('suggestion'),
                                understanding = self.t2r('understanding'),
                                acknowledg = self.t2r('acknowledg'),
                                ement = self.t2r('ement', opcional = True),
                                research = self.t2r('research'),
                                trend = self.t2r('trend'),
                                practical = self.t2r('practical'),
                                application = self.t2r('application'),
                                further = self.t2r('further'),
                                observation = self.t2r('observation'))
            block2 = '^{begin}[S][⋅]?{ummary}{ands}{conclusion}[⋅]?[Ss]?{end}$'.format(begin = begin, end = end, ands = ands, ummary = self.t2r('ummary'), conclusion = self.t2r('conclusion'))
            block3 = '^{begin}{final}[⋅]{consideration}[⋅]?[Ss]?{end}$'.format(begin = begin, end = end, final = self.t2r('final'), consideration = self.t2r('consideration'))
            block4 = '^[C][⋅]?{onclusion}[⋅]?[Ss]?(:|\.)'.format(onclusion = self.t2r('onclusion'))

            regexs = [block1, block2, block3, block4]
        elif section == self.SECTION_DISCUSSION_CONCLUSIONS:
            block1 = '^{begin}[D][⋅]?{iscussion}[⋅]?[Ss]?{ands}{conclusion}[⋅]?[Ss]?{end}$'.format(begin = begin, end = end, ands = ands, iscussion = self.t2r('iscussion'), conclusion = self.t2r('conclusion'))
            block2 = '^{begin}[C][⋅]?{onclusion}[⋅]?[Ss]?{ands}{discussion}[⋅]?[Ss]?{end}$'.format(begin = begin, end = end, ands = ands, onclusion = self.t2r('onclusion'), discussion = self.t2r('discussion'))

            regexs = [block1, block2]
        elif section == self.SECTION_SUMMARY:
            block1 = '^{begin}[S][⋅]?{ummary}({ands}({future}[⋅]({work}[⋅]?[Ss]?|{outlook}[⋅]?[Ss]?|{trend}[⋅]?[Ss]?)|{outlook}[⋅]?[Ss]?|{prospect}[⋅]?[Ss]?|{concluding}[⋅]{remark}[⋅]?[Ss]?|{further}[⋅]{work}[⋅]?[Ss]?)|[⋅]{of}[⋅]({statistical})?[⋅]?{result}[⋅]?[Ss]?)?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ummary = self.t2r('ummary'),
                                future = self.t2r('future'),
                                work = self.t2r('work'),
                                outlook = self.t2r('outlook'),
                                trend = self.t2r('trend'),
                                prospect = self.t2r('prospect'),
                                concluding = self.t2r('concluding'),
                                remark = self.t2r('remark'),
                                further = self.t2r('further'),
                                of = self.t2r('of'),
                                statistical = self.t2r('statistical'),
                                result = self.t2r('result'))

            regexs = [block1]
        elif section == self.SECTION_RECOMMENDATIONS:
            block1 = '^{begin}[R][⋅]?{ecommendation}[⋅]?[Ss]?({ands}|[⋅]{For})?[⋅]?({repair}[⋅]?[Ss]?|({the})?[⋅]?{future}[⋅]?({study}|{work}[⋅]?[Ss]?|{research}[⋅]?[Ss]?))?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ecommendation = self.t2r('ecommendation'),
                                For = self.t2r('for'),
                                repair = self.t2r('repair'),
                                the = self.t2r('the'),
                                future = self.t2r('future'),
                                study = self.t2r('study'),
                                work = self.t2r('work'),
                                research = self.t2r('research'))

            regexs = [block1]
        elif section == self.SECTION_ACKNOWLEDGEMENTS:
            block1 = '^{begin}[A][⋅]?{cknowledg}[⋅]?{ement}[⋅]?[Ss]?{end}'.format(begin = begin, end = end, cknowledg = self.t2r('cknowledg'), ement = self.t2r('ement', opcional = True))

            regexs = [block1]
        elif section == self.SECTION_REFERENSES:
            begin = '(\d.{0,4}[⋅]{0,2})?'
            block1 = '^{begin}{bibliography}{end}$'.format(begin = begin, end = end, bibliography = self.t2r('bibliography'))
            block2 = '^{begin}[L][⋅]?{iterature}[⋅]{cited}{end}$'.format(begin = begin, end = end, iterature = self.t2r('iterature'), cited = self.t2r('cited'))
            block3 = '^{begin}([L][⋅]?{ist_of}[⋅])?{reference}[⋅]?[Ss]?([⋅]{cited}|{ands}{notes})?{end}$' \
                        .format(begin = begin,
                                end = end,
                                ands = ands,
                                ist_of = self.t2r('ist of'),
                                reference = self.t2r('reference'),
                                cited = self.t2r('cited'),
                                notes = self.t2r('notes'))

            regexs = [block1, block2, block3]

        for index_re, regex in enumerate(regexs):
            pattern = re.compile(regex)

            done = False
            with open(file, 'r') as fr:
                for nline, line in enumerate(fr, start = 1):
                    line = line.strip()
                    line = line.replace('\t', '⋅').replace(' ', '⋅').replace(' ', '⋅').replace(' ', '⋅')
                    result = pattern.search(line)

                    if result:
                        # self.show_print('[[%s]] %s, %s' % (index_re, nline, line), [self.LOG_FILE], font = self.YELLOW)

                        if section in [self.SECTION_ABSTRACT, self.SECTION_KEYWORDS, self.SECTION_INTRODUCTION, self.SECTION_METHODS, self.SECTION_SUMMARY]:
                            if section not in order:
                                update = True
                                # Validation Abstract/Summary
                                if section == self.SECTION_SUMMARY and self.SECTION_ABSTRACT in order:
                                    if order[self.SECTION_ABSTRACT] == nline:
                                        update = False
                                if update:
                                    order.update({section: nline})
                                    done = True
                                    break
                        else:
                            order.update({section: nline})
                if done:
                    break
            fr.close()

    def search_keyword(self, dict_section, file, dict_by_kw):
        nline_begin = 0
        nline_end = 0
        finded = False

        if self.SECTION_METHODS in dict_section.values():
            check = False
            for index, (nline, section) in enumerate(dict_section.items()):
                if section == self.SECTION_METHODS:
                    nline_begin = nline
                    check = True
                    continue
                if check:
                    if section in self.AFTER_METHOD:
                        nline_end = nline
                        check = False
                        break

            # gyg
            # https://github.com/kouroshparsa/toned.git
            if nline_begin > 0 and nline_end > 0:
                with open(file, 'r') as fr:
                    for nline, line in enumerate(fr, start = 1):
                        # Block M&M
                        if nline_begin < nline and nline < nline_end:
                            for word in self.KEYWORDS:
                                options_re = self.t2r_kw(word.strip())
                                for regex in options_re:
                                    pattern = re.compile(regex)

                                    result = pattern.search(line.strip())
                                    if result:
                                        _list = dict_by_kw[word].copy()
                                        _file = os.path.basename(file)
                                        if _file not in _list:
                                            _list.append(_file)
                                            dict_by_kw.update({word: _list})
                fr.close()

    def save_results_xls(self, dict_by_kw):
        uniq_files = {}
        keywords = {}
        for word, files in dict_by_kw.items():
            if len(files) > 0:
                keywords.update({word: files})

                for file in files:
                    if file not in uniq_files:
                        uniq_files.update({file: []})

        txt_info = self.read_xls()
        if len(txt_info) > 0:
            self.xls_columns.append(self.xls_col_title)
            self.xls_columns.append(self.xls_col_abstract)
            self.xls_columns.append(self.xls_col_year)
            self.xls_columns.append(self.xls_col_doi)
            self.xls_columns.append(self.xls_col_document_type)
            self.xls_columns.append(self.xls_col_languaje)
            self.xls_columns.append(self.xls_col_cited_by)
            self.xls_columns.append(self.xls_col_repository)
        self.xls_columns.append(self.xls_col_txt_name)

        for word, files in keywords.items():
            self.xls_columns.append(word)
            for file in files:
                current_kws = uniq_files[file].copy()
                current_kws.append(word)
                uniq_files.update({file: sorted(current_kws)})
        uniq_files = {item[0]: item[1] for item in sorted(uniq_files.items(), reverse = True)}

        data_result = []
        for index, (file, kws) in enumerate(uniq_files.items(), start = 1):
            line = [index]
            if file in txt_info.keys():
                line.append(txt_info[file][self.xls_col_title])
                line.append(txt_info[file][self.xls_col_abstract])
                line.append(txt_info[file][self.xls_col_year])
                line.append(txt_info[file][self.xls_col_doi])
                line.append(txt_info[file][self.xls_col_document_type])
                line.append(txt_info[file][self.xls_col_languaje])
                line.append(txt_info[file][self.xls_col_cited_by])
                line.append(txt_info[file][self.xls_col_repository])
                line.append(txt_info[file][self.xls_col_txt_name])
            else:
                line.append(file)

            for kw in keywords.keys():
                status = 'Ok' if kw in kws else ''
                line.append(status)
            data_result.append(line)

        data_search = {self.XLS_SHEET_SELECTED: data_result,
                       self.XLS_SHEET_NPAPERS_BY_KWS: dict_by_kw}

        self.save_xls(data_search)

    def save_xls(self, data):

        def create_sheet(oworkbook, sheet_type, data_list, styles_title, styles_rows, styles_row_kws):
            is_full = False
            if sheet_type == self.XLS_SHEET_SELECTED:
                _xls_columns = self.xls_columns.copy()
                if self.xls_col_doi in _xls_columns:
                    is_full = True
            else:
                _xls_columns = self.xls_columns_kws.copy()

            _last_col = len(_xls_columns) - 1

            worksheet = oworkbook.add_worksheet(sheet_type)
            worksheet.freeze_panes(row = 1, col = 0) # Freeze the first row.
            worksheet.autofilter(first_row = 0, first_col = 0, last_row = 0, last_col = _last_col)
            worksheet.set_default_row(height = 14.5)

            # Add columns
            for icol, column in enumerate(_xls_columns):
                worksheet.write(0, icol, column, styles_title)

            # Add rows
            worksheet.set_column(first_col = 0, last_col = 0, width = 7)  # Column A:A
            if sheet_type == self.XLS_SHEET_SELECTED:
                worksheet.set_column(first_col = 1, last_col = 1, width = 30) # Column B:B
                _start = 2
                if is_full:
                    worksheet.set_column(first_col = 2, last_col = 2, width = 33) # Column C:C
                    worksheet.set_column(first_col = 3, last_col = 3, width = 8)  # Column D:D
                    worksheet.set_column(first_col = 4, last_col = 4, width = 30) # Column E:E
                    worksheet.set_column(first_col = 5, last_col = 5, width = 18) # Column F:F
                    worksheet.set_column(first_col = 6, last_col = 6, width = 12) # Column G:G
                    worksheet.set_column(first_col = 7, last_col = 7, width = 11) # Column H:H
                    worksheet.set_column(first_col = 8, last_col = 8, width = 13) # Column I:I
                    worksheet.set_column(first_col = 9, last_col = 9, width = 30) # Column J:J
                    _start = 10
                for icol, kw in enumerate(_xls_columns[_start:], start = _start):
                    worksheet.set_column(first_col = icol, last_col = icol, width = len(kw) * 1.2)
            else:
                worksheet.set_column(first_col = 1, last_col = 1, width = 17) # Column B:B
                worksheet.set_column(first_col = 2, last_col = 2, width = 12) # Column C:C

            if sheet_type == self.XLS_SHEET_SELECTED:
                for irow, item in enumerate(data_list, start = 1):
                    _icol = 9 if is_full else 1
                    for icol, vcolumn in enumerate(item):
                        cell_style = styles_rows if icol <= _icol else styles_row_kws
                        worksheet.write(irow, icol, vcolumn, cell_style)
            else:
                icol = 0
                for irow, (word, files) in enumerate(data_list.items(), start = 1):
                    worksheet.write(irow, icol + 0, irow, styles_rows)
                    worksheet.write(irow, icol + 1, word, styles_rows)
                    worksheet.write(irow, icol + 2, len(files), styles_row_kws)

        workbook = xlsxwriter.Workbook(self.XLS_FILE)

        # Styles
        cell_format_title = workbook.add_format({'bold': True,
                                                 'font_color': 'white',
                                                 'bg_color': 'black',
                                                 'align': 'center',
                                                 'valign': 'vcenter'})
        cell_format_row = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        cell_format_row_kw = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

        create_sheet(workbook, self.XLS_SHEET_SELECTED, data[self.XLS_SHEET_SELECTED], cell_format_title, cell_format_row, cell_format_row_kw)
        create_sheet(workbook, self.XLS_SHEET_NPAPERS_BY_KWS, data[self.XLS_SHEET_NPAPERS_BY_KWS], cell_format_title, cell_format_row, cell_format_row_kw)

        workbook.close()

    def copy_pdfs(self, dict_by_kw):

        def get_pdf(pdfname, extension = 'pdf'):
            count = 0
            pdf_result = None
            for root, dirnames, filenames in self.walklevel(self.FOLDER_PDF):
                for filename in filenames:
                    if re.search('\.(%s)$' % extension, filename):
                        if pdfname == filename:
                            pdf_result = os.path.join(root, filename)
            return pdf_result

        txt_info = self.read_xls()
        pdf_info = {}
        for txtname, item in txt_info.items():
            txtname, _ = os.path.splitext(txtname)
            pdfname = '%s.pdf' % txtname
            collect = {}
            collect[self.xls_col_document_type] = item[self.xls_col_document_type]
            pdf_info.update({pdfname: collect})

        pdfs = []
        for kw, files in dict_by_kw.items():
            for filename in files:
                filename, _ = os.path.splitext(filename)
                pdffile = '%s.pdf' % filename
                if pdffile not in pdfs:
                    pdfs.append(pdffile)

                    folder_out = self.OUTPUT_PDF
                    if pdffile in pdf_info:
                        folder_type = pdf_info[pdffile][self.xls_col_document_type]
                        folder_in = os.path.join(self.FOLDER_PDF, folder_type)
                        folder_out = os.path.join(self.OUTPUT_PDF, folder_type)

                        pdffile = os.path.join(folder_in, pdffile)
                    else:
                        pdffile = get_pdf(pdffile)

                    # Copying
                    if self.check_path(pdffile):
                        self.create_directory(folder_out)
                        shutil.copy(pdffile, folder_out)
        return pdfs

    def print_keywords(self):
        keywords_by_row = []
        row = []
        for kw in self.KEYWORDS:
            len_row = len(', '.join(row))

            if len_row + len(kw) <= 140:
                row.append(kw)
            else:
                keywords_by_row.append(row)
                row = []
        if len(row) > 0:
            keywords_by_row.append(row)

        for row in keywords_by_row:
            self.show_print("  %s" % ', '.join(row), [self.LOG_FILE], font = self.GREEN)

def main():
    try:
        start = osk.start_time()
        menu()

        osk.LOG_FILE = os.path.join(osk.OUTPUT_PATH, osk.LOG_NAME)
        osk.XLS_FILE = os.path.join(osk.OUTPUT_PATH, osk.XLS_FILE)
        osk.XLS_FILE_CONVERTED = os.path.join(osk.FOLDER_TXT, osk.XLS_FILE_CONVERTED)
        osk.OUTPUT_PDF = os.path.join(osk.OUTPUT_PATH, osk.OUTPUT_PDF)
        osk.create_directory(osk.OUTPUT_PDF)
        osk.KEYWORDS = osk.read_kws()
        osk.show_print("#############################################################################", [osk.LOG_FILE], font = osk.BIGREEN)
        osk.show_print("############################## Search Keywords ##############################", [osk.LOG_FILE], font = osk.BIGREEN)
        osk.show_print("#############################################################################", [osk.LOG_FILE], font = osk.BIGREEN)
        total = osk.count_files(osk.FOLDER_TXT, extension = 'txt')

        osk.show_print("Text files to analyze: %s" % total, [osk.LOG_FILE], font = osk.GREEN)
        osk.show_print("Keywords search (%s):" % len(osk.KEYWORDS), [osk.LOG_FILE], font = osk.GREEN)
        osk.print_keywords()
        osk.show_print("", [osk.LOG_FILE])
 
        txt_by_kw = {word: [] for word in osk.KEYWORDS}
        count = 1
        for root, dirnames, filenames in osk.walklevel(osk.FOLDER_TXT):
            for filename in filenames:
                if re.search('\.(txt)$', filename):
                    osk.show_print("[%s/%s] Reading the file: %s..." % (count, total, filename[:50]), [osk.LOG_FILE], end = '\r')
                    txtfile = os.path.join(root, filename)

                    order_section = {}
                    osk.re_search_sections_file(osk.SECTION_ABSTRACT, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_KEYWORDS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_INTRODUCTION, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_LITERATURE_REVIEW, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_METHODS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_RESULTS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_RESULTS_DISCUSSION, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_DISCUSSION, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_CONCLUSIONS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_DISCUSSION_CONCLUSIONS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_SUMMARY, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_RECOMMENDATIONS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_ACKNOWLEDGEMENTS, txtfile, order_section)
                    osk.re_search_sections_file(osk.SECTION_REFERENSES, txtfile, order_section)

                    reorder_section = {value: key for key, value in order_section.items()}
                    reorder_section = {item[0]: item[1] for item in sorted(reorder_section.items())}

                    osk.search_keyword(reorder_section, txtfile, txt_by_kw)
                    count += 1
        osk.show_print("")
        osk.show_print("", [osk.LOG_FILE])

        osk.save_results_xls(txt_by_kw)
        pdfs = osk.copy_pdfs(txt_by_kw)
        osk.show_print("Results file: %s" % osk.XLS_FILE, [osk.LOG_FILE], font = osk.GREEN)
        osk.show_print("Results folder: %s" % osk.OUTPUT_PDF, [osk.LOG_FILE], font = osk.GREEN)
        osk.show_print("  # Papers: %s" % len(pdfs), [osk.LOG_FILE], font = osk.GREEN)

        osk.show_print("", [osk.LOG_FILE])
        osk.show_print(osk.finish_time(start, "Elapsed time"), [osk.LOG_FILE])
        osk.show_print("Done!", [osk.LOG_FILE])
    except Exception as e:
        osk.show_print("\n%s" % traceback.format_exc(), [osk.LOG_FILE], font = osk.RED)
        osk.show_print(osk.finish_time(start, "Elapsed time"), [osk.LOG_FILE])
        osk.show_print("Done!", [osk.LOG_FILE])

if __name__ == '__main__':
    osk = SearchKW()
    main()
