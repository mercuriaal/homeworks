import time


def logger(logger_file):
    def decorator(function):
        def wrapper(*args, **kwargs):
            with open(logger_file, 'a') as file:
                result = function(*args, **kwargs)
                file.write(f'Call time - {time.asctime()} \n'
                           f'Function name - {function.__name__} \n'
                           f'Arguments - {args}, {kwargs} \n'
                           f'Return result - {result} \n\n')
                return result
        return wrapper
    return decorator
