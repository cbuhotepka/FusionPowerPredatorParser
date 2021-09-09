
if auto_parse and delimiter and (utils.is_simple_file(PATTERN_TEL_PASS, file)):
    keys, colsname_plain = utils.get_keys('1=tel, 2=password')
    all_files_status.add('pass')
    gl_num_columns = 1
    console.print('[cyan]' + 'Автопарсинг tel password')
    console.print(f'[magenta]Разделитель[/magenta]: "[red]{delimiter}[/red]"')
elif auto_parse and delimiter and (utils.is_simple_file(PATTERN_USERMAIL_USERNAME_PASS, file)):
    keys, colsname_plain = utils.get_keys(f'1=user_mail_name, 2=password')
    all_files_status.add('pass')
    gl_num_columns = 1
    console.print('[cyan]' + f'Автопарсинг umn password')
    console.print(f'[magenta]Разделитель[/magenta]: "[red]{delimiter}[/red]"')