import itertools
import os
import subprocess
import shared
import argparse

GUNROCK_PATH = shared.DEPS / "gunrock"
GUNROCK_BUILD = GUNROCK_PATH / "build"
GUNROCK_TARGETS = ["bfs", "sssp", "tc"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--j", default=8, help="Number of threads used to build")
    parser.add_argument("--cc", default="/usr/bin/gcc-8", help="Path to CC compiler")
    parser.add_argument("--cxx", default="/usr/bin/g++-8", help="Path to CXX compiler")
    parser.add_argument("--cudacxx", default="/usr/bin/g++-8", help="Path to CUDAHOSTCXX compiler")
    parser.add_argument("--autodetect", default=True, help="Autodetect target architecture")
    parser.add_argument("--gencode", default="SM61", help="Target sm and compute architecture. Available: "
                                                          "SM10, SM13, SM20, SM30, SM35, SM37, SM50, "
                                                          "SM52, SM60, SM61, SM70, SM72, SM75, SM80")

    args = parser.parse_args()

    # For ref on gencode https://stackoverflow.com/questions/17599189/what-is-the-purpose-of-using-multiple-arch-flags-in-nvidias-nvcc-compiler/17599585#17599585

    try:
        env = os.environ.copy()
        env["CC"] = args.cc
        env["CXX"] = args.cxx
        env["CUDAHOSTCXX"] = args.cudacxx
        print(f"Build gunrock inside {GUNROCK_PATH} directory")
        print(f"Using env: CC={args.cc} CXX={args.cxx} CUDAHOSTCXX={args.cudacxx}")
        subprocess.check_call(["cmake", str(GUNROCK_PATH), "-B", str(GUNROCK_BUILD),
                               "-DCUDA_AUTODETECT_GENCODE=ON" if args.autodetect
                               else f"-DGUNROCK_GENCODE_{args.gencode}=ON"],
                              env=env)
        subprocess.check_call(["cmake", "--build", str(GUNROCK_BUILD)] +
                              list(itertools.chain(*[["-t", t] for t in GUNROCK_TARGETS])) +
                              ["-j", str(args.j)])
    except subprocess.CalledProcessError as error:
        print("Failed to build gunrock. Error:", error)
        return 1

    print("Done!")
    return 0


if __name__ == '__main__':
    exit(main())
