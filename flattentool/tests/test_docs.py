import os
import shlex
import subprocess
import sys

from os.path import join, getsize
from six import text_type


def test_cafe_examples_in_docs():
    tests_passed = 0
    for root, dirs, files in os.walk('examples/cafe'):
        for filename in files:
            if 'xlsx' in root and sys.version_info[:2] < (3,4):
                continue
            if 'cmd.txt' in filename:
                with open(join(root, filename), 'rb') as fp:
                    cmds = text_type(fp.read(), 'utf8').strip().split('\n')
                    actual_stdout = b''
                    actual_stderr = b''
                    for cmd in cmds:
                        assert (
                            cmd.startswith('$ flatten-tool ') or cmd.startswith('$ cat ')
                        ), "Expected commands to start with '$ flatten-tool'"
                        # Since we are defining all the commands ourselves, this is reasonably safe
                        cmd_parts = shlex.split(cmd[len('$ '):])
                        # Include coverage output in the results
                        if cmd_parts[0] == 'flatten-tool':
                            cmd_parts = [
                                'coverage',
                                'run',
                                '--source', 'flattentool',
                                '--parallel-mode',
                            ] + cmd_parts
                        process = subprocess.Popen(cmd_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        (cmd_actual_stdout, cmd_actual_stderr) = process.communicate()
                        process.wait()
                        assert process.returncode == 0, cmd
                        actual_stdout += (cmd_actual_stdout or b'')
                        actual_stderr += (cmd_actual_stderr or b'')
                    with open(join(root, 'expected.json'), 'rb') as fstdout:
                        expected_stdout = fstdout.read()
                    expected_stderr = b''
                    if os.path.exists(join(root, 'expected_stderr.json')):
                        with open(join(root, 'expected_stderr.json'), 'rb') as fstderr:
                            data = fstderr.read()
                            expected_stderr_lines = text_type(data, 'utf8').split('\n')
                            for line in expected_stderr_lines:
                                if line:
                                    if line.startswith('.../'):
                                        line = text_type(os.getcwd()) + line[3:]
                                    expected_stderr += (line + '\n').encode('utf8')
                                else:
                                     expected_stderr += b'\n'
                    assert _strip(actual_stdout) == _strip(expected_stdout), cmds
                    assert _strip(actual_stderr) == _strip(expected_stderr), cmds
                    tests_passed += 1
    # Check that the number of tests were run that we expected
    if sys.version_info[:2] < (3,4):
        assert tests_passed == 19
    else:
        assert tests_passed == 20


# Older versions of Python have an extra whitespace at the end compared to newer ones
# https://bugs.python.org/issue16333
def _strip(output):
    # Don't worry about any extra blank lines at the end either
    outstr = text_type(output, 'utf8').rstrip('\n')
    return '\n'.join(line.rstrip(' ') for line in outstr.split('\n'))


# Useful for a coverage check - see developer docs for how to run the check
if __name__ == '__main__':
    test_cafe_examples_in_docs()
