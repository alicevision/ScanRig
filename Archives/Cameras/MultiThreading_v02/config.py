import logging, argparse, os

ARGS = None

#------------------------- LOGGING
log_levels = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}

#------------------------- CONFIG FUNCTION
def config():
    parser = argparse.ArgumentParser(description='Display video stream')
    parser.add_argument('-o', '--output', metavar='Output folder', type=str,
                        default='',
                        help='')
    parser.add_argument('-e', '--extension', metavar='Output file format/extention', type=str,
                        default='png',
                        help='')
    parser.add_argument('-c', '--cameras', metavar='Cameras Indexes', type=int, nargs='+',
                        default=[0],
                        help='')
    parser.add_argument('-d', '--display', metavar='Display window', type=bool,
                        default=True,
                        help='')
    parser.add_argument('-s', '--sleep', metavar='Display sleep time (ms)', type=int,
                        default=1,
                        help='')
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=3,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                            "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                            "DEBUG=4")

    args = parser.parse_args()
    logging.basicConfig(level=log_levels[args.verbosity])

    if args.output and not os.path.exists(args.output):
        os.mkdir(args.output)

    logging.info("Args: " + str(args))
    logging.info("Press 'esc' to exit.")

    return args