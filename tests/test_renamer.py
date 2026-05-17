#!/usr/bin/env python3
"""
FileRenamePro - 单元测试
"""

import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renamer import (
    FileRenamer, RenameRule, RenameMode,
    RenameOperation, BatchRenamer
)


class TestRenameRule(unittest.TestCase):
    """测试 RenameRule 类"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        rule = RenameRule(
            mode=RenameMode.SERIAL,
            prefix="test_",
            start_num=5
        )
        data = rule.to_dict()
        self.assertEqual(data['mode'], 'serial')
        self.assertEqual(data['prefix'], 'test_')
        self.assertEqual(data['start_num'], 5)
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'mode': 'replace',
            'find': 'old',
            'replace': 'new',
            'prefix': '',
            'suffix': '',
            'start_num': 1,
            'step': 1,
            'digits': 3,
            'date_format': '%Y%m%d',
            'hash_algo': 'md5',
            'hash_length': 8,
            'random_length': 8,
            'case_mode': 'lower',
            'insert_pos': 0,
            'insert_text': '',
            'ignore_ext': False,
        }
        rule = RenameRule.from_dict(data)
        self.assertEqual(rule.mode, RenameMode.REPLACE)
        self.assertEqual(rule.find, 'old')
        self.assertEqual(rule.replace, 'new')


class TestFileRenamer(unittest.TestCase):
    """测试 FileRenamer 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.renamer = FileRenamer()
        
        # 创建测试文件
        self.test_files = []
        for i in range(5):
            filepath = os.path.join(self.temp_dir, f"test_file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"content {i}")
            self.test_files.append(filepath)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_preview_replace(self):
        """测试替换模式预览"""
        rule = RenameRule(
            mode=RenameMode.REPLACE,
            find="test_",
            replace="doc_"
        )
        results = self.renamer.preview(self.test_files, rule)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0][1], "doc_file_0.txt")
        self.assertEqual(results[1][1], "doc_file_1.txt")
    
    def test_preview_serial(self):
        """测试序号模式预览"""
        rule = RenameRule(
            mode=RenameMode.SERIAL,
            prefix="img_",
            start_num=10,
            step=5,
            digits=4
        )
        results = self.renamer.preview(self.test_files, rule)
        
        self.assertEqual(results[0][1], "img_0010.txt")
        self.assertEqual(results[1][1], "img_0015.txt")
        self.assertEqual(results[2][1], "img_0020.txt")
    
    def test_preview_date(self):
        """测试日期模式预览"""
        from datetime import datetime
        
        rule = RenameRule(
            mode=RenameMode.DATE,
            prefix="backup_",
            date_format="%Y%m%d"
        )
        results = self.renamer.preview(self.test_files, rule)
        
        today = datetime.now().strftime("%Y%m%d")
        self.assertEqual(results[0][1], f"backup_{today}.txt")
    
    def test_preview_case_lower(self):
        """测试小写转换预览"""
        rule = RenameRule(
            mode=RenameMode.CASE,
            case_mode="lower"
        )
        results = self.renamer.preview(self.test_files, rule)
        
        self.assertEqual(results[0][1], "test_file_0.txt")
    
    def test_preview_case_upper(self):
        """测试大写转换预览"""
        rule = RenameRule(
            mode=RenameMode.CASE,
            case_mode="upper"
        )
        results = self.renamer.preview(self.test_files, rule)
        
        self.assertEqual(results[0][1], "TEST_FILE_0.TXT")
    
    def test_preview_insert(self):
        """测试插入模式预览"""
        rule = RenameRule(
            mode=RenameMode.INSERT,
            insert_pos=5,
            insert_text="NEW"
        )
        results = self.renamer.preview(self.test_files, rule)
        
        self.assertEqual(results[0][1], "test_NEWfile_0.txt")
    
    def test_rename_and_undo(self):
        """测试重命名和撤销"""
        rule = RenameRule(
            mode=RenameMode.REPLACE,
            find="test_",
            replace="doc_"
        )
        
        # 执行重命名
        operations = self.renamer.rename(self.test_files, rule)
        
        # 检查成功
        self.assertEqual(sum(1 for op in operations if op.success), 5)
        
        # 检查文件已重命名
        for i in range(5):
            old_path = os.path.join(self.temp_dir, f"test_file_{i}.txt")
            new_path = os.path.join(self.temp_dir, f"doc_file_{i}.txt")
            self.assertFalse(os.path.exists(old_path))
            self.assertTrue(os.path.exists(new_path))
        
        # 撤销
        undone = self.renamer.undo()
        self.assertEqual(len(undone), 5)
        
        # 检查文件已恢复
        for i in range(5):
            old_path = os.path.join(self.temp_dir, f"test_file_{i}.txt")
            self.assertTrue(os.path.exists(old_path))
    
    def test_dry_run(self):
        """测试预览模式（不实际执行）"""
        rule = RenameRule(
            mode=RenameMode.REPLACE,
            find="test_",
            replace="doc_"
        )
        
        # 预览模式
        operations = self.renamer.rename(self.test_files, rule, dry_run=True)
        
        # 检查文件未被修改
        for i in range(5):
            filepath = os.path.join(self.temp_dir, f"test_file_{i}.txt")
            self.assertTrue(os.path.exists(filepath))


class TestBatchRenamer(unittest.TestCase):
    """测试 BatchRenamer 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.batch = BatchRenamer()
        
        # 创建测试文件
        self.test_files = []
        for i in range(3):
            filepath = os.path.join(self.temp_dir, f"file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"content {i}")
            self.test_files.append(filepath)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_rule(self):
        """测试添加规则"""
        rule1 = RenameRule(mode=RenameMode.REPLACE, find="a", replace="b")
        rule2 = RenameRule(mode=RenameMode.CASE, case_mode="upper")
        
        self.batch.add_rule(rule1)
        self.batch.add_rule(rule2)
        
        self.assertEqual(len(self.batch.rules), 2)
    
    def test_clear_rules(self):
        """测试清空规则"""
        self.batch.add_rule(RenameRule(mode=RenameMode.REPLACE))
        self.batch.clear_rules()
        self.assertEqual(len(self.batch.rules), 0)


def run_tests():
    """运行测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestRenameRule))
    suite.addTests(loader.loadTestsFromTestCase(TestFileRenamer))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchRenamer))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
