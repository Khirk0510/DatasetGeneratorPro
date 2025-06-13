import pandas as pd
import re
from typing import Tuple, List

def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    CSVファイルの構造を検証
    
    Args:
        df: 検証対象のDataFrame
        
    Returns:
        Tuple[bool, str]: (検証結果, メッセージ)
    """
    required_columns = [
        'テーブル名（日本語）',
        'テーブル名（英語）', 
        'カラム名（日）',
        'カラム名（英）',
        '分析シナリオ',
        'TGDScript'
    ]
    
    missing_columns = []
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        return False, f"必要なカラムが不足しています: {', '.join(missing_columns)}"
    
    # データの存在確認
    if len(df) == 0:
        return False, "データが存在しません"
    
    # TGDScriptカラムの内容確認
    if df['TGDScript'].isna().all():
        return False, "TGDScriptカラムにデータが存在しません"
    
    return True, "OK"

def format_japanese_text(text: str) -> str:
    """
    日本語テキストのフォーマット
    
    Args:
        text: フォーマット対象のテキスト
        
    Returns:
        str: フォーマット後のテキスト
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # 余分な空白を除去
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 句読点の後のスペース調整
    text = re.sub(r'([。、！？])\s*', r'\1', text)
    
    return text

def extract_script_commands(script: str) -> List[str]:
    """
    TGDScriptからコマンドを抽出
    
    Args:
        script: TGDScript文字列
        
    Returns:
        List[str]: 抽出されたコマンドのリスト
    """
    if not isinstance(script, str):
        return []
    
    commands = []
    lines = script.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):  # コメント行を除外
            # コマンドの開始部分を抽出
            command_match = re.match(r'^([A-Z]+)', line)
            if command_match:
                commands.append(command_match.group(1))
    
    return commands

def validate_script_syntax(script: str) -> Tuple[bool, List[str]]:
    """
    TGDScriptの構文チェック
    
    Args:
        script: チェック対象のTGDScript
        
    Returns:
        Tuple[bool, List[str]]: (構文が正しいか, エラーメッセージのリスト)
    """
    if not isinstance(script, str) or not script.strip():
        return False, ["スクリプトが空です"]
    
    errors = []
    lines = script.strip().split('\n')
    
    valid_commands = ['OPEN', 'EXTRACT', 'SUMMARIZE', 'HISTOGRAM', 'DEVIATION', 'CLOSE']
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # コマンドの確認
        command_match = re.match(r'^([A-Z]+)', line)
        if not command_match:
            errors.append(f"行{i}: 有効なコマンドが見つかりません")
            continue
            
        command = command_match.group(1)
        if command not in valid_commands:
            errors.append(f"行{i}: 未知のコマンド '{command}'")
        
        # 引用符のバランスチェック
        quote_count = line.count('"')
        if quote_count % 2 != 0:
            errors.append(f"行{i}: 引用符のバランスが合いません")
        
        # OPEN文の構文チェック
        if command == 'OPEN':
            if not re.search(r'OPEN\s+"[^"]+"', line):
                errors.append(f"行{i}: OPEN文の構文が正しくありません")
        
        # EXTRACT文の構文チェック
        elif command == 'EXTRACT':
            if not re.search(r'EXTRACT.*TO\s+"[^"]+"', line):
                errors.append(f"行{i}: EXTRACT文にTO句がありません")
    
    return len(errors) == 0, errors

def clean_csv_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    CSVデータのクリーニング
    
    Args:
        df: クリーニング対象のDataFrame
        
    Returns:
        pd.DataFrame: クリーニング後のDataFrame
    """
    cleaned_df = df.copy()
    
    # 文字列カラムの前後空白を除去
    string_columns = cleaned_df.select_dtypes(include=['object']).columns
    for col in string_columns:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        # 'nan'文字列をNaNに変換
        cleaned_df[col] = cleaned_df[col].replace('nan', pd.NA)
    
    # 空行を除去
    cleaned_df = cleaned_df.dropna(how='all')
    
    return cleaned_df

def generate_file_name(base_name: str, extension: str = 'csv') -> str:
    """
    ファイル名を生成
    
    Args:
        base_name: ベースとなるファイル名
        extension: ファイル拡張子
        
    Returns:
        str: 生成されたファイル名
    """
    import datetime
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    clean_base = re.sub(r'[^\w\-_]', '_', base_name)
    
    return f"{clean_base}_{timestamp}.{extension}"

def calculate_similarity(text1: str, text2: str) -> float:
    """
    2つのテキストの類似度を計算（簡単な実装）
    
    Args:
        text1: 比較対象のテキスト1
        text2: 比較対象のテキスト2
        
    Returns:
        float: 類似度（0.0-1.0）
    """
    if not isinstance(text1, str) or not isinstance(text2, str):
        return 0.0
    
    if text1 == text2:
        return 1.0
    
    # 簡単な文字レベルの類似度計算
    set1 = set(text1)
    set2 = set(text2)
    
    if len(set1) == 0 and len(set2) == 0:
        return 1.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0

def analyze_script_patterns(scripts: List[str]) -> dict:
    """
    TGDScriptのパターンを分析
    
    Args:
        scripts: 分析対象のスクリプトリスト
        
    Returns:
        dict: 分析結果
    """
    analysis = {
        'total_scripts': len(scripts),
        'command_frequency': {},
        'average_length': 0,
        'unique_patterns': set()
    }
    
    total_length = 0
    
    for script in scripts:
        if not isinstance(script, str):
            continue
            
        total_length += len(script)
        commands = extract_script_commands(script)
        
        for command in commands:
            analysis['command_frequency'][command] = analysis['command_frequency'].get(command, 0) + 1
        
        # パターンの抽出（簡略化）
        pattern = ' -> '.join(commands)
        analysis['unique_patterns'].add(pattern)
    
    if len(scripts) > 0:
        analysis['average_length'] = total_length / len(scripts)
    
    analysis['unique_patterns'] = len(analysis['unique_patterns'])
    
    return analysis
