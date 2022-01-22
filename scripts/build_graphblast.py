import subprocess
import shared
import argparse

GRAPHBLAST_PATH = shared.DEPS / "graphblast"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--j", default=8, help="Number of threads used to build")
    args = parser.parse_args()

    try:
        print(f"Build graphblast inside {GRAPHBLAST_PATH} directory")
        subprocess.check_call(["make", "-B", f"--directory={GRAPHBLAST_PATH}", f"-j{args.j}"])
    except subprocess.CalledProcessError as error:
        print("Failed to build graphblas. Error:", error)
        return 1

    print("Done!")
    return 0


if __name__ == '__main__':
    exit(main())
