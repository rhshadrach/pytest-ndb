#!/usr/bin/env python3
"""
Python script for building documentation.

To build the docs you must have all optional dependencies for pandas
installed. See the installation instructions for a list of these.

Usage
-----
    $ python make.py clean
    $ python make.py html
    $ python make.py latex
"""
import argparse
import importlib
import os
import shutil
import subprocess
import sys
import webbrowser

DOC_PATH = os.path.dirname(os.path.abspath(__file__))
SOURCE_PATH = os.path.join(DOC_PATH, "source")
BUILD_PATH = os.path.join(DOC_PATH, "build")


class DocBuilder:
    """
    Class to wrap the different commands of this script.

    All public methods of this class can be called as parameters of the
    script.
    """

    def __init__(
        self,
        num_jobs="auto",
        verbosity=0,
        warnings_are_errors=False,
    ) -> None:
        self.num_jobs = num_jobs
        self.verbosity = verbosity
        self.warnings_are_errors = warnings_are_errors

    def _process_single_doc(self, single_doc):
        """
        Make sure the provided value for --single is a path to an existing
        .rst/.ipynb file, or a pandas object that can be imported.

        For example, categorial.rst or pandas.DataFrame.head. For the latter,
        return the corresponding file path
        (e.g. reference/api/pandas.DataFrame.head.rst).
        """
        base_name, extension = os.path.splitext(single_doc)
        if extension in (".rst", ".ipynb"):
            if os.path.exists(os.path.join(SOURCE_PATH, single_doc)):
                return single_doc
            else:
                raise FileNotFoundError(f"File {single_doc} not found")

        elif single_doc.startswith("pandas."):
            try:
                obj = pandas  # noqa: F821
                for name in single_doc.split("."):
                    obj = getattr(obj, name)
            except AttributeError as err:
                raise ImportError(f"Could not import {single_doc}") from err
            else:
                return single_doc[len("pandas.") :]
        else:
            raise ValueError(
                f"--single={single_doc} not understood. "
                "Value should be a valid path to a .rst or .ipynb file, "
                "or a valid pandas object "
                "(e.g. categorical.rst or pandas.DataFrame.head)"
            )

    @staticmethod
    def _run_os(*args):
        """
        Execute a command as a OS terminal.

        Parameters
        ----------
        *args : list of str
            Command and parameters to be executed

        Examples
        --------
        >>> DocBuilder()._run_os('python', '--version')
        """
        subprocess.check_call(args, stdout=sys.stdout, stderr=sys.stderr)

    def _sphinx_build(self, kind: str):
        """
        Call sphinx to build documentation.

        Attribute `num_jobs` from the class is used.

        Parameters
        ----------
        kind : {'html', 'latex'}

        Examples
        --------
        >>> DocBuilder(num_jobs=4)._sphinx_build('html')
        """
        if kind not in ("html", "latex"):
            raise ValueError(f"kind must be html or latex, not {kind}")

        cmd = ["sphinx-build", "-b", kind]
        if self.num_jobs:
            cmd += ["-j", self.num_jobs]
        if self.warnings_are_errors:
            cmd += ["-W", "--keep-going"]
        if self.verbosity:
            cmd.append(f"-{'v' * self.verbosity}")
        cmd += [
            "-d",
            os.path.join(BUILD_PATH, "doctrees"),
            SOURCE_PATH,
            os.path.join(BUILD_PATH, kind),
        ]
        return subprocess.call(cmd)

    def _open_browser(self, single_doc_html):
        """
        Open a browser tab showing single
        """
        url = os.path.join("file://", DOC_PATH, "build", "html", single_doc_html)
        webbrowser.open(url, new=2)

    def html(self):
        """
        Build HTML documentation.
        """
        ret_code = self._sphinx_build("html")
        zip_fname = os.path.join(BUILD_PATH, "html", "pandas.zip")
        if os.path.exists(zip_fname):
            os.remove(zip_fname)

        return ret_code

    @staticmethod
    def clean():
        """
        Clean documentation generated files.
        """
        shutil.rmtree(BUILD_PATH, ignore_errors=True)
        shutil.rmtree(os.path.join(SOURCE_PATH, "reference", "api"), ignore_errors=True)

    def zip_html(self):
        """
        Compress HTML documentation into a zip file.
        """
        zip_fname = os.path.join(BUILD_PATH, "html", "pandas.zip")
        if os.path.exists(zip_fname):
            os.remove(zip_fname)
        dirname = os.path.join(BUILD_PATH, "html")
        fnames = os.listdir(dirname)
        os.chdir(dirname)
        self._run_os("zip", zip_fname, "-r", "-q", *fnames)


def main():
    cmds = [method for method in dir(DocBuilder) if not method.startswith("_")]

    joined = ",".join(cmds)
    argparser = argparse.ArgumentParser(
        description="oss_health documentation builder", epilog=f"Commands: {joined}"
    )

    joined = ", ".join(cmds)
    argparser.add_argument(
        "command", nargs="?", default="html", help=f"command to run: {joined}"
    )
    argparser.add_argument(
        "--num-jobs", default="auto", help="number of jobs used by sphinx-build"
    )
    argparser.add_argument(
        "--python-path", type=str, default=os.path.dirname(DOC_PATH), help="path"
    )
    argparser.add_argument("--github-pat", type=str, default="", help="path")
    argparser.add_argument(
        "-v",
        action="count",
        dest="verbosity",
        default=0,
        help=(
            "increase verbosity (can be repeated), "
            "passed to the sphinx build command"
        ),
    )
    argparser.add_argument(
        "--warnings-are-errors",
        "-W",
        action="store_true",
        help="fail if warnings are raised",
    )
    args = argparser.parse_args()

    if args.command not in cmds:
        joined = ", ".join(cmds)
        raise ValueError(f"Unknown command {args.command}. Available options: {joined}")

    # Below we update both os.environ and sys.path. The former is used by
    # external libraries (namely Sphinx) to compile this module and resolve
    # the import of `python_path` correctly. The latter is used to resolve
    # the import within the module, injecting it into the global namespace
    os.environ["PYTHONPATH"] = args.python_path
    sys.path.insert(0, args.python_path)
    globals()["oss_health"] = importlib.import_module("oss_health")

    if args.command == "html":
        import oss_health

        oss_health.make_pypi_to_github_mapping(1)
        oss_health.run(args.github_pat)

    builder = DocBuilder(
        args.num_jobs,
        args.verbosity,
        args.warnings_are_errors,
    )
    return getattr(builder, args.command)()


if __name__ == "__main__":
    sys.exit(main())
