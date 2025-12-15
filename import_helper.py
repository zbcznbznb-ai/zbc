import sqlite3
import os

# 配置：文件名和数据库名
SOURCE_FILE = "all_words_final.txt"
DB_FILE = "english_learning.db"

def run_import():
    # 1. 检查文件是否存在
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ 错误：找不到文件 {SOURCE_FILE}")
        print("请确保你把单词文本文件放在了同一个文件夹里！")
        return

    # 2. 读取单词并去重
    print(f"📖 正在读取 {SOURCE_FILE} ...")
    unique_words = set()
    words_to_insert = []
    
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        word = line.strip()
        if not word: continue # 跳过空行
        
        # 简单清洗：去掉非字母字符（可选），这里仅做去重
        # 逻辑：统一转小写判断是否存在，但存储时保留原样（优先保留小写格式）
        word_lower = word.lower()
        if word_lower not in unique_words:
            unique_words.add(word_lower)
            words_to_insert.append(word)

    print(f"✅ 读取完成！去重后共有 {len(words_to_insert)} 个新单词。")

    # 3. 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 检查数据库是否已存在 words 表
    try:
        cursor.execute("SELECT count(*) FROM words")
    except sqlite3.OperationalError:
        print("❌ 数据库未初始化。请先运行一次主程序(run.py)以生成数据库文件。")
        return

    # 4. 批量插入
    # 默认值设置：
    # meaning -> "[待补充]"
    # unit -> "导入词库"
    # difficulty -> 2
    
    print("🚀 正在写入数据库...")
    count = 0
    skipped = 0
    
    for word in words_to_insert:
        # 检查数据库里是不是已经有这个词了（防止和系统自带的词重复）
        cursor.execute("SELECT id FROM words WHERE lower(spelling) = ?", (word.lower(),))
        if cursor.fetchone():
            skipped += 1
            continue
            
        # 💡 高级技巧：如果你会安装 'googletrans' 或 'translate' 库，
        # 可以在这里调用 API 自动获取中文。但为了稳定性，这里默认使用占位符。
        meaning = "👉 点击编辑补充中文" 
        
        cursor.execute(
            "INSERT INTO words (spelling, meaning, part_of_speech, difficulty, unit) VALUES (?, ?, ?, ?, ?)",
            (word, meaning, "未知", 2, "📂 导入词库")
        )
        count += 1

    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"🎉 导入成功！")
    print(f"📥 新增单词: {count} 个")
    print(f"♻️ 跳过重复: {skipped} 个")
    print(f"现在请重新运行主程序，在【单词管理】或【学习中心】查看新单元'📂 导入词库'。")

if __name__ == "__main__":
    run_import()