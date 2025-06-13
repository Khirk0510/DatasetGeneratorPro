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
                try:
                    script_value = row['TGDScript']
                    if script_value is not None and str(script_value).strip() != '' and str(script_value) != 'nan':
                        script_str = str(script_value).strip()
                        if len(script_str) > 0:
                            pattern = {
                                'script': script_str,
                                'table_jp': str(row.get('テーブル名（日本語）', '')),
                                'table_en': str(row.get('テーブル名（英語）', '')),
                                'columns_jp': str(row.get('カラム名（日）', '')),
                                'columns_en': str(row.get('カラム名（英）', '')),
                                'scenario': str(row.get('分析シナリオ', '')),
                                'procedure': str(row.get('具体的手続', ''))
                            }
                            patterns.append(pattern)
                except Exception:
                    continue
        
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
        """TGDScriptを生成 - テーブル名とカラム名を正確に置換"""
        
        if not base_script or not isinstance(base_script, str):
            return ""
            
        # ベーススクリプトから構造を抽出
        script_lines = base_script.strip().split('\n')
        new_script_lines = []
        
        # カラム名のリストを準備
        jp_cols = [c.strip() for c in columns_jp.split(',') if c.strip()] if columns_jp else []
        
        for line in script_lines:
            new_line = line
            
            # OPEN文の処理 - テーブル名を置換
            if 'OPEN' in line and '""' in line:
                # 最初の""内のテーブル名を新しいテーブル名に置換
                new_line = re.sub(r'OPEN\s+""([^""]*)""', f'OPEN ""{table_jp}""', line)
            
            # EXTRACT文の処理 - カラム名を置換
            elif 'EXTRACT' in line:
                # [カラム名]の形式を見つけて置換
                column_matches = re.findall(r'\[([^\]]+)\]', line)
                if column_matches and jp_cols:
                    for i, match in enumerate(column_matches):
                        if i < len(jp_cols):
                            # 元のカラム名を新しいカラム名に置換
                            new_line = new_line.replace(f'[{match}]', f'[{jp_cols[i]}]')
                        else:
                            # カラムが足りない場合はランダムに選択
                            replacement_col = random.choice(jp_cols)
                            new_line = new_line.replace(f'[{match}]', f'[{replacement_col}]')
            
            # SUMMARIZE文の処理 - カラム名を置換
            elif 'SUMMARIZE' in line:
                column_matches = re.findall(r'\[([^\]]+)\]', line)
                if column_matches and jp_cols:
                    for i, match in enumerate(column_matches):
                        if i < len(jp_cols):
                            new_line = new_line.replace(f'[{match}]', f'[{jp_cols[i]}]')
                        else:
                            replacement_col = random.choice(jp_cols)
                            new_line = new_line.replace(f'[{match}]', f'[{replacement_col}]')
            
            # TO文の出力先パス調整 - テーブル名を含むパスを更新
            if 'TO "' in line:
                # パス内のテーブル名を置換
                match = re.search(r'TO "([^"]*)"', line)
                if match:
                    original_path = match.group(1)
                    # パス内の既存のテーブル名を新しいテーブル名に置換
                    new_path = original_path
                    # 一般的なテーブル名パターンを置換
                    common_table_names = ['入金データ', '売上データ', '購買データ', '在庫データ', '顧客データ']
                    for common_name in common_table_names:
                        if common_name in new_path:
                            new_path = new_path.replace(common_name, table_jp)
                            break
                    
                    # パスが変更された場合のみ置換
                    if new_path != original_path:
                        new_line = line.replace(original_path, new_path)
            
            new_script_lines.append(new_line)
        
        return '\n'.join(new_script_lines)
    
    def generate_scripts(self, num_scripts: int = 50, 
                        variation_level: str = "medium",
                        diversify_tables: bool = True,
                        diversify_columns: bool = True,
                        diversify_scenarios: bool = True) -> pd.DataFrame:
        """
        TGDScriptを生成 - 既存データを基に新しいTGDScriptのみ生成
        
        Args:
            num_scripts: 生成するスクリプト数
            variation_level: バリエーションレベル（low/medium/high）
            diversify_tables: テーブル名を多様化するか
            diversify_columns: カラム名を多様化するか
            diversify_scenarios: シナリオを多様化するか
            
        Returns:
            生成されたデータのDataFrame
        """
        
        # 元のデータをコピー
        original_data = self.training_data.copy()
        generated_rows = []
        
        # 指定された数だけデータを生成
        for i in range(num_scripts):
            # 既存データからランダムに1行を選択
            base_row = original_data.sample(n=1).iloc[0].copy()
            
            # 基本情報を取得
            table_jp = base_row.get('テーブル名（日本語）', '')
            table_en = base_row.get('テーブル名（英語）', '')
            columns_jp = base_row.get('カラム名（日）', '')
            columns_en = base_row.get('カラム名（英）', '')
            scenario = base_row.get('分析シナリオ', '')
            procedure = base_row.get('具体的手続', '')
            original_script = base_row.get('TGDScript', '')
            
            # バリエーションを生成する場合
            if diversify_tables and random.random() < 0.3:  # 30%の確率でテーブル名を変更
                variations = self._generate_table_variations([table_jp])
                if len(variations) > 1:
                    table_jp = random.choice([t for t in variations if t != table_jp])
                    # 英語名も調整
                    en_mapping = {'データ': 'data', 'マスタ': 'master', 'テーブル': 'table', 
                                 '情報': 'info', '管理': 'management'}
                    table_en = table_jp
                    for jp, en in en_mapping.items():
                        table_en = table_en.replace(jp, en)
            
            if diversify_columns and random.random() < 0.4:  # 40%の確率でカラム名を変更
                jp_cols = [c.strip() for c in columns_jp.split(',') if c.strip()]
                if jp_cols:
                    variations = self._generate_column_variations(jp_cols)
                    new_cols = random.sample(variations, min(len(jp_cols), len(variations)))
                    columns_jp = ','.join(new_cols)
                    
                    # 英語カラム名も調整
                    en_col_mapping = {'番号': 'Number', 'コード': 'Code', '名': 'Name', 
                                    '日': 'Date', '金額': 'Amount', 'フラグ': 'Flag'}
                    en_cols = []
                    for jp_col in new_cols:
                        en_col = jp_col
                        for jp, en in en_col_mapping.items():
                            en_col = en_col.replace(jp, en)
                        en_cols.append(en_col)
                    columns_en = ','.join(en_cols)
            
            # TGDScriptを生成（テーブル名とカラム名を置換）
            new_script = self._generate_tgd_script(
                table_jp, table_en, columns_jp, columns_en, 
                scenario, original_script
            )
            
            # 新しい行を作成（既存の行をベースに、TGDScriptのみ更新）
            new_row = base_row.copy()
            new_row['テーブル名（日本語）'] = table_jp
            new_row['テーブル名（英語）'] = table_en
            new_row['カラム名（日）'] = columns_jp
            new_row['カラム名（英）'] = columns_en
            new_row['TGDScript'] = new_script
            
            generated_rows.append(new_row)
        
        return pd.DataFrame(generated_rows)
