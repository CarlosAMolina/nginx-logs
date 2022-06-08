import lib
from timeit import default_timer as timer

# https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python#7370824


if __name__ == "__main__":
    start = timer()
    args = lib.get_args_parsed()
    lib.run(args)
    end = timer()
    duration = end - start
    # print(f"Time elapsed: {duration}s")
    print(f"Time elapsed: {duration * 1000}ms")
