import os
import shutil
import json
from pathlib import Path

# ===== 配置 =====
SRC_ASSETS = Path("src/assets")
TEMPLATE_MERGED = Path("src/pack.mcmeta.merged.template")
TEMPLATE_INDIVIDUAL = Path("src/pack.mcmeta.individual.template")
README_FILE = Path("README.md")
DIST_DIR = Path("dist")

# ===== 工具函数：将文件夹名转为显示名称 =====
def folder_to_display_name(folder_name: str) -> str:
    SPECIAL_MAP = {
        "vms": "VMS",
        "aes_ministry": "AES Ministry",
        "old_road_sign": "Old Road Sign",
        "motorway_permanent": "Motorway Permanent",
        "transport_medium": "Transport Medium",
    }
    if folder_name in SPECIAL_MAP:
        return SPECIAL_MAP[folder_name]
    if folder_name.isupper():
        return folder_name
    name = folder_name.replace('_', ' ')
    return name.title()

# ===== 构建合并包 =====
def build_merged():
    print("🔨 正在构建合并包...")
    out_dir = DIST_DIR / "merged"
    assets_out = out_dir / "assets"
    
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(assets_out, exist_ok=True)
    
    for font_dir in SRC_ASSETS.iterdir():
        if font_dir.is_dir():
            shutil.copytree(font_dir, assets_out / font_dir.name)
    
    shutil.copy(TEMPLATE_MERGED, out_dir / "pack.mcmeta")
    
    if README_FILE.exists():
        shutil.copy(README_FILE, out_dir / "README.md")
    
    zip_path = DIST_DIR / "British Road Sign Fonts"
    shutil.make_archive(str(zip_path), 'zip', out_dir)
    
    shutil.rmtree(out_dir, ignore_errors=True)
    print("✅ 合并包已生成: dist/British Road Sign Fonts.zip")

# ===== 构建独立包 =====
def build_individual():
    print("🔨 正在构建独立包...")
    
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
        
        out_dir = individuals_dir / font_name
        assets_out = out_dir / "assets" / font_name
        os.makedirs(assets_out, exist_ok=True)
        
        src_font = font_dir / "font"
        if src_font.exists() and src_font.is_dir():
            shutil.copytree(src_font, assets_out / "font")
        else:
            print(f"⚠️ 警告: {font_dir}/font 不存在，跳过")
            continue
        
        # 生成 pack.mcmeta —— 与合并包格式一致
        meta = json.loads(json.dumps(template))
        meta["pack"]["description"] = meta["pack"]["description"].replace(
            "{FONT_DISPLAY_NAME}", display_name
        )
        
        desc_escaped = json.dumps(meta["pack"]["description"], ensure_ascii=False)
        pack_format = meta["pack"]["pack_format"]
        min_f = meta["pack"]["min_format"]
        max_f = meta["pack"]["max_format"]
        
        content = f'''{{
    "pack": {{
        "description": {desc_escaped},
        "pack_format": {pack_format},
        "supported_formats": [{min_f}, {max_f}],
        "min_format": {min_f},
        "max_format": {max_f}
    }}
}}
'''
        with open(out_dir / "pack.mcmeta", 'w', encoding='utf-8') as f:
            f.write(content)
        
        if README_FILE.exists():
            shutil.copy(README_FILE, out_dir / "README.md")
        
        # 打包到 dist/ 根目录
        zip_name = f"{display_name} Font"
        shutil.make_archive(
            str(DIST_DIR / zip_name),
            'zip',
            out_dir
        )
        print(f"   ✅ 已生成: {zip_name}.zip")
    
    shutil.rmtree(individuals_dir, ignore_errors=True)
    print("✅ 所有独立包已生成")

# ===== 主入口 =====
if __name__ == "__main__":
    DIST_DIR.mkdir(exist_ok=True)
    build_merged()
    build_individual()
    print("\n🎉 全部构建完成！")