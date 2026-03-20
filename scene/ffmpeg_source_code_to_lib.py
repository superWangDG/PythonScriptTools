# 将 ffmpeg 的源码编译到指定的平台库
import os
import shutil
import subprocess
import sys
import re
import platform

from localization.localization import get_localized_text
from utils.file_utils import select_source

# 设置最低部署目标
DEPLOYMENT_IOS_TARGET = "13.0"
# 设置目标架构（真机 arm64，模拟器 x86_64，苹果芯片的模拟器 arm64-sim ）
# ARCHS = ["arm64", "x86_64", "arm64-sim"]
ARCHS = ["arm64-sim"]

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
    compile_ffmpeg_make(directory)
    # ios_generate_ffmpeg(directory)
    # dir_arm64 = "/Users/wangdegui/Documents/FFMPEG/ios-build/arm64"
    # clear_versions("/Users/wangdegui/Documents/FFMPEG/ios-build", "arm64")
    # generate_framework_dir("/Users/wangdegui/Documents/FFMPEG/ios-build", "arm64")

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
                host = "x86_64-apple-darwin" if ARCH == "x86_64" else "apple-darwin"
                ARCH_NAME = ARCH
                if ARCH == "arm64-sim":
                    # 如果也是 m 系列模拟器
                    platform = "iphonesimulator"
                    host = "arm-apple-darwin"
                    ARCH_NAME = "arm64"
                # 获取 SDK 路径
                SYSROOT = subprocess.check_output(
                    ["xcrun", "--sdk", platform, "--show-sdk-path"]).decode().strip()
                configure_flags = [
                    "./configure",
                    f"--prefix={os.path.join(target_make_dir, ARCH)}",
                    "--enable-static",
                    f"--extra-cflags=-arch {ARCH_NAME} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT}",
                ]
                if dependent_name == "x264":
                    configure_flags.append(f"--host={host}")
                    configure_flags.append("--disable-asm")
                    configure_flags.append("--disable-cli")
                    configure_flags.append(
                        f"--extra-ldflags=-arch {ARCH_NAME} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT}")
                elif dependent_name == "libvpx":
                    target = "arm64-darwin-gcc"
                    if ARCH == "x86_64":
                        target = "x86_64-iphonesimulator-gcc"
                        configure_flags.append("--disable-runtime-cpu-detect")

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
    # IOS_SDK_VERSION = subprocess.check_output(
    #     ["xcrun", "--sdk", "iphoneos", "--show-sdk-version"]).decode().strip()
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
        if ARCH == "x86_64":
            PLATFORM = "iphonesimulator"
            ARCH_NAME = "x86_64"
            OUTPUT_ARCH_DIR = "x86_64"
        elif ARCH == "arm64-sim":
            PLATFORM = "iphonesimulator"
            ARCH_NAME = "arm64"
            OUTPUT_ARCH_DIR = "arm64-sim"
        else:  # arm64 真机
            PLATFORM = "iphoneos"
            ARCH_NAME = "arm64"
            OUTPUT_ARCH_DIR = "arm64"

        # 获取 SDK 路径
        SYSROOT = subprocess.check_output(
            ["xcrun", "--sdk", PLATFORM, "--show-sdk-path"]).decode().strip()
        x264I = f"ios_x264/{ARCH_NAME}/include"
        x264L = f"ios_x264/{ARCH_NAME}/lib"
        libvpxI = f"ios_libvpx/{ARCH_NAME}/include"
        libvpxL = f"ios_libvpx/{ARCH_NAME}/lib"
        sslI = f"ios_openssl/{ARCH_NAME}/include"
        sslL = f"ios_openssl/{ARCH_NAME}/lib"
        # 设置编译器
        # CC = subprocess.check_output(["xcrun", "--sdk", "iphoneos", "-find", "clang"]).decode().strip()
        print(f"Building for architecture: {ARCH_NAME}")
        # 配置 FFmpeg 编译参数
        configure_cmd = [
            "./configure",
            f"--prefix={os.path.join(OUTPUT_DIR, OUTPUT_ARCH_DIR)}",
            f"--arch={ARCH_NAME}",
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
            f"--extra-cflags=-arch {ARCH_NAME} -mios-version-min={DEPLOYMENT_IOS_TARGET} -isysroot {SYSROOT} -D__STDC_NO_STDBIT__ "
            f"-I{os.path.join(dependent_dir, x264I)} "
            f"-I{os.path.join(dependent_dir, libvpxI)} "
            f"-I{os.path.join(dependent_dir, sslI)}",
            f"--extra-ldflags=-arch {ARCH_NAME} -isysroot {SYSROOT} "
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


def generate_framework_dir(root_dir, arch):
    """
    Create .framework directories for each .dylib file.
    """
    lib_dir = os.path.join(root_dir, arch, "lib")
    include_dir = os.path.join(root_dir, arch, "include")
    frameworks_dir = os.path.join(root_dir, arch, "frameworks")

    os.makedirs(frameworks_dir, exist_ok=True)

    for file in os.listdir(lib_dir):
        print(f"file address: {file}")
        if file.endswith(".dylib") and file.startswith("lib"):
            dylib_path = os.path.join(lib_dir, file)

            # 提取框架名称并格式化成 LibXxx 形式
            framework_base_name = file[len("lib"):-len(".dylib")]  # e.g., avformat
            framework_name = f"Lib{framework_base_name}"  # e.g., LibAvformat

            # 创建 .framework 目录
            framework_dir = os.path.join(frameworks_dir, f"{framework_name}.framework")
            os.makedirs(framework_dir, exist_ok=True)

            # 拷贝 binary，并重命名为无后缀名（和 framework 同名）
            target_binary_path = os.path.join(framework_dir, framework_name)
            shutil.copyfile(dylib_path, target_binary_path)

            # 拷贝 Headers（include/libxxx -> Headers）
            header_src_dir = os.path.join(include_dir, f"lib{framework_base_name}")
            header_dest_dir = os.path.join(framework_dir, "Headers")
            if os.path.exists(header_src_dir):
                shutil.copytree(header_src_dir, header_dest_dir, dirs_exist_ok=True)
                print(f"📁 Headers copied to {framework_name}.framework/Headers")
            else:
                print(f"⚠️ Warning: Headers for lib{framework_base_name} not found.")

            # 写入 Info.plist
            plist_path = os.path.join(framework_dir, "Info.plist")
            with open(plist_path, "w") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{framework_name}</string>
    <key>CFBundleIdentifier</key>
    <string>org.clourdhearing.ffmpeg.{framework_base_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>FMWK</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>{framework_name}</string>
</dict>
</plist>
''')
            print(f"✅ Created framework: {framework_name}.framework\n")
