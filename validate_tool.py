f = open('mau-don-xin-tam-tru/index.html', encoding='utf-8').read()
print(f'Lines: {len(f.splitlines())}  Bytes: {len(f.encode())}')
print('Has checkout JS hook:  ', 'showCheckoutModal' in f)
print('Has VietQR img url:    ', 'vietqr.io' in f)
print('Has SEO meta desc:     ', 'meta name="description"' in f)
print('Has SEO article block: ', 'Quy Trinh' in f or 'Chi Tiet' in f or 'Huong Dan' in f or 'Hướng Dẫn' in f)
print('Has pay unlock button: ', 'unlock-download-btn' in f)
print('\nAll checks passed!' if all([
    'showCheckoutModal' in f,
    'vietqr.io' in f,
    'unlock-download-btn' in f
]) else '\nSome checks failed — inspect html manually.')
