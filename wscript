# Build instructions
# ------------------
#
# Standard build and install command:
#
#   $ python waf.py --prefix=/desired/path configure build install
#
# To use clang instead of the automatically detected installed
# compiler:
#
#   $ CXX=clang++ CC=clang python waf.py configure ...
#
# To cross-compile a 32bit binary on a 64bit system on unixes:
#
#   $ python waf.py --dest-cpu=i386 configure ...
#
# On Windows:
#
#   $ python .\waf.py --msvc_targets=x86 configure
#
from checksums import dlls
from hashlib import md5
from os import path
from urllib import urlopen
from waflib import Errors, Task

cpu_to_bits = {'amd64' : 64, 'i386' : 32, 'x86' : 32, 'x86_64' : 64}

guids = {
    32 : 'a19134b3-f679-4901-bd35-04d6e9d0cee0',
    64 : '98a680c5-da23-42fe-b953-c33616a6b3c3'
}

APPNAME = 'factor-lang'
VERSION = '0.98'

# List source files
common_source = [
    'aging_collector.cpp',
    'alien.cpp',
    'arrays.cpp',
    'bignum.cpp',
    'byte_arrays.cpp',
    'callbacks.cpp',
    'callstack.cpp',
    'code_blocks.cpp',
    'code_heap.cpp',
    'compaction.cpp',
    'contexts.cpp',
    'data_heap.cpp',
    'data_heap_checker.cpp',
    'debug.cpp',
    'dispatch.cpp',
    'entry_points.cpp',
    'errors.cpp',
    'factor.cpp',
    'free_list.cpp',
    'full_collector.cpp',
    'gc.cpp',
    'gc_info.cpp',
    'image.cpp',
    'inline_cache.cpp',
    'instruction_operands.cpp',
    'io.cpp',
    'jit.cpp',
    'math.cpp',
    'mvm.cpp',
    'nursery_collector.cpp',
    'object_start_map.cpp',
    'objects.cpp',
    'primitives.cpp',
    'quotations.cpp',
    'run.cpp',
    'safepoints.cpp',
    'sampling_profiler.cpp',
    'strings.cpp',
    'to_tenured_collector.cpp',
    'tuples.cpp',
    'utilities.cpp',
    'vm.cpp',
    'words.cpp'
    ]

def wix_light(ctx, source, target, extra_files):
    wixobjs = ' '.join(source)
    return ctx(
        rule = 'light -ext WixUIExtension -nologo -out ${TGT} %s' % wixobjs,
        source = source + extra_files,
        target = target
        )

def wix_heat_dir(ctx, group, dirpath, source = None):
    if source is None:
        source = []
    # -sw 5150 suppresses warning about self-registering dlls.
    rule_fmt = ('heat dir %s -sw 5150 -nologo -var var.MySource '
                '-cg %sgroup -gg -dr INSTALLDIR -out ${TGT}')
    return ctx(
        rule = rule_fmt % (dirpath, group),
        source = source,
        target = '%s.wxs' % group
        )

def wix_candle(ctx, group, dirpath):
    return ctx(
        rule = 'candle -nologo -out ${TGT} ${SRC} -dMySource="%s"' % dirpath,
        source = ['%s.wxs' % group],
        target = ['%s.wxsobj' % group]
        )

# This monkey patching enables syncronous output from rule tasks.
# https://groups.google.com/d/msg/waf-users/2uA3DEltTKg/8T4X9I4OeeQJ
def my_exec_command(self, cmd, **kw):
    bld = self.generator.bld
    if not kw.get('cwd'):
        cwd = getattr(bld, 'cwd', bld.variant_dir)
        bld.cwd = kw['cwd'] = cwd

    kw["stdout"] = kw["stderr"] = None
    return bld.exec_command(cmd, **kw)
Task.TaskBase.exec_command = my_exec_command

def options(ctx):
    ctx.load('compiler_c compiler_cxx')
    ctx.add_option(
        '--make-bootstrap-image',
        action = 'store_true',
        default = False,
        help = 'generate new boot images (requires Factor to be installed)'
    )
    ctx.add_option(
        '--debug',
        action = 'store_true',
        default = False,
        help = 'build with debugging settings'
    )
    ctx.add_option(
        '--debug-gc-maps',
        action = 'store_true',
        default = False,
        help = 'build with gc map debugging'
    )
    dest_cpus = cpu_to_bits.keys()
    text = ', '.join(dest_cpus[:-1]) + ' or ' + dest_cpus[-1]
    ctx.add_option(
        '--dest-cpu',
        type = 'string',
        default = '',
        help = 'cpu target (gcc & clang only), one of: %s' % text
    )

def configure(ctx):
    ctx.load('compiler_c compiler_cxx')

    env = ctx.env
    dest_os = env.DEST_OS

    # Handle all options first
    opts = ctx.options
    if opts.dest_cpu:
        env.DEST_CPU = opts.dest_cpu
    if opts.make_bootstrap_image:
        ctx.find_program(APPNAME)
    ctx.env.MAKE_BOOTSTRAP_IMAGE = opts.make_bootstrap_image

    cxx = ctx.env.COMPILER_CXX
    pf = '.' if dest_os == 'win32' else opts.prefix

    # Values to be inked into the binary.
    ctx.define('FACTOR_VERSION', VERSION)
    try:
        git_label = ctx.cmd_and_log("git describe --all --long").strip()
    except Errors.WafError, e:
        git_label = 'tarball-build'
    ctx.define('FACTOR_GIT_LABEL', git_label)
    ctx.define('INSTALL_PREFIX', pf)

    if opts.debug:
        ctx.define('FACTOR_DEBUG', 1)
        if cxx == 'msvc':
            env.CXXFLAGS += ['/Zi', '/FS']
            env.LINKFLAGS += ['/DEBUG']
        elif cxx == 'g++':
            env.CXXFLAGS += ['-g']
    if opts.debug_gc_maps:
        ctx.define('DEBUG_GC_MAPS', 1)

    bits = get_bits(ctx)

    if dest_os == 'win32':
        ctx.check_lib_msvc('shell32')
        ctx.load('winres')
        if cxx == 'msvc':
            env.WINRCFLAGS += ['/nologo']
            env.CXXFLAGS += ['/EHsc', '/O2', '/WX', '/W3']
            if bits == 32:
                env.LINKFLAGS += ['/safeseh:no']
        elif cxx == 'g++':
            env.LINKFLAGS += ['-static-libgcc', '-static-libstdc++', '-s']
            env.CXXFLAGS += ['-O2', '-fomit-frame-pointer', '-std=c++11']
        ctx.define('_CRT_SECURE_NO_WARNINGS', None)
        # WIX checks
        ctx.find_program('candle')
        ctx.find_program('heat')
        ctx.find_program('light')
    elif dest_os == 'linux':
        # Lib checking
        ctx.check_cxx(lib = 'pthread', uselib_store = 'pthread')
        ctx.check_cxx(lib = 'dl', uselib_store = 'dl')
        ctx.check_cxx(
            function_name = 'clock_gettime',
            header_name = ['sys/time.h','time.h'],
            lib = 'rt', uselib_store = 'rt'
        )
        env.append_unique('CXXFLAGS', [
            '-O3', '-fomit-frame-pointer',
            '-Werror', '-Wall', '-std=c++11'
        ])
        for lst in ('CFLAGS', 'CXXFLAGS', 'LINKFLAGS'):
            env[lst] += ['-m%d' % bits]
        env.LINKFLAGS += ['-Wl,--no-as-needed', '-Wl,--export-dynamic']

def download_file(self):
    gen = self.generator
    url = gen.url
    expected_digest = gen.digest
    local_path = self.outputs[0].abspath()
    if path.exists(local_path):
        with open(local_path, 'rb') as f:
            digest = md5(f.read()).hexdigest()
            if digest == expected_digest:
                return
    data = urlopen(url).read()
    digest = md5(data).hexdigest()
    if digest != expected_digest:
        fmt = 'Digest mismatch: File %s has digest %s, expected %s.'
        raise Errors.WafError(fmt % (url, digest, expected_digest))
    with open(local_path, 'wb') as f:
        f.write(data)
    return

def get_bits(ctx):
    return cpu_to_bits[ctx.env.DEST_CPU]

def build_msi(ctx, bits, image_target):
    # Download all dlls needed for the build
    dll_targets = []
    url_fmt = 'http://downloads.factorcode.org/dlls/%s%s'
    for name, digest32, digest64 in dlls:
        digest = digest32 if bits == 32 else digest64
        if digest is None:
            continue
        url = url_fmt % ('' if bits == 32 else '64/', name)
        r = ctx(
            rule = download_file,
            url = url,
            digest = digest,
            target = 'dlls/%s' % name,
            always = True
            )
        dll_targets.append(r.target)

    # Generate wxs fragments of the Factor sources.
    frags = ['core', 'basis', 'extra', 'misc']
    fmt = 'heat dir ../%s -nologo -var var.MySource -cg %sgroup -gg -dr INSTALLDIR -out ${TGT}'
    for root in frags:
        wix_heat_dir(ctx, root, '../%s' % root)
        wix_candle(ctx, root, '../%s' % root)

    # Generate one wxs fragment for all bundled dlls.
    wix_heat_dir(ctx, 'dlls', 'dlls', source = dll_targets)
    wix_candle(ctx, 'dlls', 'dlls')

    # Wix wants the Product/@Version attribute to be all
    # numeric. So if you have a version like 0.97-git, you need to
    # strip out the -git part.
    product_version = VERSION.split('-')[0]
    bits_and_version = '%dbit %s' % (bits, VERSION)
    candle_rule = ' '.join([
        'candle',
        '-nologo',
        '-dProductVersion=%s' % product_version,
        '-dVersion="%s"' % bits_and_version,
        '-dBits=%s' % bits,
        '-dUpgradeCode=%s' % guids[bits],
        '-out ${TGT} ${SRC}'
    ])
    ctx(
        rule = candle_rule,
        source = ['factor.wxs'],
        target = ['factor.wxsobj']
        )
    wxsobjs = ['%s.wxsobj' % f for f in ['factor', 'dlls'] + frags]
    wix_light(
        ctx,
        wxsobjs,
        'factor.%dbit.%s.msi' % (bits, VERSION),
        [image_target, '%s.com' % APPNAME]
        )


def build(ctx):
    dest_os = ctx.env.DEST_OS
    image_target = '%s.image' % APPNAME

    bits = get_bits(ctx)
    os_sources = {
        'win32' : [
            'cpu-x86.cpp',
            'main-windows.cpp',
            'mvm-windows.cpp',
            'os-windows.cpp',
            'factor.rc',
            'os-windows-x86.%d.cpp' % bits
            ],
        'linux' : [
            'cpu-x86.cpp',
            'main-unix.cpp',
            'mvm-unix.cpp',
            'os-genunix.cpp',
            'os-linux.cpp',
            'os-unix.cpp'
            ]
        }
    os_uses = {
        'win32' : ['SHELL32'],
        'linux' : ['dl', 'gtk', 'gtkglext', 'pthread', 'rt']
        }
    vm_sources = [path.join('vm', s)
                  for s in common_source + os_sources[dest_os]]
    ctx.objects(includes = '.', source = vm_sources, target = 'OBJS')

    link_libs = os_uses[dest_os] + ['OBJS']
    features = 'cxx cxxprogram'

    if dest_os == 'win32':
        cxx = ctx.env.COMPILER_CXX
        subsys_fmt = '/SUBSYSTEM:%s' if cxx == 'msvc' else '-Wl,-subsystem,%s'
        tg1 = ctx.program(
            features = features,
            source = [],
            target = APPNAME,
            use = link_libs,
            linkflags = subsys_fmt % 'console',
            name = 'factor-com'
        )
        tg1.env.cxxprogram_PATTERN = '%s.com'
        ctx.add_group()
        ctx.program(
            features = features,
            source = [],
            target = APPNAME,
            use = link_libs,
            linkflags = subsys_fmt % 'windows',
            name = 'factor-exe'
            )
    elif dest_os == 'linux':
        ctx.program(
            features = features,
            source = [],
            target = APPNAME,
            use = link_libs
        )

    # Common paths
    libdir = '${PREFIX}/lib/factor'
    cwd = ctx.path

    # Build ffi test library. It is used by some unit tests.
    ctx.shlib(
        # Force lib prefix on windows too, it's nonidiomatic.
        target = '%sfactor-ffi-test' % ('lib' if dest_os == 'win32' else ''),
        source = ['vm/ffi_test.c'],
        install_path = libdir
        )

    # Build shared lib on Windows, static on Linux.  This is needed to
    # trick waf into always building the dll after the exe.
    ctx.add_group()
    if dest_os == 'win32':
        func = ctx.shlib
        features = 'cxx cxxshlib'
        linkflags = subsys_fmt % 'console'
    elif dest_os == 'linux':
        func = ctx.stlib
        features = 'cxx cxxstlib'
        linkflags = []
    func(
        features = features,
        target = APPNAME,
        source = [],
        install_path = libdir,
        use = link_libs,
        linkflags = linkflags
    )
    os_family = {'linux' : 'unix', 'win32' : 'windows'}[dest_os]
    boot_image_name = 'boot.%s-x86.%s.image' % (os_family, bits)

    # Since factor-lang needs to be run with the project root
    # directory as cwd, that is where the boot image needs to be
    # placed.
    boot_image_path = '../%s' % boot_image_name

    if ctx.env.MAKE_BOOTSTRAP_IMAGE:
        # Backslashes are misinterpreted by Factor on Windows
        resource_path = cwd.abspath().replace('\\', '/')
        params = [
            '-resource-path=%s' % resource_path,
            '-script',
            '-e="USING: system bootstrap.image vocabs.refresh ; '
            'refresh-all make-my-image"',
        ]
        ctx(
            rule = '"%s" %s' % (ctx.env['FACTOR-LANG'], ' '.join(params)),
            source = [],
            target = boot_image_path
        )
    else:
        source_image = 'boot-images/%s' % boot_image_name
        ctx(
            features = 'subst',
            source = source_image,
            target = boot_image_path,
            is_copy = True
        )

    # Build factor.image using the newly built executable.
    factor_exe = {'linux' : APPNAME, 'win32' : '%s.com' % APPNAME}[dest_os]

    # The first image we build doesn't contain local changes for some
    # reason. Not sure how resource-path works in combination with a
    # boot image on Windows. Seems like the resource-path switch
    # doesn't work in that case.
    old_image = '%s.incomplete.image' % APPNAME
    params = [
        '-i=${SRC[1].abspath()}',
        '-resource-path=%s' % cwd.abspath(),
        '-output-image=%s' % old_image
    ]
    ctx(
        rule = '${SRC[0].abspath()} ' + ' '.join(params),
        source = [factor_exe, boot_image_path],
        target = old_image
    )

    # Image built, but it needs to be updated too.
    params = [
        '-script',
        '-resource-path=..',
        '-i=%s' % old_image,
        '-e="USING: vocabs.loader vocabs.refresh system memory ; '
        'refresh-all \\"%s\\" save-image-and-exit"' % image_target
    ]
    ctx(
        rule = '${SRC[0].abspath()} ' + ' '.join(params),
        source = [factor_exe, old_image],
        target = image_target
    )

    # Installer and installation targets.
    if dest_os == 'win32':
        build_msi(ctx, bits, image_target)

    pat = '(basis|core|extra)/**/*'
    glob = cwd.ant_glob(pat)

    ctx.install_files(libdir, glob, cwd = cwd, relative_trick = True)
    ctx.install_files(libdir, 'license.txt', cwd = cwd)

    # Install stuff in misc
    sharedir = '${PREFIX}/share/factor'
    base = cwd.find_dir('misc')
    pat = '(fuel|icons|textadept|vim)/**/*.(el|lua|png|vim)'
    glob = base.ant_glob(pat)
    ctx.install_files(sharedir, glob, cwd = base, relative_trick = True)

    # Install factor.image and boot image
    ctx.install_files(libdir, [image_target, boot_image_name])
    ctx.symlink_as(
        '${PREFIX}/bin/%s' % image_target,
        '../lib/factor/%s' % image_target
    )
