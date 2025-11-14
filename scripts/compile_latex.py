"""
Script để biên dịch file LaTeX sang PDF
Sử dụng package pdflatex từ pip
"""

import sys
import os
from pathlib import Path

def compile_latex(tex_file):
    """
    Biên dịch file LaTeX sang PDF
    
    Args:
        tex_file: Đường dẫn đến file .tex
    """
    try:
        # Kiểm tra file có tồn tại không
        if not os.path.exists(tex_file):
            print(f"❌ Không tìm thấy file: {tex_file}")
            return False
        
        print(f"📄 Đang biên dịch: {tex_file}")
        
        # Thử dùng pdflatex module
        try:
            import pdflatex
            pdf = pdflatex.PDFLaTeX.from_texfile(tex_file)
            pdf.set_pdf_filename(tex_file.replace('.tex', '.pdf'))
            pdf.create_pdf(keep_pdf_file=True, keep_log_file=True)
            print("✅ Biên dịch thành công!")
            return True
        except ImportError:
            print("⚠️ Module pdflatex không khả dụng")
        except Exception as e:
            print(f"⚠️ Lỗi khi dùng pdflatex module: {e}")
            print("💡 Có thể cần cài đặt LaTeX distribution (MiKTeX hoặc TeX Live)")
        
        # Thử dùng subprocess để gọi pdflatex trực tiếp
        import subprocess
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', tex_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Biên dịch thành công!")
            return True
        else:
            print("❌ Lỗi biên dịch:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Không tìm thấy pdflatex command")
        print("\n💡 Giải pháp:")
        print("1. Cài đặt MiKTeX: https://miktex.org/download")
        print("2. Hoặc sử dụng Overleaf online: https://www.overleaf.com")
        print("3. Hoặc cài TeX Live: https://www.tug.org/texlive/")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False


if __name__ == '__main__':
    # File LaTeX mặc định
    default_file = 'Trading_Bot_Ly_Thuyet.tex'
    
    # Lấy file từ command line hoặc dùng mặc định
    tex_file = sys.argv[1] if len(sys.argv) > 1 else default_file
    
    print("=" * 60)
    print("🔧 LaTeX Compiler")
    print("=" * 60)
    print()
    
    success = compile_latex(tex_file)
    
    if success:
        pdf_file = tex_file.replace('.tex', '.pdf')
        if os.path.exists(pdf_file):
            print(f"\n📄 File PDF đã được tạo: {pdf_file}")
    else:
        print("\n💡 Gợi ý:")
        print("   - Sử dụng Overleaf (miễn phí, không cần cài đặt)")
        print("   - Hoặc cài MiKTeX/TeX Live để biên dịch local")

