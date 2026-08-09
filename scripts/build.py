import os
import shutil
import json
import re
from pathlib import Path

# ===== 配置 =====
SRC_ASSETS = Path("src/assets")
TEMPLATE_MERGED = Path("src/pack.mcmeta.merged.template")
TEMPLATE_INDIVIDUAL = Path("src/pack.mcmeta.individual.template")
DIST_DIR = Path("dist")

# ===== 工具函数：将文件夹名转为显示名称 =====
def folder_to_display_name(folder_name: str) -> str:
    """
    将文件夹名转换为用户友好的显示名称。
    示例：
        vms              -> VMS
        motorway_permanent -> Motorway Permanent
        transport        -> Transport
    """
    # 如果全是大写字母（如 VMS），保持原样
    if folder_name.isupper():
        return folder_name
    
    # 将下划线替换为空格
    name = folder_name.replace('_', ' ')
    
    # 每个单词首字母大写
    return name.title()

# ===== 构建合并包 =====
def build_merged():
    print("🔨 正在构建合并包...")
    out_dir = DIST_DIR / "merged"
    assets_out = out_dir / "assets"
    
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(assets_out, exist_ok=True)
    
    # 1. 复制所有字体文件夹
    for font_dir in SRC_ASSETS.iterdir():
        if font_dir.is_dir():
            shutil.copytree(font_dir, assets_out / font_dir.name)
    
    # 2. 复制 pack.mcmeta（合并版）
    shutil.copy(TEMPLATE_MERGED, out_dir / "pack.mcmeta")
    
    # 3. 打包
    shutil.make_archive(
        str(DIST_DIR / "British-Road-Sign-Fonts-Merged"),
        'zip',
        out_dir
    )
    print("✅ 合并包已生成: dist/British-Road-Sign-Fonts-Merged.zip")

# ===== 构建独立包 =====
def build_individual():
    print("🔨 正在构建独立包...")
    
    # 加载模板
    with open(TEMPLATE_INDIVIDUAL, 'r', encoding='utf-8') as f:
        template = json.load(f)
    
    individuals_dir = DIST_DIR / "individuals"
    shutil.rmtree(individuals_dir, ignore_errors=True)
    os.makedirs(individuals_dir, exist_ok=True)
    
    for font_dir in SRC_ASSETS.iterdir():
        if not font_dir.is_dir():
            continue
        
        font_name = font_dir.name
        display_name = folder_to_display_name(font_name)
        
        # 当前独立包的输出目录
        out_dir = individuals_dir / font_name
        assets_out = out_dir / "assets" / font_name
        os.makedirs(assets_out, exist_ok=True)
        
        # 1. 复制该字体的 font 文件夹（保持原有结构）
        src_font = font_dir / "font"
        if src_font.exists() and src_font.is_dir():
            shutil.copytree(src_font, assets_out / "font")
        else:
            print(f"⚠️ 警告: {font_dir}/font 不存在，跳过")
            continue
        
        # 2. 生成该包的 pack.mcmeta（替换占位符）
        meta = json.loads(json.dumps(template))  # 深拷贝
        meta["pack"]["description"] = meta["pack"]["description"].replace(
            "{FONT_DISPLAY_NAME}", display_name
        )
        
        with open(out_dir / "pack.mcmeta", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)
        
        # 3. 打包
        zip_name = f"British-Road-Sign-Font-{display_name.replace(' ', '-')}"
        shutil.make_archive(
            str(individuals_dir / zip_name),
            'zip',
            out_dir
        )
        print(f"   ✅ 已生成: {zip_name}.zip")
    
    print("✅ 所有独立包已生成")

# ===== 主入口 =====
if __name__ == "__main__":
    DIST_DIR.mkdir(exist_ok=True)
    build_merged()
    build_individual()
    print("\n🎉 全部构建完成！")
