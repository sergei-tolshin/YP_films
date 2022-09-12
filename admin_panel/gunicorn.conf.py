from multiprocessing import cpu_count

workers = cpu_count() * 2 + 1

port = 8000

address = '0.0.0.0'

bind = f'{address}:{port}'

accesslog = '-'
errorlog = '-'

limit_request_line = 8188
