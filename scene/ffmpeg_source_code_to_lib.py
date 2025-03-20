# 将 ffmpeg 的源码编译到指定的平台库
import os
import subprocess
import sys
import re
import platform

from localization.localization import get_localized_text
from utils.file_utils import select_source

# 设置最低部署目标
DEPLOYMENT_IOS_TARGET = "13.0"
# 设置目标架构（真机 arm64，模拟器 x86_64）
ARCHS = ["arm64"]

# 目标平台
TARGET_OS = "ios"


def configure_ffmpeg(path, target_os, arch, prefix):
    configure_command = [
        './configure',
        f'--target-os={target_os}',
        f'--arch={arch}',
        '--enable-shared',
        '--disable-static',
        f'--prefix={prefix}',
        '--enable-pic',
        '--disable-everything',
    ]

    try:
        subprocess.run(configure_command, check=True, cwd=path, stdout=sys.stdout, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error occurred while configuring FFmpeg:")
        print(e.stderr.decode())  # 打印详细错误信息
        raise
    # subprocess.run(configure_command, check=True, cwd=path)


def make_and_install():
    subprocess.run(['make'], check=True)
    subprocess.run(['make', 'install'], check=True)


def run_ffmpeg_make():
    # directory = select_source(only_folder=True).strip()
    directory = "/Users/wangdegui/Documents/FFMPEG/Source/FFmpeg-master"
    # compile_ffmpeg_make(directory)
    # ios_generate_ffmpeg(directory)
    # dir_arm64 = "/Users/wangdegui/Documents/FFMPEG/ios-build/arm64"
    clear_versions("/Users/wangdegui/Documents/FFMPEG/ios-build", "arm64")

def compile_ffmpeg_make(path):
    """编译ffmpeg需要的环境 x264、libvpx、openssl"""
    dependent_urls = [
        "https://code.videolan.org/videolan/x264.git",
        "https://chromium.googlesource.com/webm/libvpx",
        "https://github.com/openssl/openssl.git"
    ]
    parent_dir = os.path.dirname(os.path.dirname(path))
    dependent_dir = os.path.join(parent_dir, "ffmpeg-dependent-source")
    dependent_make_dir = os.path.join(parent_dir, "ffmpeg-dependent-make")
    for dependent_url in dependent_urls:
        dependent_name = os.path.basename(dependent_url).rstrip(".git")
        # 目标源码的克隆地址
        target_source_dir = os.path.join(dependent_dir, f"{TARGET_OS}_{dependent_name}")
        target_make_dir = os.path.join(dependent_make_dir, f"{TARGET_OS}_{dependent_name}")
        try:
            if not os.path.exists(target_source_dir):
                print("执行了 克隆 的操作")
                # 克隆仓库
                subprocess.run(["git", "clone", dependent_url, target_source_dir], check=True)

            # 进入克隆的目录
            os.chdir(target_source_dir)
            for ARCH in ARCHS:
                platform = "iphonesimulator" if ARCH == "x86_64" else "iphoneos"
                # 获取 SDK 路径
                SYSROOT = subprocess.check_output(
                    ["xcrun", "--sdk", platform, "--show-sdk-path"]).decode().strip()
                configure_flags = [
                    "./configure",
                    f"--prefix={os.path.join(target_make_dir, ARCH)}",
                    "--enable-static",
                    f"--extra-cflags=-arch {ARCH} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT}",
                ]
                if dependent_name == "x264":
                    configure_flags.append("--host=arm-apple-darwin")
                    configure_flags.append("--disable-asm")
                    configure_flags.append("--disable-cli")
                    configure_flags.append(
                        f"--extra-ldflags=-arch {ARCH} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT}")
                elif dependent_name == "libvpx":
                    target = "arm64-darwin-gcc"
                    if ARCH == "x86_64":
                        target = "x86-iphonesimulator-gcc"
                    configure_flags.append(f"--target={target}")
                    configure_flags.append("--enable-vp9")
                    configure_flags.append("--disable-examples")
                    configure_flags.append("--disable-tools")
                    configure_flags.append("--disable-docs")
                    configure_flags.append(
                        f"--extra-cxxflags=-arch {ARCH} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT}")
                elif dependent_name == "openssl":
                    configure_flags = [
                        "./configure",
                        f"--prefix={os.path.join(target_make_dir, ARCH)}",
                        f"CFLAGS=-arch {ARCH} -isysroot {SYSROOT} -mios-version-min={DEPLOYMENT_IOS_TARGET}",
                    ]

                # --extra - cflags = "-arch arm64 -mios-version-min=13.0 -isysroot $(xcrun --sdk iphoneos --show-sdk-path)"
                # --extra - cxxflags = "-arch arm64 -mios-version-min=13.0 -isysroot $(xcrun --sdk iphoneos --show-sdk-path)"
                # 如果需要 make 的库已经存在的情况不再执行
                if os.path.exists(os.path.join(target_make_dir, ARCH)):
                    continue
                # 打印出完整的命令
                print("Running command:", " ".join(configure_flags))
                subprocess.run(configure_flags, check=True)
                subprocess.run(["make"], check=True)
                subprocess.run(["make", "install"], check=True)
                print(f"install name: {dependent_name}, platform: {platform} complete")

        except subprocess.CalledProcessError as e:
            print("Error occurred while clone: {}".format(e.stderr.decode()))


def ios_generate_ffmpeg(path):
    """
    path = FFmpeg 源码路径
    iOS 编译FFMPeg
    """
    # 设置目标架构（真机 arm64，模拟器 x86_64）
    # ARCHS = ["arm64", "x86_64"]
    # 获取当前 Xcode SDK 版本
    IOS_SDK_VERSION = subprocess.check_output(
        ["xcrun", "--sdk", "iphoneos", "--show-sdk-version"]).decode().strip()
    # 获取它的上级目录
    parent_dir = os.path.dirname(os.path.dirname(path))
    # 输出目录
    OUTPUT_DIR = os.path.join(parent_dir, "ios-build")

    dependent_dir = os.path.join(parent_dir, "ffmpeg-dependent-make")

    # 清理旧的编译文件
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            os.remove(os.path.join(root, file))

    # 开始编译不同架构的 FFmpeg
    for ARCH in ARCHS:
        PLATFORM = "iphonesimulator" if ARCH == "x86_64" else "iphoneos"
        # 获取 SDK 路径
        SYSROOT = subprocess.check_output(
            ["xcrun", "--sdk", PLATFORM, "--show-sdk-path"]).decode().strip()
        x264I = "ios_x264/arm64/include"
        x264L = "ios_x264/arm64/lib"
        libvpxI = "ios_libvpx/arm64/include"
        libvpxL = "ios_libvpx/arm64/lib"
        sslI = "ios_openssl/arm64/include"
        sslL = "ios_openssl/arm64/lib"
        # 设置编译器
        # CC = subprocess.check_output(["xcrun", "--sdk", "iphoneos", "-find", "clang"]).decode().strip()
        print(f"Building for architecture: {ARCH}")
        # 配置 FFmpeg 编译参数
        configure_cmd = [
            "./configure",
            f"--prefix={os.path.join(OUTPUT_DIR, ARCH)}",
            f"--arch={ARCH}",
            "--target-os=darwin",
            "--enable-cross-compile",
            "--enable-shared",
            "--disable-static",
            "--disable-autodetect",
            "--enable-pic",
            "--enable-libx264",
            "--enable-libvpx",
            "--enable-openssl",
            "--enable-nonfree",
            "--enable-gpl",
            f"--extra-cflags=-arch {ARCH} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT} -D__STDC_NO_STDBIT__ "
            f"-I{os.path.join(dependent_dir, x264I)} "
            f"-I{os.path.join(dependent_dir, libvpxI)} "
            f"-I{os.path.join(dependent_dir, sslI)}",
            f"--extra-ldflags=-arch {ARCH} -isysroot {SYSROOT} "
            f"-L{os.path.join(dependent_dir, x264L)} "
            f"-L{os.path.join(dependent_dir, libvpxL)} "
            f"-L{os.path.join(dependent_dir, sslL)} "
            "-framework AudioToolbox -framework CoreAudio",
            f"--sysroot={SYSROOT}",
            f"--cc=xcrun --sdk {PLATFORM} clang",
            "--disable-programs",
            "--disable-doc",
            "--install-name-dir=@rpath"
        ]

        # 执行配置
        subprocess.run(configure_cmd, check=True, cwd=path)

        # 编译 FFmpeg
        subprocess.run(["make", "-j" + str(os.cpu_count())], check=True, cwd=path)

        # 安装到指定目录
        subprocess.run(["make", "install"], check=True, cwd=path)
        # 清除
        subprocess.run(["make", "clean"], check=True, cwd=path)
        clear_versions(OUTPUT_DIR, ARCH)


def clear_versions(root_dir, arch):
    """
    Clear all versions of ffmpeg source files.
    """
    lib_dir = os.path.join(root_dir, arch, "lib")
    os.chdir(lib_dir)
    for file in os.listdir(lib_dir):
        if os.path.islink(file):
            os.unlink(file)
        else:
            # 使用正则表达式匹配文件名中的版本号部分，并去除
            rename_file = re.sub(r'\.\d+(\.\d+)*\.dylib$', '.dylib', file)
            # 重命名文件
            try:
                os.rename(file, rename_file)
            except FileNotFoundError:
                print(f"File {file} not found.")
            except Exception as e:
                print(f"Error renaming file: {e}")
    # 创建 framework 目录
    # FRAMEWORK_DIR = os.path.join(OUTPUT_DIR, "FFmpeg.framework")
    # os.makedirs(os.path.join(FRAMEWORK_DIR, "Headers"), exist_ok=True)
    #
    # # 复制头文件
    # header_source = os.path.join(OUTPUT_DIR, "arm64", "include")
    # header_target = os.path.join(FRAMEWORK_DIR, "Headers")
    # for header in os.listdir(header_source):
    #     header_path = os.path.join(header_source, header)
    #     if os.path.isfile(header_path):
    #         subprocess.run(["cp", "-R", header_path, header_target])

    # 合并不同架构的静态库
    # lipo_cmd = [
    #     "lipo", "-create", "-output", os.path.join(FRAMEWORK_DIR, "FFmpeg"),
    #     os.path.join(OUTPUT_DIR, "arm64", "lib", "libavcodec.a"),
    #     os.path.join(OUTPUT_DIR, "x86_64", "lib", "libavcodec.a")
    # ]
    # subprocess.run(lipo_cmd, check=True)
