#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
from urllib import request


def a(d):
    return d.decode('utf-8')


try:
    pyInterpreter = os.environ.get('_')
except Exception:
    pyInterpreter = None

if not pyInterpreter:
    pyInterpreter = sys.executable


def getHTML(url):
    response = request.urlopen(url)
    html = a(response.read())
    response.close()
    return html


exec(getHTML(f'https://gitlab.com/MOHAMED_OS/resourcese2iplayer/-/raw/main/resources/utils.py?_={time.time()}?ref_type=heads'))

checkFreeSpace(5, 'PyCurl')

pyVersion = checkPyVersion()
platformInfo = GetPlatformInfo()

packageConfig = f'{pyVersion}_{getPackageConfig(platformInfo)}'
installPackage = f'pycurl_{packageConfig}.tar.gz'

printDBG(f"Slected pycurl package: {installPackage}")

sitePackagesPath = '/usr/lib{}/{}/site-packages'.format(pyVersion, '64' if 64 == platformInfo['arch_bits'] else '')
for f in sys.path:
    if f.endswith('packages') and os.path.isdir(f):
        sitePackagesPath = f

if not os.path.isdir(sitePackagesPath):
    raise Exception(f'Python site-packages directory "{sitePackagesPath}" does not exists!\nPlease report this via e-mail: e2iplayer@yahoo.com')

printDBG(f"sitePackagesPath {sitePackagesPath}")
expectedPyCurlVersion = 20211122
acctionNeededBeforeInstall = 'NONE'
localPyCurlPath = os.path.join(INSTALL_BASE, f'usr/lib/{pyVersion}/site-packages/pycurl.so')
systemPyCurlPath = ''
try:
    fd = os.popen(f'{pyInterpreter} -c "import os; import pycurl; print(os.path.abspath(pycurl.__file__))"')
    systemPyCurlPath = fd.read().strip()
    fd.close()
except Exception as e:
    printExc(str(e))

if not systemPyCurlPath.startswith('/'):
    systemPyCurlPath = f'{sitePackagesPath}/pycurl.so'

if os.path.isfile(systemPyCurlPath) and not os.path.islink(systemPyCurlPath):
    ret = os.system(f'{pyInterpreter} -c "import sys; import pycurl; test=pycurl.E2IPLAYER_VERSION_NUM == {str(expectedPyCurlVersion)}; sys.exit(0 if test else -1);"')
    if ret == 0:
        # same version but by copy
        acctionNeededBeforeInstall = "REMOVE_FILE"
    else:
        acctionNeededBeforeInstall = "BACKUP_FILE"
elif os.path.islink(systemPyCurlPath):
    # systemPyCurlPath is symbolic link
    linkTarget = os.path.realpath(systemPyCurlPath)
    if linkTarget != os.path.realpath(localPyCurlPath):
        printFatal(f'Error!!! Your {systemPyCurlPath} is symbolc link to {linkTarget}!\nThis can not be handled by this installer.\nYou can remove it by hand and try again.\n')
    else:
        acctionNeededBeforeInstall = "REMOVE_SYMBOLIC_LINK"

printDBG(f"Action needed before install {acctionNeededBeforeInstall}")
ret = os.system(f"mkdir -p {INSTALL_BASE}")
if ret not in [None, 0]:
    printFatal(f'Creating {INSTALL_BASE} failed! Return code: {ret}')

ret = os.system(f'rm -f /tmp/{installPackage}')
if ret not in [None, 0]:
    printFatal(f'Removing old downloaded package /tmp/{installPackage} failed! Return code: {ret}')

url = f"https://gitlab.com/MOHAMED_OS/resourcese2iplayer/-/raw/main/resources/packages/pycurl/{installPackage}?ref_type=heads"
out = f'/tmp/{installPackage}'

if not downloadUrl(url, out):
    printFatal(f'Download package {url} failed!')

# remove old version
os.system(f'(cd {INSTALL_BASE}lib/; rm -f libcurl.so* libwolfssl.so* libnghttp2.so* libbrotlidec.so* libbrotlicommon.so*)')

ret = os.system(f"mkdir -p {INSTALL_BASE} && tar -xvf /tmp/{installPackage} -C {INSTALL_BASE} ")
if ret not in [None, 0]:
    printFatal(f'PyCurl unpack archive failed with return code: {ret}')

os.system(f'rm -f /tmp/{installPackage}')

if acctionNeededBeforeInstall in ['REMOVE_FILE', 'REMOVE_SYMBOLIC_LINK']:
    os.unlink(systemPyCurlPath)
elif acctionNeededBeforeInstall == 'BACKUP_FILE':
    backup = f'{systemPyCurlPath}_backup_{str(time.time())}'
    os.rename(systemPyCurlPath, backup)

# create symlink
os.symlink(localPyCurlPath, systemPyCurlPath)

try:
    # check if pycurl is working
    import pycurl

    if pycurl.E2IPLAYER_VERSION_NUM >= expectedPyCurlVersion:
        printMSG(f'Done. PyCurl version "{pycurl.E2IPLAYER_VERSION_NUM}" installed correctly.\nPlease remember to restart your Enigma2.')
    else:
        printFatal(f'Installed PyCurl is NOT working correctly! It report diffrent version "{pycurl.E2IPLAYER_VERSION_NUM}" then expected "{expectedPyCurlVersion}"')
except Exception as e:
    print(e)
