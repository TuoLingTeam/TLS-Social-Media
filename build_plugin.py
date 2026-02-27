#!/usr/bin/env python3
"""
社交媒体 Copilot 插件构建脚本
一键执行：pnpm install → pnpm build → pnpm zip
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class PluginBuilder:
    def __init__(self, project_dir=None):
        """初始化构建器"""
        if project_dir is None:
            # 默认使用当前目录
            self.project_dir = Path.cwd()
        else:
            self.project_dir = Path(project_dir).resolve()
        
        self.package_json = self.project_dir / "package.json"
        self.output_dir = self.project_dir / "output"
        self.crx_file = None
        
    def check_prerequisites(self):
        """检查前置条件"""
        print("🔍 检查前置条件...")
        
        # 检查项目目录
        if not self.project_dir.exists():
            print(f"❌ 项目目录不存在: {self.project_dir}")
            return False
        
        # 检查 package.json
        if not self.package_json.exists():
            print(f"❌ 找不到 package.json，请确保在项目根目录")
            return False
        
        # 检查 pnpm 或 npm
        try:
            result = subprocess.run(
                ["pnpm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                pnpm_version = result.stdout.strip()
                print(f"✅ pnpm 已安装: {pnpm_version}")
                return True
        except FileNotFoundError:
            print("⚠️  pnpm 未找到，尝试使用 npm...")
        
        # 检查 npm
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"✅ npm 已安装: {npm_version}")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ 没有找到 pnpm 或 npm，请先安装")
        return False
    
    def run_command(self, cmd, description):
        """执行命令"""
        print(f"\n{'='*60}")
        print(f"📦 {description}")
        print(f"{'='*60}")
        print(f"执行命令: {' '.join(cmd)}\n")
        
        try:
            # 在项目目录中执行命令
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print(f"\n✅ {description} 成功")
                return True
            else:
                print(f"\n❌ {description} 失败 (exit code: {result.returncode})")
                return False
        except subprocess.TimeoutExpired:
            print(f"\n❌ {description} 超时（>5分钟）")
            return False
        except Exception as e:
            print(f"\n❌ {description} 出错: {e}")
            return False
    
    def find_crx_file(self):
        """查找生成的 CRX 文件"""
        if not self.output_dir.exists():
            return None
        
        for crx_file in self.output_dir.glob("*.crx"):
            self.crx_file = crx_file
            return crx_file
        
        return None
    
    def rename_zip_file(self):
        """重命名生成的 ZIP 文件为 TLS-Social-Media.zip"""
        if not self.output_dir.exists():
            return None
        
        # 查找生成的 zip 文件
        zip_files = list(self.output_dir.glob("*.zip"))
        if not zip_files:
            return None
        
        # 重命名第一个找到的 zip 文件
        old_zip = zip_files[0]
        new_zip = self.output_dir / "TLS-Social-Media.zip"
        
        # 如果源文件和目标文件相同，直接返回
        if old_zip == new_zip:
            return new_zip
        
        # 如果目标文件已存在，先删除
        if new_zip.exists():
            new_zip.unlink()
        
        old_zip.rename(new_zip)
        return new_zip
    
    def build(self):
        """执行完整的构建流程"""
        print("\n" + "🚀" * 30)
        print("开始构建社交媒体 Copilot 插件")
        print("🚀" * 30)
        
        # 1. 检查前置条件
        if not self.check_prerequisites():
            return False
        
        # 2. 安装依赖
        print("\n")
        if not self.run_command(["pnpm", "install"], "安装依赖"):
            print("💡 提示: 如果 pnpm 不可用，尝试使用 npm install")
            if not self.run_command(["npm", "install"], "使用 npm 安装依赖"):
                return False
        
        # 3. 构建项目
        print("\n")
        if not self.run_command(["pnpm", "build"], "构建项目"):
            if not self.run_command(["npm", "run", "build"], "使用 npm 构建项目"):
                return False
        
        # 4. 打包为 CRX
        print("\n")
        if not self.run_command(["pnpm", "zip"], "打包为 CRX"):
            if not self.run_command(["npm", "run", "zip"], "使用 npm 打包"):
                return False
        
        # 5. 重命名 ZIP 文件
        zip_file = self.rename_zip_file()
        
        # 6. 查找输出文件
        crx_file = self.find_crx_file()
        
        print("\n" + "="*60)
        print("✅ 构建完成！")
        print("="*60)
        
        print(f"\n📁 输出目录: {self.output_dir}")
        print(f"   - output/chrome-mv3/        (未打包的扩展目录)")
        
        if zip_file:
            print(f"   - {zip_file.name}      (ZIP 压缩包)")
            print(f"\n💾 ZIP 文件路径: {zip_file}")
        
        if crx_file:
            print(f"   - {crx_file.name}           (可安装的 CRX 文件)")
            print(f"\n💾 CRX 文件路径: {crx_file}")
        
        print("\n" + "="*60)
        print("📖 使用方式:")
        print("="*60)
        print("\n方式 1️⃣: 直接加载文件夹")
        print(f"  1. 打开 chrome://extensions/")
        print(f"  2. 开启 '开发者模式'")
        print(f"  3. 点击 '加载未打包的扩展程序'")
        print(f"  4. 选择: {self.output_dir}/chrome-mv3")
        
        if crx_file:
            print("\n方式 2️⃣: 安装 CRX 文件")
            print(f"  1. 打开 chrome://extensions/")
            print(f"  2. 拖拽 CRX 文件到页面中")
            print(f"  3. 或双击 CRX 文件")
        
        print("\n方式 3️⃣: 分享给他人")
        if zip_file:
            print(f"  - 分享 {zip_file.name} 文件")
        print(f"  - 或分享 {self.output_dir}/chrome-mv3 文件夹")
        if crx_file:
            print(f"  - 或分享 {crx_file.name} 文件")
        
        print("\n" + "🎉" * 30)
        
        return True


def main():
    """主函数"""
    # 获取项目目录（支持命令行参数）
    project_dir = None
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    
    # 创建构建器并执行
    builder = PluginBuilder(project_dir)
    success = builder.build()
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()