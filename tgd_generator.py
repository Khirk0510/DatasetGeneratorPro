import pandas as pd
import random
import re
from typing import List, Dict, Tuple
import numpy as np

class TGDScriptGenerator:
    """TGDScriptの自動生成クラス"""
    
    def __init__(self, training_data: pd.DataFrame):
        """
        初期化
        
        Args:
            training_data: トレーニング用のDataFrame
        """
        self.training_data = training_data
        self.table_patterns = self._extract_table_patterns()
        self.column_patterns = self._extract_column_patterns()
        self.scenario_patterns = self._extract_scenario_patterns()
        self.script_patterns = self._extract_script_patterns()
        
    def _extract_table_patterns(self) -> Dict[str, List[str]]:
        """テーブル名のパターンを抽出"""
        patterns = {
            'japanese': [],
            'english': []
        }
        
        if 'テーブル名（日本語）' in self.training_data.columns:
            patterns['japanese'] = self.training_data['テーブル名（日本語）'].dropna().unique().tolist()
        
        if 'テーブル名（英語）' in self.training_data.columns:
            patterns['english'] = self.training_data['テーブル名（英語）'].dropna().unique().tolist()
            
        return patterns
    
    def _extract_column_patterns(self) -> Dict[str, List[str]]:
        """カラム名のパターンを抽出"""
        patterns = {
            'japanese': [],
            'english': []
        }
        
        # 日本語カラム名
        if 'カラム名（日）' in self.training_data.columns:
            for col_str in self.training_data['カラム名（日）'].dropna():
                if isinstance(col_str, str):
                    cols = [c.strip() for c in col_str.split(',')]
                    patterns['japanese'].extend(cols)
        
        # 英語カラム名
        if 'カラム名（英）' in self.training_data.columns:
            for col_str in self.training_data['カラム名（英）'].dropna():
                if isinstance(col_str, str):
                    cols = [c.strip() for c in col_str.split(',')]
                    patterns['english'].extend(cols)
        
        # 重複除去
        patterns['japanese'] = list(set(patterns['japanese']))
        patterns['english'] = list(set(patterns['english']))
        
        return patterns
    
    def _extract_scenario_patterns(self) -> List[str]:
        """分析シナリオのパターンを抽出"""
        scenarios = []
        if '分析シナリオ' in self.training_data.columns:
            scenarios = self.training_data['分析シナリオ'].dropna().unique().tolist()
        return scenarios
    
    def _extract_script_patterns(self) -> List[Dict]:
        """TGDScriptのパターンを抽出"""
        patterns = []
        
        if 'TGDScript' in self.training_data.columns:
            for _, row in self.training_data.iterrows():
                if pd.notna(row.get('TGDScript')):
                    pattern = {
                        'script': row['TGDScript'],
                        'table_jp': row.get('テーブル名（日本語）', ''),
                        'table_en': row.get('テーブル名（英語）', ''),
                        'columns_jp': row.get('カラム名（日）', ''),
                        'columns_en': row.get('カラム名（英）', ''),
                        'scenario': row.get('分析シナリオ', ''),
                        'procedure': row.get('具体的手続', '')
                    }
                    patterns.append(pattern)
        
        return patterns
    
    def _generate_table_variations(self, base_tables: List[str]) -> List[str]:
        """テーブル名のバリエーションを生成"""
        variations = base_tables.copy()
        
        # 既存テーブル名のバリエーション生成
        suffixes = ['マスタ', 'テーブル', 'データ', '情報', '管理', 'ファイル']
        prefixes = ['売上', '購買', '在庫', '顧客', '商品', '取引', '会計', '財務']
        
        for base in base_tables[:5]:  # 最初の5つのテーブルからバリエーション生成
            # サフィックス追加
            for suffix in suffixes:
                if suffix not in base:
                    variations.append(f"{base}{suffix}")
            
            # プレフィックス追加
            for prefix in prefixes:
                if prefix not in base:
                    variations.append(f"{prefix}{base}")
        
        return list(set(variations))
    
    def _generate_column_variations(self, base_columns: List[str]) -> List[str]:
        """カラム名のバリエーションを生成"""
        variations = base_columns.copy()
        
        # 日本語カラム名のバリエーション
        jp_suffixes = ['番号', 'コード', '名', '日', '金額', '区分', 'フラグ', '理由']
        jp_prefixes = ['入金', '売上', '購買', '在庫', '顧客', '商品', '取引']
        
        for base in base_columns[:10]:  # 最初の10個からバリエーション生成
            for suffix in jp_suffixes:
                if suffix not in base and len(base) > 2:
                    variations.append(f"{base[:-1] if base.endswith(suffix) else base}{suffix}")
            
            for prefix in jp_prefixes:
                if prefix not in base:
                    variations.append(f"{prefix}{base}")
        
        return list(set(variations))
    
    def _generate_scenario_variations(self, base_scenarios: List[str]) -> List[str]:
        """分析シナリオのバリエーションを生成"""
        variations = base_scenarios.copy()
        
        # シナリオのキーワード置換
        replacements = {
            '入金': ['売上', '購買', '支払', '請求'],
            'キャンセル': ['削除', '取消', '修正', '変更'],
            '理由': ['根拠', '原因', '要因', '背景'],
            '金額': ['数量', '単価', '合計', '残高'],
            '処理': ['作業', '操作', '実行', '登録']
        }
        
        for scenario in base_scenarios[:10]:
            for original, alternatives in replacements.items():
                if original in scenario:
                    for alt in alternatives:
                        new_scenario = scenario.replace(original, alt)
                        if new_scenario != scenario:
                            variations.append(new_scenario)
        
        return list(set(variations))
    
    def _generate_tgd_script(self, table_jp: str, table_en: str, columns_jp: str, 
                           columns_en: str, scenario: str, base_script: str) -> str:
        """TGDScriptを生成"""
        
        # ベーススクリプトから構造を抽出
        script_lines = base_script.strip().split('\n')
        
        # 新しいスクリプトを構築
        new_script_lines = []
        
        for line in script_lines:
            new_line = line
            
            # OPEN文の処理
            if 'OPEN' in line and '""' in line:
                # テーブル名を置換
                new_line = re.sub(r'""[^""]*""', f'"{table_jp}"', line, count=1)
            
            # EXTRACT文の処理
            elif 'EXTRACT' in line:
                # カラム名を動的に置換
                if '[' in line and ']' in line:
                    # 条件部分のカラム名を置換
                    jp_cols = [c.strip() for c in columns_jp.split(',') if c.strip()]
                    if jp_cols:
                        # ランダムにカラムを選択して条件を生成
                        selected_col = random.choice(jp_cols)
                        
                        # 条件の種類をランダムに選択
                        conditions = ['= ""1""', '<> """"', '> 0', '< 1000', 'IS NULL', 'IS NOT NULL']
                        condition = random.choice(conditions)
                        
                        # 条件部分を置換
                        new_line = re.sub(r'\[[^\]]+\]\s*[=<>!]+\s*"[^"]*"', 
                                        f'[{selected_col}] {condition}', line)
            
            # TO文の出力先パス調整
            if 'TO "' in line:
                # 出力先のパスを調整
                match = re.search(r'TO "([^"]*)"', line)
                if match:
                    original_path = match.group(1)
                    # パスの一部を動的に変更
                    path_parts = original_path.split('\\')
                    if len(path_parts) > 2:
                        # ファイル名部分を変更
                        filename = path_parts[-1]
                        new_filename = filename.replace('入金データ', table_jp)
                        path_parts[-1] = new_filename
                        new_path = '\\'.join(path_parts)
                        new_line = line.replace(original_path, new_path)
            
            new_script_lines.append(new_line)
        
        return '\n'.join(new_script_lines)
    
    def generate_scripts(self, num_scripts: int = 50, 
                        variation_level: str = "medium",
                        diversify_tables: bool = True,
                        diversify_columns: bool = True,
                        diversify_scenarios: bool = True) -> pd.DataFrame:
        """
        TGDScriptを生成
        
        Args:
            num_scripts: 生成するスクリプト数
            variation_level: バリエーションレベル（low/medium/high）
            diversify_tables: テーブル名を多様化するか
            diversify_columns: カラム名を多様化するか
            diversify_scenarios: シナリオを多様化するか
            
        Returns:
            生成されたデータのDataFrame
        """
        
        # バリエーションの生成
        tables_jp = self.table_patterns['japanese'].copy()
        tables_en = self.table_patterns['english'].copy()
        columns_jp = self.column_patterns['japanese'].copy()
        columns_en = self.column_patterns['english'].copy()
        scenarios = self.scenario_patterns.copy()
        
        if diversify_tables:
            tables_jp = self._generate_table_variations(tables_jp)
            # 英語テーブル名も簡単に生成
            en_mapping = {'データ': 'data', 'マスタ': 'master', 'テーブル': 'table', 
                         '情報': 'info', '管理': 'management'}
            for jp_table in tables_jp:
                en_table = jp_table
                for jp, en in en_mapping.items():
                    en_table = en_table.replace(jp, en)
                tables_en.append(en_table)
        
        if diversify_columns:
            columns_jp = self._generate_column_variations(columns_jp)
            # 英語カラム名も簡単に生成
            en_col_mapping = {'番号': 'Number', 'コード': 'Code', '名': 'Name', 
                            '日': 'Date', '金額': 'Amount', 'フラグ': 'Flag'}
            for jp_col in columns_jp:
                en_col = jp_col
                for jp, en in en_col_mapping.items():
                    en_col = en_col.replace(jp, en)
                columns_en.append(en_col)
        
        if diversify_scenarios:
            scenarios = self._generate_scenario_variations(scenarios)
        
        # 生成データのリスト
        generated_data = []
        
        for i in range(num_scripts):
            # ベースパターンをランダム選択
            base_pattern = random.choice(self.script_patterns)
            
            # テーブル名の選択
            table_jp = random.choice(tables_jp) if tables_jp else "データテーブル"
            table_en = random.choice(tables_en) if tables_en else "data_table"
            
            # カラム名の選択（複数をランダムに組み合わせ）
            num_columns = random.randint(3, 8)
            selected_columns_jp = random.sample(columns_jp, min(num_columns, len(columns_jp)))
            selected_columns_en = random.sample(columns_en, min(num_columns, len(columns_en)))
            
            columns_jp_str = ",".join(selected_columns_jp)
            columns_en_str = ",".join(selected_columns_en)
            
            # シナリオの選択
            scenario = random.choice(scenarios) if scenarios else "データの整合性を確認する"
            
            # 仮説の生成
            hypothesis = f"{table_jp}において、{random.choice(['データの不整合', '入力ミス', '処理の誤り', '承認漏れ', '重複データ'])}が存在する"
            
            # 説明文の生成
            explanation = f"{hypothesis}場合、不正処理、入力ミス、業務運用の逸脱、{table_jp}との不整合などの問題が発生する可能性がある"
            
            # 具体的手続の生成
            procedure_templates = [
                f"1. {table_jp}を開く\n2. 条件に該当するレコードを抽出\n3. 抽出結果を出力し、件数を集計して確認",
                f"1. {table_jp}を開く\n2. 特定の条件でデータをフィルタリング\n3. 結果を別ファイルに保存し、詳細確認",
                f"1. {table_jp}を開く\n2. データの整合性をチェック\n3. 不整合データを抽出して分析"
            ]
            procedure = random.choice(procedure_templates)
            
            # TGDScriptの生成
            tgd_script = self._generate_tgd_script(
                table_jp, table_en, columns_jp_str, columns_en_str, 
                scenario, base_pattern['script']
            )
            
            # データレコードの作成
            record = {
                'テーブル名（日本語）': table_jp,
                'テーブル名（英語）': table_en,
                'カラム名（日）': columns_jp_str,
                'カラム名（英）': columns_en_str,
                '仮説': hypothesis,
                '分析シナリオ': scenario,
                '説明文': explanation,
                '具体的手続': procedure,
                'TGDScript': tgd_script
            }
            
            generated_data.append(record)
        
        return pd.DataFrame(generated_data)
