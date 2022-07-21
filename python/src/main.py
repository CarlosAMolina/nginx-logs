import lib
from timeit import default_timer as timer

# https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python#7370824

def print_duration(duration: float):
    unit_of_time = "s"
    if duration < 1:
        unit_of_time = "ms"
        duration = duration * 1000
    print(f"Time elapsed: {duration}{unit_of_time}")

if __name__ == "__main__":
    start = timer()
    args = lib.get_args_parsed()
    lib.run(args)
    end = timer()
    duration = end - start
    print_duration(duration)
