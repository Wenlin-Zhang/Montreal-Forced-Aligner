import sys
import shutil, os
import argparse
import subprocess
import re

if sys.platform == 'win32':
    exe_ext = '.exe'
    lib_ext = '.dll'
elif sys.platform == 'darwin':
    exe_ext = ''
    lib_ext = ['.dylib']
else:
    exe_ext = ''
    lib_ext = ['.so', '.so.1']

ignored_filenames = ['.DS_Store', 'configure' , 'Doxyfile' ,
                'INSTALL', 'NOTES','TODO','Makefile','AUTHORS',
                'COPYING', 'NEWS', 'README', 'CHANGELOG', 'DISCLAIMER',
                'log', 'makefile', 'packImageTarFile']

included_filenames = ['compute-mfcc-feats', 'copy-feats', 'gmm-acc-stats-ali',
                'compile-train-graphs','align-equal-compiled', 'gmm-acc-stats-ali',
                'gmm-align-compiled', 'gmm-boost-silence', 'linear-to-nbest',
                'lattice-align-words', 'nbest-to-ctm','lattice-to-phone-lattice',
                'acc-tree-stats', 'sum-tree-stats', 'convert-ali','ali-to-post',
                'weight-silence-post', 'gmm-est-fmllr', 'compose-transforms',
                'transform-feats', 'gmm-est', 'gmm-sum-accs', 'gmm-init-mono',
                'cluster-phones', 'compile-questions', 'build-tree','gmm-init-model',
                'gmm-mixup', 'gmm-info', 'fstcompile', 'fstarcsort', 'compute-cmvn-stats',
                'apply-cmvn', 'add-deltas', 'feat-to-dim', 'subset-feats',
                'extract-segments', 'openblas', 'openfst64']

dylib_pattern = re.compile(r'\s*(.*)\s+\(')

def CollectBinaries(directory):
    outdirectory = os.path.dirname(os.path.realpath(__file__))
    bin_out = os.path.join(outdirectory, 'bin')
    os.makedirs(bin_out, exist_ok = True)
    tools_dir = os.path.join(directory, 'tools')
    for root, dirs, files in os.walk(tools_dir):
        for name in files:
            ext = os.path.splitext(name)
            (key, value) = ext
            if value == exe_ext and key in included_filenames:
                bin_name = os.path.join(bin_out, name)
                if not os.path.exists(bin_name):
                    shutil.copy(os.path.join(root, name), bin_out)
                    if sys.platform == 'darwin':
                        p = subprocess.Popen(['otool', '-L', bin_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, err = p.communicate()
                        rc = p.returncode
                        output = output.decode()
                        libs = dylib_pattern.findall(output)
                        for l in libs:
                            if l.startswith('/usr'):
                                continue
                            lib = os.path.basename(l)
                            subprocess.call(['install_name_tool','-change',l, '@loader_path/'+lib, bin_name])
            elif sys.platform == 'win32' and name in ['openfst64.dll','libopenblas.dll']:
                shutil.copy(os.path.join(root, name), bin_out)
            elif sys.platform != 'win32':
                c = False
                for le in lib_ext:
                    if name.endswith(le):
                        c = True
                if c:
                    shutil.copy(os.path.join(root, name), bin_out)

    if sys.platform == 'win32':
        src_dir = directory
    else:
        src_dir = os.path.join(directory, 'src')
    for root, dirs, files in os.walk(src_dir, followlinks = True):
        cur_dir = os.path.basename(root)
        for name in files:
            ext = os.path.splitext(name)
            (key, value) = ext
            bin_name = os.path.join(bin_out, name)
            if not os.path.exists(bin_name):
                if value == exe_ext:
                    if key not in included_filenames:
                        continue
                    shutil.copy(os.path.join(root, name), bin_out)
                elif value == lib_ext:
                    shutil.copy(os.path.join(root, name), bin_out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    args = parser.parse_args()
    directory = os.path.expanduser(args.dir)
    CollectBinaries(directory)
