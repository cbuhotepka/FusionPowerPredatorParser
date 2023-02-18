import os
import openpyxl


def search_words_in_files(folder_path, words_list):
    # Перебираем все файлы в папке
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # Получаем полный путь до файла
            file_path = os.path.join(root, file_name)
            # Ищем нужные слова в файле Excel
            if file_name.endswith('.xlsx') or file_name.endswith('.xlsm') or file_name.endswith('.xls'):
                workbook = openpyxl.load_workbook(file_path)
                for sheet_name in workbook.sheetnames:
                    sheet = workbook[sheet_name]
                    for row in sheet.iter_rows():
                        for cell in row:
                            # Проверяем, содержит ли ячейка нужное слово
                            for word in words_list:
                                if word in str(cell.value):
                                    print(
                                        f'Слово "{word}" найдено в ячейке {cell.coordinate} на листе {sheet_name} в файле {file_path}')
            # Ищем нужные слова в остальных файлах
            else:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    for line in file:
                        # Проверяем, содержит ли строка нужное слово
                        for word in words_list:
                            if word in line:
                                print(f'Слово "{word}" найдено в файле {file_path}')


def search_words_in_excel_files(folder_path, words_list):
    # Перебираем все файлы в папке
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # Получаем полный путь до файла
            file_path = os.path.join(root, file_name)
            # Ищем нужные слова в файле Excel
            if file_name.endswith('.xlsx') or file_name.endswith('.xlsm'):
                workbook = openpyxl.load_workbook(file_path)
                for sheet_name in workbook.sheetnames:
                    sheet = workbook[sheet_name]
                    for row in sheet.iter_rows():
                        for cell in row:
                            # Проверяем, содержит ли ячейка нужное слово
                            for word in words_list:
                                if word in str(cell.value):
                                    print(
                                        f'Слово "{word}" найдено в ячейке {cell.coordinate} на листе {sheet_name} в файле {file_path}')
