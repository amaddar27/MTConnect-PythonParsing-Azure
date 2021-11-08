import sys
import traceback
from simulations import run_simulation_execution, run_simulation_all

if __name__ == '__main__':

    try:
        nextSequence, bufferSize, programs = run_simulation_execution(initial=True, nextSequence='', bufferSize='',
                                                                      programs={})
        while True:
            nextSequence, bufferSize, programs = run_simulation_execution(initial=False, nextSequence=nextSequence,
                                                                          bufferSize=bufferSize, programs=programs)

    except KeyboardInterrupt:  # stops when ctrl+c is pressed (or stop button on pycharm)
        print("Program stopped")
        sys.exit(0)

    except Exception as e:  # stops at any exception
        print("Unexpected error")
        print(traceback.format_exc())
        raise SystemExit(e)