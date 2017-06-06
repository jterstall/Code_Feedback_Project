import ICP
import argparse
import ConceptualCoupling

def init_arg_parser():
    parser = argparse.ArgumentParser(
        description="Feedback program based on coupling metrics")
    parser.add_argument("dimension", nargs='?', help="Dimension to reduce lsi vectors to, default=100", default=100, type=int)
    parser.add_argument(
        "path", help="Directory where student assignment is stored (absolute path)", type=str)
    parser.add_argument(
        "main_file", help="Main file of student assignment used to run the program", type=str)
    parser.add_argument(
        "--suppress", help="Suppresses student assignment output", action='store_true')
    parser.add_argument("optional_args", nargs="*",
                        help="Any arguments necessary for passing on to student program in command line")
    # Retrieve user input
    args, unknown = parser.parse_known_args()
    args.optional_args.extend(unknown)
    return args


def main():
    args = init_arg_parser()
    ConceptualCoupling.run_conceptual_coupling(args.path, args.dimension)
    ICP.run_ICP(args.main_file, args.path, args.optional_args)


if __name__ == '__main__':
    main()
