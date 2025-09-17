#!/usr/bin/env python3
"""
Build script for MyCrypto frontend assets
Handles JS/CSS minification for production deployment
"""

import os
import subprocess
import shutil
from pathlib import Path

def ensure_dist_directory():
    """Create dist directory if it doesn't exist"""
    dist_dir = Path("static/dist")
    dist_dir.mkdir(parents=True, exist_ok=True)
    return dist_dir

def check_node_dependencies():
    """Check if Node.js dependencies are installed"""
    if not Path("node_modules").exists():
        print("Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], check=True)

def build_javascript():
    """Minify JavaScript files"""
    print("Building JavaScript assets...")
    
    js_files = [
        "static/js/api.js",
        "static/js/auth.js", 
        "static/js/dashboard.js",
        "static/js/websocket.js"
    ]
    
    # Check if all JS files exist
    for js_file in js_files:
        if not Path(js_file).exists():
            print(f"Warning: {js_file} not found, skipping...")
            js_files.remove(js_file)
    
    if js_files:
        cmd = [
            "npx", "terser"
        ] + js_files + [
            "--compress",
            "--mangle", 
            "--source-map",
            "--output", "static/dist/app.min.js"
        ]
        
        subprocess.run(cmd, check=True)
        print("✓ JavaScript minified successfully")
    else:
        print("No JavaScript files found to minify")

def build_css():
    """Minify CSS files"""
    print("Building CSS assets...")
    
    css_files = [
        "static/css/auth.css",
        "static/css/dashboard.css"
    ]
    
    # Check if all CSS files exist
    existing_css = [f for f in css_files if Path(f).exists()]
    
    if existing_css:
        # Concatenate CSS files first, then minify
        combined_css = ""
        for css_file in existing_css:
            with open(css_file, 'r', encoding='utf-8') as f:
                combined_css += f"/* {css_file} */\n"
                combined_css += f.read() + "\n\n"
        
        # Write combined CSS to temp file
        temp_css = Path("static/dist/temp.css")
        with open(temp_css, 'w', encoding='utf-8') as f:
            f.write(combined_css)
        
        # Minify the combined file
        cmd = [
            "npx", "csso-cli",
            str(temp_css),
            "--output", "static/dist/app.min.css"
        ]
        
        subprocess.run(cmd, check=True)
        
        # Clean up temp file
        temp_css.unlink()
        
        print("✓ CSS minified successfully")
    else:
        print("No CSS files found to minify")

def get_file_sizes():
    """Display file sizes for comparison"""
    print("\n📊 File Size Comparison:")
    
    # Original files
    original_js_size = 0
    js_files = ["static/js/api.js", "static/js/auth.js", "static/js/dashboard.js", "static/js/websocket.js"]
    for js_file in js_files:
        if Path(js_file).exists():
            original_js_size += Path(js_file).stat().st_size
    
    original_css_size = 0
    css_files = ["static/css/auth.css", "static/css/dashboard.css"]
    for css_file in css_files:
        if Path(css_file).exists():
            original_css_size += Path(css_file).stat().st_size
    
    # Minified files
    minified_js = Path("static/dist/app.min.js")
    minified_css = Path("static/dist/app.min.css")
    
    if minified_js.exists():
        minified_js_size = minified_js.stat().st_size
        js_reduction = ((original_js_size - minified_js_size) / original_js_size) * 100
        print(f"JavaScript: {original_js_size:,} bytes → {minified_js_size:,} bytes ({js_reduction:.1f}% reduction)")
    
    if minified_css.exists():
        minified_css_size = minified_css.stat().st_size
        css_reduction = ((original_css_size - minified_css_size) / original_css_size) * 100
        print(f"CSS: {original_css_size:,} bytes → {minified_css_size:,} bytes ({css_reduction:.1f}% reduction)")

def main():
    """Main build process"""
    print("🚀 Starting MyCrypto frontend build process...")
    
    try:
        # Ensure dist directory exists
        ensure_dist_directory()
        
        # Check Node.js dependencies
        check_node_dependencies()
        
        # Build assets
        build_javascript()
        build_css()
        
        # Show file sizes
        get_file_sizes()
        
        print("\n✅ Build completed successfully!")
        print("Minified assets are available in static/dist/")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
