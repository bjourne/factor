from os import path
from waflib import Task, TaskGen

APPNAME = 'factor-lang'
VERSION = '0.96'

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

def copy_file(ctx, source, target):
    ctx(
        rule = 'cp ${SRC[0].abspath()} ${TGT[0].abspath()}',
        source = source,
        target = target
        )

# WIX support
TaskGen.declare_chain(
    name = 'wxs',
    rule = 'candle.exe -nologo -out ${TGT} ${SRC}',
    ext_in = '.wxs',
    ext_out = '.wxsobj')
TaskGen.declare_chain(
    name = 'wxsobj',
    rule = 'light.exe -nologo -out ${TGT} ${SRC}',
    ext_in = '.wxsobj',
    ext_out = '.msi')


# This monkey patching enables syncronous output from rule tasks.
# https://groups.google.com/d/msg/waf-users/2uA3DEltTKg/8T4X9I4OeeQJ
def my_exec_command(self, cmd, **kw):
    bld = self.generator.bld
    try:
        if not kw.get('cwd', None):
            kw['cwd'] = bld.cwd
    except AttributeError:
        bld.cwd = kw['cwd'] = bld.variant_dir
    kw["stdout"] = kw["stderr"] = None
    return bld.exec_command(cmd, **kw)
Task.TaskBase.exec_command = my_exec_command

def options(ctx):
    ctx.load('compiler_c compiler_cxx')

def configure(ctx):
    ctx.env['MSVC_VERSIONS'] = ['msvc 10.0']
    ctx.load('compiler_c compiler_cxx')
    ctx.check(features='cxx cxxprogram', cflags=['-Wall'])
    env = ctx.env
    dest_cpu = env.DEST_CPU
    dest_os = env.DEST_OS
    bits = {'amd64' : 64, 'i386' : 32, 'x86_64' : 64}[dest_cpu]
    if dest_os == 'win32':
        ctx.check_lib_msvc('shell32')
        env.CXXFLAGS += ['/EHsc', '/O2', '/WX', '/W3']
        if dest_cpu == 'i386':
            env.LINKFLAGS.append('/safesh')
        ctx.load('winres')
        env.WINRCFLAGS.append('/nologo')
        ctx.define('_CRT_SECURE_NO_WARNINGS', None)
        # WIX checks
        ctx.find_program('candle')
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
        ctx.check_cfg(atleast_pkgconfig_version='0.0.0')
        ctx.check_cfg(
            package = 'gtk+-2.0',
            uselib_store = 'gtk',
            atleast_version = '2.18.0',
            args = '--cflags --libs',
            mandatory = True
        )
        ctx.check_cfg(
            package = 'gtkglext-1.0',
            uselib_store = 'gtkglext',
            atleast_version = '1.0.0',
            args = '--cflags --libs',
            mandatory = True
        )

        env.CXXFLAGS += ['-O3', '-fomit-frame-pointer']
        if bits == 64:
            env.CXXFLAGS += ['-m64']
        env.LINKFLAGS += ['-Wl,--no-as-needed', '-Wl,--export-dynamic']
    ctx.define('INSTALL_PREFIX', ctx.options.prefix)

def build(ctx):
    dest_os = ctx.env.DEST_OS
    dest_cpu = ctx.env.DEST_CPU

    bits = {'amd64' : 64, 'i386' : 32, 'x86_64' : 64}[dest_cpu]
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
        ctx.program(
            features = features,
            source = [],
            target = APPNAME,
            use = link_libs,
            linkflags = '/SUBSYSTEM:windows'
            )
        # The node name can't be factor.com because it will clash with
        # the previously created factor.exe node.
        target = ctx.path.get_bld().make_node('tmp.com')
        ctx.program(
            features = features,
            source = [],
            target = target,
            use = link_libs,
            linkflags = '/SUBSYSTEM:console'
        )
        copy_file(ctx, 'tmp.com', '%s.com' % APPNAME)
        # Can you indicate that the exe and com files need to be built
        # before this target?
        ctx(source = ['factor.wxs'])
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
        target = 'factor-ffi-test',
        source = ['vm/ffi_test.c'],
        install_path = libdir
    )

    # Build factor.image using the newly built executable.
    os_family = {'linux' : 'unix', 'win32' : 'windows'}[dest_os]
    source_image = 'boot-images/boot.%s-x86.%s.image' % (os_family, bits)

    # On Windows, boot.image must reside in the projects root dir. Not
    # sure if, or why, it is different on Linux. -resource-path
    # doesn't seem to have much effect.
    boot_image = {'win32' : '../boot.image', 'linux' : 'boot.image'}[dest_os]
    copy_file(ctx, source_image, boot_image)

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
        source = [factor_exe, boot_image],
        target = old_image
    )

    # Image built, but it needs to be updated too.
    real_image = '%s.image' % APPNAME
    params = [
        '-script',
        '-resource-path=..',
        '-i=%s' % old_image,
        '-e="USING: vocabs.loader vocabs.refresh system memory ; '
        'refresh-all \\"%s\\" save-image-and-exit"' % real_image
    ]
    ctx(
        rule = '${SRC[0].abspath()} ' + ' '.join(params),
        source = [factor_exe, old_image],
        target = real_image
    )

    # Install standard library
    pat = '(basis|core|extra)/**/*.(c|factor|png|tiff|TXT|txt)'
    glob = cwd.ant_glob(pat)

    ctx.install_files(libdir, glob, cwd = cwd, relative_trick = True)
    ctx.install_files(libdir, 'license.txt', cwd = cwd)

    # Install stuff in misc
    sharedir = '${PREFIX}/share/factor'
    base = cwd.find_dir('misc')
    pat = '(fuel|icons|textadept|vim)/**/*.(el|lua|png|vim)'
    glob = base.ant_glob(pat)
    ctx.install_files(sharedir, glob, cwd = base, relative_trick = True)

    # Install image
    ctx.install_files(libdir, real_image)
    ctx.symlink_as(
        '${PREFIX}/bin/%s' % real_image,
        '../lib/factor/%s' % real_image
    )
