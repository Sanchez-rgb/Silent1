"""文档转换模块 - Word转PDF"""
import os
import subprocess
import tempfile
import platform
from pathlib import Path
from typing import Optional, List, Tuple
import shutil


class ConverterError(Exception):
    """转换错误"""
    pass


class DocumentConverter:
    """文档转换器"""
    
    def __init__(self, upload_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """初始化转换器"""
        self.upload_dir = upload_dir or tempfile.mkdtemp(prefix="doc_upload_")
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="doc_output_")
        
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def convert_docx_to_pdf(self, docx_path: str, output_path: Optional[str] = None) -> str:
        """
        转换DOCX文件为PDF
        
        Args:
            docx_path: DOCX文件路径
            output_path: 输出PDF路径
            
        Returns:
            PDF文件路径
        """
        if not os.path.exists(docx_path):
            raise ConverterError(f"文件不存在: {docx_path}")
        
        if output_path is None:
            output_path = os.path.join(
                self.output_dir,
                os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
            )
        
        system = platform.system().lower()
        
        try:
            if system == "windows":
                self._convert_with_word(docx_path, output_path)
            else:
                self._convert_with_libreoffice(docx_path, output_path)
            
            if not os.path.exists(output_path):
                raise ConverterError(f"PDF文件未生成: {output_path}")
            
            return output_path
            
        except Exception as e:
            raise ConverterError(f"转换失败: {str(e)}")
    
    def _convert_with_word(self, docx_path: str, pdf_path: str):
        """使用Microsoft Word转换（Windows）"""
        try:
            import comtypes.client as client
            import pythoncom
            
            pythoncom.CoInitialize()
            
            try:
                word = client.CreateObject("Word.Application")
                word.Visible = False
                
                try:
                    doc = word.Documents.Open(os.path.abspath(docx_path))
                    doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # wdFormatPDF = 17
                    doc.Close()
                finally:
                    word.Quit()
            finally:
                pythoncom.CoUninitialize()
                
        except ImportError:
            # comtypes未安装，尝试使用docx2pdf
            try:
                from docx2pdf import convert
                convert(docx_path, pdf_path)
            except Exception as e:
                raise ConverterError(f"Word转换失败，请安装Microsoft Word或LibreOffice: {e}")
        except Exception as e:
            raise ConverterError(f"Word COM调用失败: {e}")
    
    def _convert_with_libreoffice(self, docx_path: str, pdf_path: str):
        """使用LibreOffice转换（Linux/macOS）"""
        output_dir = os.path.dirname(pdf_path) or self.output_dir
        
        # 尝试不同的命令名
        commands = ["libreoffice", "soffice"]
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    [
                        cmd,
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", output_dir,
                        os.path.abspath(docx_path)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # LibreOffice会在output_dir生成PDF
                    expected_pdf = os.path.join(
                        output_dir,
                        os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
                    )
                    
                    if os.path.exists(expected_pdf) and expected_pdf != pdf_path:
                        shutil.move(expected_pdf, pdf_path)
                    
                    return
                    
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                raise ConverterError("转换超时，请检查文件大小")
        
        raise ConverterError("未找到LibreOffice，请安装LibreOffice")
    
    def batch_convert(self, docx_files: List[str]) -> List[str]:
        """
        批量转换DOCX文件
        
        Args:
            docx_files: DOCX文件路径列表
            
        Returns:
            PDF文件路径列表
        """
        pdf_files = []
        errors = []
        
        for docx_path in docx_files:
            try:
                pdf_path = self.convert_docx_to_pdf(docx_path)
                pdf_files.append(pdf_path)
            except ConverterError as e:
                errors.append(f"{os.path.basename(docx_path)}: {str(e)}")
        
        if errors:
            raise ConverterError(f"部分文件转换失败: {'; '.join(errors)}")
        
        return pdf_files
    
    def cleanup(self):
        """清理临时文件"""
        for directory in [self.upload_dir, self.output_dir]:
            try:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
            except Exception:
                pass
    
    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        return {
            "name": os.path.basename(file_path),
            "size": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "extension": os.path.splitext(file_path)[1].lower()
        }


def convert_single_file(file_path: str, output_path: Optional[str] = None) -> str:
    """便捷函数：转换单个文件"""
    converter = DocumentConverter()
    return converter.convert_docx_to_pdf(file_path, output_path)


def validate_file(file_path: str) -> Tuple[bool, str]:
    """验证文件是否有效"""
    if not os.path.exists(file_path):
        return False, "文件不存在"
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.doc', '.docx']:
        return False, f"不支持的文件格式: {ext}，仅支持.doc和.docx"
    
    size_mb = os.path.getsize(file_path) / 1024 / 1024
    if size_mb > 50:
        return False, f"文件过大: {size_mb:.2f}MB，最大支持50MB"
    
    return True, "文件有效"
