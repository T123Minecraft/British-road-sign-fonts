import os
import shutil
import json
from pathlib import Path

# 配置
SRC_ASSETS = Path("src/assets")
DIST_DIR = Path("dist")
TEMPLATE_MERGED = Path("src/pack.mcmeta.merged.template")
TEMPLATE_INDIVIDUAL = Path("src/pack.mcmeta.individual.template")

def build_merged():
    """构建合并包：assets 下包含所有字体"""
    out_dir = DIST_DIR / "merged"
    assets_out = out_dir / "assets"
    
    # 清空并重新创建
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(assets_out, exist_ok=True)
    
    # 1. 复制所有字体文件夹
    for font_dir in SRC_ASSETS.iterdir():
        if font_dir.is_dir():
            shutil.copytree(font_dir, assets_out / font_dir.name)
    
    # 2. 复制 pack.mcmeta（合并版）
    shutil.copy(TEMPLATE_MERGED, out_dir / "pack.mcmeta")
    
    # 3. 打包成 zip
    shutil.make_archive(str(DIST_DIR / "British-Road-Sign-Fonts-Merged"), 'zip', out_dir)
    print("✅ 合并包已生成")

def build_individual():
    """构建独立包：每个字体单独成一个包"""
    individuals_dir = DIST_DIR / "individuals"
    shutil.rmtree(individuals_dir, ignore_errors=True)
    os.makedirs(individuals_dir, exist_ok=True)
    
    # 加载独立包的模板内容（JSON 格式）
    with open(TEMPLATE_INDIVIDUAL, 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    for font_dir in SRC_ASSETS.iterdir():
        if not font_dir.is_dir():
            continue
        
        font_name = font_dir.name
        out_dir = individuals_dir / font_name
        assets_out = out_dir / "assets" / font_name
        
        # 1. 复制该字体的文件夹
        shutil.copytree(font_dir, assets_out / "font")
        # 注意：源结构是 assets/字体名/font/，这里保持相同
        
        # 2. 生成 pack.mcmeta（替换描述中的占位符）
        # 假设模板里有 "description": "British Road Sign - {FONT_NAME}"
        meta = json.loads(json.dumps(template_data))  # 深拷贝
        # 将描述中的占位符替换为实际字体名（首字母大写）
        display_name = font_name.capitalize()
        meta['pack']['description'] = meta['pack']['description'].replace('{FONT_NAME}', display_name)
        
        with open(out_dir / "pack.mcmeta", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        # 3. 单独打包每个字体
        zip_name = f"British-Road-Sign-Font-{font_name.capitalize()}"
        shutil.make_archive(str(individuals_dir / zip_name), 'zip', out_dir)
    
    print("✅ 独立包已生成")

if __name__ == "__main__":
    DIST_DIR.mkdir(exist_ok=True)
    build_merged()
    build_individual()
