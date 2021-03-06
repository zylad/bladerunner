#!/usr/bin/env python
#coding: utf-8

"""Progress bar and terminal width functions for Bladerunner.

This file is part of Bladerunner.

Copyright (c) 2013, Activision Publishing, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of Activision Publishing, Inc. nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from __future__ import division
from __future__ import unicode_literals
import os
import sys


class ProgressBar(object):
    """A simple textual progress bar."""

    def __init__(self, total_updates, options=None):
        """Initializes the object.

        Args:
            total_updates: an integer of how many times update() will be called
            options: a dictionary of additional options. schema:
                width: an integer for fixed terminal width printing
                style: an integer style, between 0-2
                show_counters: a boolean to declare showing the counters or not
        """

        self.total = total_updates
        try:
            self.total_width = options['width'] or get_term_width()
        except (KeyError, TypeError):
            self.total_width = get_term_width()

        self.counter = 0  # update counter
        self.chars = {
            "left": ["[", "{", ""],
            "right": ["]", "}", ""],
            "space": [" ", " ", "░"],
            25: ["/", ".", "▒"],
            50: ["-", "-", "▓"],
            75: ["\\", "+", "▊"],
            100: ["=", "*", "█"],
        }

        try:
            if options["style"] < 0 or \
               options["style"] >= len(self.chars["left"]):
                self.style = 0
            else:
                self.style = options["style"]
        except (KeyError, TypeError):
            self.style = 0

        try:
            self.show_counters = options["show_counters"]
        except (KeyError, TypeError):
            self.show_counters = True

        if self.show_counters:
            self.width = self.total_width - (
                (len(str(self.total)) * 2)
                + len(self.chars["left"][self.style])
                + len(self.chars["right"][self.style])
                + 2  # the space and the slash
            )
        else:
            self.width = self.total_width - (
                len(self.chars["left"][self.style])
                + len(self.chars["right"][self.style])
            )

        super(ProgressBar, self).__init__()

    def setup(self):
        """Prints an empty progress bar to the screen."""

        if self.show_counters:
            counter_diff = len(str(self.total)) - len(str(self.counter))
            spaces = self.width + counter_diff
            sys.stdout.write("{left}{space}{right} {count}/{total}".format(
                left=self.chars["left"][self.style],
                space=self.chars["space"][self.style] * spaces,
                right=self.chars["right"][self.style],
                count=self.counter,
                total=self.total,
            ))
        else:
            sys.stdout.write("{left}{space}{right}".format(
                left=self.chars["left"][self.style],
                space=self.chars["space"][self.style] * self.width,
                right=self.chars["right"][self.style],
            ))
        sys.stdout.flush()

    def update(self):
        """Updates self.counter by 1 and prints the new progress bar."""

        self.counter += 1
        counter_diff = len(str(self.total)) - len(str(self.counter))
        percent = (self.counter / self.total) * (self.width + counter_diff)

        sys.stdout.write("\r{left}{spaces}".format(
            left=self.chars["left"][self.style],
            spaces=self.chars[100][self.style] * int(percent),
        ))

        try:
            if not self.total > self.width * 4:
                halfchar = self.chars[rounded(percent, 50)][self.style]
            else:
                halfchar = self.chars[rounded(percent, 25)][self.style]
        except KeyError:
            halfchar = ""

        if self.show_counters:
            sys.stdout.write("{left}{space}{right} {count}/{total}".format(
                left=halfchar,
                space=self.chars["space"][self.style] * (
                    self.width
                    + counter_diff
                    - int(percent)
                    - len(halfchar)
                ),
                right=self.chars["right"][self.style],
                count=self.counter,
                total=self.total
            ))
        else:
            sys.stdout.write("{left}{space}{right}".format(
                left=halfchar,
                space=self.chars["space"][self.style] * (
                    self.width
                    - int(percent)
                    - len(halfchar)
                ),
                right=self.chars["right"][self.style],
            ))
        sys.stdout.flush()

    def clear(self):
        """Clears the progress bar from the screen and resets the cursor."""

        sys.stdout.write("\r{spaces}".format(spaces=" " * self.total_width))
        sys.stdout.flush()
        sys.stdout.write("\r")
        sys.stdout.flush()


def rounded(number, round_to):
    """Internal function for rounding numbers.

    Args:
        number: an integer
        round_to: an integer want the number to be rounded towards

    Returns:
        number, rounded to the nearest round_to
    """

    return int(round(((number - int(number)) * 100) / round_to) * round_to)


def get_term_width():
    """Tries to get the current terminal width, returns 80 if it cannot.

    credit for this function: http://stackoverflow.com/a/566752
    """

    env = os.environ

    def ioctl_try(os_fd):
        """Internal method to ask the fcntl module for the window size."""

        try:
            import fcntl
            import termios
            import struct
        except ImportError:
            return None

        try:
            termsize = struct.unpack(
                "hh",
                fcntl.ioctl(
                    os_fd,
                    termios.TIOCGWINSZ,
                    "1234",
                )
            )
            return termsize
        except Exception:
            return None

    termsize = ioctl_try(0) or ioctl_try(1) or ioctl_try(2)
    if not termsize:
        try:
            os_fd = os.open(os.ctermid(), os.O_RDONLY)
            termsize = ioctl_try(os_fd)
            os.close(os_fd)
        except Exception:
            pass
    if not termsize:
        try:
            termsize = (env["LINES"], env["COLUMNS"])
        except (IndexError, KeyError):
            termsize = (25, 80)
    return int(termsize[1])


def cmd_line_help(name):
    """Overrides argparse's help."""

    sys.exit(
        "{name} -- the simple python progress bar used in Bladerunner.\n"
        "Options:\n"
        "\t-c --count=<int>\tThe number of updates (default: 10)\n"
        "\t-d --delay=<seconds>\tThe seconds between updates (default: 1)\n"
        "\t-h --help\t\tDisplay this help message and quit\n"
        "\t--hide-counters\t\tDo not show the counters with the progress bar\n"
        "\t-s --style=<int>\tUse an alternate style (default: 0)\n"
        "\t-w --width=<int>\tThe total width (default: 80)\n".format(
            name=name,
        )
    )


def cmd_line_arguments(args):
    """Sets up argparse for the command line demo."""

    parser = argparse.ArgumentParser(
        prog="progressbar",
        description="progressbar -- a simple python progress bar",
        add_help=False,
    )

    parser.add_argument(
        "--count",
        "-c",
        dest="count",
        metavar="INT",
        type=int,
        nargs=1,
        default=10,
    )

    parser.add_argument(
        "--delay",
        "-d",
        dest="delay",
        metavar="SECONDS",
        type=float,
        nargs=1,
        default=1,
    )

    parser.add_argument(
        "--style",
        "-s",
        dest="style",
        metavar="INT",
        type=int,
        nargs=1,
        default=0,
    )

    parser.add_argument(
        "--width",
        "-w",
        dest="width",
        metavar="INT",
        type=int,
        nargs=1,
        default=80,
    )

    parser.add_argument(
        "--hide-counters",
        dest="show_counters",
        action="store_false",
        default=True,
    )

    parser.add_argument(
        "--help",
        "-h",
        dest="helper",
        action="store_true",
        default=False,
    )

    options = parser.parse_args(args)

    if options.helper:
        cmd_line_help(sys.argv[0].split("/")[-1])

    if options.count != 10:
        options.count = options.count[0]

    if options.delay != 1:
        options.delay = options.delay[0]

    if options.style != 0:
        options.style = options.style[0]

    if options.width != 80:
        options.width = options.width[0]

    return options


if __name__ == "__main__":

    import time
    import argparse

    OPTIONS = cmd_line_arguments(sys.argv[1:])

    PROGRESSBAR = ProgressBar(
        OPTIONS.count,
        {
            "style": OPTIONS.style,
            "width": OPTIONS.width,
            "show_counters": OPTIONS.show_counters,
        },
    )
    try:
        for i in range(OPTIONS.count):
            time.sleep(OPTIONS.delay)
            PROGRESSBAR.update()
    except KeyboardInterrupt:
        pass
    raise SystemExit("\n")
