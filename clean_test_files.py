#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python测试文件清理脚本
安全删除项目中以"test_"开头的测试文件，但保留必要的代码

作者: Python代码清理专家
版本: 1.0
"""

import os
import sys
import shutil
import re
import ast
import tempfile
import datetime
from typing import List, Dict, Tuple, Set
from pathlib import Path


class TestFileCleaner:
    """测试文件清理器"""
    
    def __init__(self, backup_enabled: bool = True):
        """
        初始化清理器
        
        Args:
            backup_enabled: 是否启用备份功能
        """
        self.backup_enabled = backup_enabled
        self.backup_dir = None
        self.test_files = []
        self.preserved_files = []
        self.deleted_files = []
        self.necessary_markers = ['# NECESSARY', '# KEEP', '# DO NOT DELETE']
        self.config_files = ['pytest.ini', 'conftest.py', 'tox.ini', 'setup.cfg']
        
    def scan_test_files(self, root_dir: str = '.') -> List[str]:
        """
        扫描项目中所有以"test_"开头的Python文件
        
        Args:
            root_dir: 根目录路径
            
        Returns:
            测试文件路径列表
        """
        print("=" * 60)
        print("步骤1: 扫描测试文件")
        print("=" * 60)
        
        test_files = []
        root_path = Path(root_dir).resolve()
        
        for file_path in root_path.rglob("test_*.py"):
            # 跳过备份目录中的文件
            if self.backup_dir and self.backup_dir in str(file_path):
                continue
                
            test_files.append(str(file_path))
            print(f"  找到测试文件: {file_path}")
        
        self.test_files = test_files
        print(f"\n总共找到 {len(test_files)} 个测试文件")
        
        return test_files
    
    def check_import_usage(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        检查文件是否被其他非测试文件导入
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否被导入, 导入该文件的文件列表)
        """
        file_name = Path(file_path).stem
        importing_files = []
        
        # 获取项目根目录
        project_root = Path(file_path).parent
        while project_root.parent != project_root.parent:
            project_root = project_root.parent
            if (project_root / 'requirements.txt').exists() or \
               (project_root / 'setup.py').exists() or \
               (project_root / 'pyproject.toml').exists():
                break
        
        # 搜索所有Python文件中的导入语句
        for py_file in project_root.rglob("*.py"):
            # 跳过测试文件和自身
            if py_file.name.startswith("test_") or str(py_file) == file_path:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否有导入该测试文件的语句
                patterns = [
                    rf'from\s+{file_name}\s+import',
                    rf'import\s+{file_name}',
                    rf'from\s+\.{file_name}\s+import',
                    rf'import\s+\.{file_name}'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        importing_files.append(str(py_file))
                        break
                        
            except (UnicodeDecodeError, IOError):
                continue
        
        return len(importing_files) > 0, importing_files
    
    def check_necessary_markers(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        检查文件中是否包含必要标记
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否包含标记, 找到的标记列表)
        """
        found_markers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for marker in self.necessary_markers:
                if marker in content:
                    found_markers.append(marker)
                    
        except (UnicodeDecodeError, IOError):
            pass
            
        return len(found_markers) > 0, found_markers
    
    def check_config_file(self, file_path: str) -> bool:
        """
        检查是否为配置文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为配置文件
        """
        file_name = Path(file_path).name
        return file_name in self.config_files
    
    def analyze_file_necessity(self, file_path: str) -> Dict:
        """
        分析文件是否必要
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果字典
        """
        result = {
            'path': file_path,
            'necessary': False,
            'reason': '',
            'details': {}
        }
        
        # 检查必要标记
        has_markers, markers = self.check_necessary_markers(file_path)
        if has_markers:
            result['necessary'] = True
            result['reason'] = '包含必要标记'
            result['details']['markers'] = markers
            return result
        
        # 检查是否为配置文件
        if self.check_config_file(file_path):
            result['necessary'] = True
            result['reason'] = '为配置文件'
            return result
        
        # 检查是否被其他文件导入
        is_imported, importing_files = self.check_import_usage(file_path)
        if is_imported:
            result['necessary'] = True
            result['reason'] = '被其他文件导入'
            result['details']['importing_files'] = importing_files
            return result
        
        # 检查是否包含工具函数（通过AST分析）
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # 检查是否有工具函数（非测试函数）
            has_utility_functions = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 如果函数名不以test_开头，可能是工具函数
                    if not node.name.startswith('test_'):
                        has_utility_functions = True
                        break
            
            if has_utility_functions:
                result['necessary'] = True
                result['reason'] = '包含工具函数'
                result['details']['has_utility_functions'] = True
                return result
                
        except (SyntaxError, UnicodeDecodeError, IOError):
            pass
        
        result['reason'] = '普通测试文件，可安全删除'
        return result
    
    def evaluate_files(self) -> List[Dict]:
        """
        评估所有测试文件的必要性
        
        Returns:
            评估结果列表
        """
        print("\n" + "=" * 60)
        print("步骤2: 评估文件必要性")
        print("=" * 60)
        
        evaluations = []
        
        for file_path in self.test_files:
            print(f"\n分析文件: {Path(file_path).name}")
            evaluation = self.analyze_file_necessity(file_path)
            evaluations.append(evaluation)
            
            status = "保留" if evaluation['necessary'] else "可删除"
            print(f"  状态: {status}")
            print(f"  原因: {evaluation['reason']}")
            
            if evaluation['details']:
                for key, value in evaluation['details'].items():
                    if key == 'markers':
                        print(f"  标记: {', '.join(value)}")
                    elif key == 'importing_files':
                        print(f"  被导入到: {', '.join(Path(f).name for f in value)}")
                    else:
                        print(f"  {key}: {value}")
        
        return evaluations
    
    def create_backup(self, files_to_delete: List[str]) -> bool:
        """
        创建备份
        
        Args:
            files_to_delete: 要删除的文件列表
            
        Returns:
            是否成功创建备份
        """
        if not self.backup_enabled or not files_to_delete:
            return True
            
        print("\n" + "=" * 60)
        print("步骤3: 创建备份")
        print("=" * 60)
        
        try:
            # 创建备份目录
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"test_files_backup_{timestamp}"
            self.backup_dir = Path(tempfile.gettempdir()) / backup_name
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"创建备份目录: {self.backup_dir}")
            
            # 复制文件到备份目录
            for file_path in files_to_delete:
                src_path = Path(file_path)
                dst_path = self.backup_dir / src_path.name
                
                # 保持相对目录结构
                rel_path = src_path.relative_to(Path.cwd())
                dst_dir = self.backup_dir / rel_path.parent
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst_path = dst_dir / src_path.name
                
                shutil.copy2(src_path, dst_path)
                print(f"  备份: {src_path.name}")
            
            print(f"\n备份完成，共备份 {len(files_to_delete)} 个文件")
            print(f"备份位置: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"备份失败: {e}")
            return False
    
    def delete_files(self, files_to_delete: List[str]) -> List[str]:
        """
        删除文件
        
        Args:
            files_to_delete: 要删除的文件列表
            
        Returns:
            成功删除的文件列表
        """
        print("\n" + "=" * 60)
        print("步骤4: 删除文件")
        print("=" * 60)
        
        deleted_files = []
        
        # 询问用户确认
        print(f"\n准备删除 {len(files_to_delete)} 个文件:")
        for file_path in files_to_delete:
            print(f"  - {Path(file_path).name}")
        
        confirm = input("\n确认删除这些文件吗? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("操作已取消")
            return deleted_files
        
        # 删除文件
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                print(f"  已删除: {Path(file_path).name}")
            except Exception as e:
                print(f"  删除失败 {Path(file_path).name}: {e}")
        
        if deleted_files:
            print(f"\n成功删除 {len(deleted_files)} 个文件")
        
        return deleted_files
    
    def generate_report(self, evaluations: List[Dict], deleted_files: List[str]) -> None:
        """
        生成操作报告
        
        Args:
            evaluations: 评估结果列表
            deleted_files: 已删除文件列表
        """
        print("\n" + "=" * 60)
        print("步骤5: 生成报告")
        print("=" * 60)
        
        # 统计信息
        total_files = len(evaluations)
        preserved_count = total_files - len(deleted_files)
        deleted_count = len(deleted_files)
        
        print(f"\n操作摘要:")
        print(f"  总文件数: {total_files}")
        print(f"  保留文件: {preserved_count}")
        print(f"  删除文件: {deleted_count}")
        
        if self.backup_dir:
            print(f"  备份位置: {self.backup_dir}")
        
        # 保留文件详情
        preserved_files = [e for e in evaluations if e['path'] not in deleted_files]
        if preserved_files:
            print(f"\n保留文件详情:")
            for evaluation in preserved_files:
                file_name = Path(evaluation['path']).name
                print(f"  - {file_name}: {evaluation['reason']}")
        
        # 删除文件详情
        if deleted_files:
            print(f"\n已删除文件:")
            for file_path in deleted_files:
                file_name = Path(file_path).name
                print(f"  - {file_name}")
        
        # 保存报告到文件
        report_file = f"test_cleanup_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("Python测试文件清理报告\n")
                f.write("=" * 40 + "\n")
                f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"操作摘要:\n")
                f.write(f"  总文件数: {total_files}\n")
                f.write(f"  保留文件: {preserved_count}\n")
                f.write(f"  删除文件: {deleted_count}\n\n")
                
                if preserved_files:
                    f.write("保留文件详情:\n")
                    for evaluation in preserved_files:
                        file_name = Path(evaluation['path']).name
                        f.write(f"  - {file_name}: {evaluation['reason']}\n")
                    f.write("\n")
                
                if deleted_files:
                    f.write("已删除文件:\n")
                    for file_path in deleted_files:
                        file_name = Path(file_path).name
                        f.write(f"  - {file_name}\n")
            
            print(f"\n详细报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"保存报告失败: {e}")
    
    def clean_test_files(self, root_dir: str = '.') -> None:
        """
        执行完整的清理流程
        
        Args:
            root_dir: 根目录路径
        """
        print("Python测试文件清理工具")
        print("=" * 60)
        print(f"开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 步骤1: 扫描测试文件
            test_files = self.scan_test_files(root_dir)
            if not test_files:
                print("\n没有找到测试文件，清理完成。")
                return
            
            # 步骤2: 评估文件必要性
            evaluations = self.evaluate_files()
            
            # 分类文件
            files_to_delete = []
            for evaluation in evaluations:
                if not evaluation['necessary']:
                    files_to_delete.append(evaluation['path'])
                    self.deleted_files.append(evaluation['path'])
                else:
                    self.preserved_files.append(evaluation['path'])
            
            if not files_to_delete:
                print("\n没有需要删除的文件，清理完成。")
                self.generate_report(evaluations, [])
                return
            
            # 步骤3: 创建备份
            backup_success = self.create_backup(files_to_delete)
            if self.backup_enabled and not backup_success:
                print("备份失败，是否继续删除?")
                confirm = input("继续执行删除操作? (y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("操作已取消")
                    return
            
            # 步骤4: 删除文件
            actually_deleted = self.delete_files(files_to_delete)
            
            # 步骤5: 生成报告
            self.generate_report(evaluations, actually_deleted)
            
        except KeyboardInterrupt:
            print("\n\n操作被用户中断")
        except Exception as e:
            print(f"\n清理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n结束时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Python测试文件清理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python clean_test_files.py                    # 清理当前目录
  python clean_test_files.py --no-backup        # 不创建备份
  python clean_test_files.py --root /path/to/project  # 清理指定目录
        """
    )
    
    parser.add_argument(
        '--root', '-r',
        default='.',
        help='项目根目录路径 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='禁用备份功能'
    )
    
    args = parser.parse_args()
    
    # 创建清理器
    backup_enabled = not args.no_backup
    cleaner = TestFileCleaner(backup_enabled=backup_enabled)
    
    # 执行清理
    cleaner.clean_test_files(args.root)


if __name__ == '__main__':
    main()
