import time


def logger(logger_file):
    def decorator(function):
        def wrapper(*args, **kwargs):
            with open(logger_file, 'a') as file:
                file.write(f'Call time - {time.asctime()} \n'
                           f'Function name - {function.__name__} \n'
                           f'Arguments - {args}, {kwargs} \n'
                           f'Return result - {function(*args, **kwargs)} \n\n')
        return wrapper
    return decorator
