import time
import asyncio
from concurrent.futures import ProcessPoolExecutor

def blocking_func(x):
   time.sleep(x) # Pretend this is expensive calculations
   return x * 5

@asyncio.coroutine
def main():
    #pool = multiprocessing.Pool()
    #out = pool.apply(blocking_func, args=(10,)) # This blocks the event loop.
    executor = ProcessPoolExecutor()
    out = yield from loop.run_in_executor(executor, blocking_func, 10)  # This does not
    print(out)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
