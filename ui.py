import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import traceback

from word_manager import WordManager, WordType
from logger import logger

class JapaneseWordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("日语单词学习应用")
        self.root.geometry("1000x600")
        
        self.word_manager = WordManager()
        self.selected_word_ids = []  # 存储选中的单词ID
        self.current_word = None
        self.current_search_keyword = ""  # 当前搜索关键词
        self.review_words = []  # 复习模式下的单词
        self.is_review_mode = False  # 是否在复习模式
        self.is_dark_mode = False
        
        self.setup_ui()
        self.refresh_type_list()

    def toggle_dark_mode(self):
        """切换暗黑/明亮模式"""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.dark_mode_button.config(text="明亮模式")
            self.apply_dark_theme()
        else:
            self.dark_mode_button.config(text="暗黑模式")
            self.apply_light_theme()

    def apply_dark_theme(self):
        """应用暗黑主题"""
        bg_color = "#2b2b2b"
        fg_color = "#dcdcdc" # white-gray
        entry_bg = "#3c3f41"
        select_bg = "#4a6984"
        button_bg = "#555555"

        self.root.config(bg=bg_color)
        
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure('.', background=bg_color, foreground=fg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TLabelFrame', background=bg_color, foreground=fg_color)
        style.configure('TLabelFrame.Label', background=bg_color, foreground=fg_color)

        style.configure('TButton', background=button_bg, foreground=fg_color, borderwidth=1)
        style.map('TButton', background=[('active', '#6a6a6a')])
        
        style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color, insertcolor=fg_color)
        
        style.configure('Treeview', background=entry_bg, foreground=fg_color, fieldbackground=entry_bg)
        style.map('Treeview', background=[('selected', select_bg)])
        style.configure('Treeview.Heading', background=button_bg, foreground=fg_color, relief='flat')
        style.map('Treeview.Heading', background=[('active', '#6a6a6a')])

        style.configure('TScrollbar', troughcolor=entry_bg, background=button_bg)

        style.configure('TCombobox', fieldbackground=entry_bg, background=button_bg, foreground=fg_color)
        
        style.configure("TMenubutton", background=button_bg, foreground=fg_color)

        # Non-ttk widgets
        self.type_listbox.config(bg=entry_bg, fg=fg_color, selectbackground=select_bg, selectforeground='white',
                                 highlightbackground=bg_color, borderwidth=0)
        self.detail_text.config(bg=entry_bg, fg=fg_color, selectbackground=select_bg, selectforeground='white',
                                insertbackground=fg_color, borderwidth=0)

    def apply_light_theme(self):
        """应用明亮主题 (恢复默认)"""
        self.root.config(bg='SystemButtonFace')

        style = ttk.Style(self.root)
        try:
            style.theme_use('vista')
        except tk.TclError:
            style.theme_use('clam')
        
        self.type_listbox.config(bg='white', fg='black', selectbackground='#0078D7', selectforeground='white')
        self.detail_text.config(bg='white', fg='black', selectbackground='#0078D7', selectforeground='white', insertbackground='black')
        # Manually refresh the widgets that were not updating correctly
        self.refresh_type_list()
        selection = self.type_listbox.curselection()
        if selection:
            self.on_type_select(None)
    
    def setup_ui(self):
        """设置界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        # 左栏：类型选择
        self.setup_type_panel(main_frame)
        
        # 中栏：单词列表
        self.setup_word_panel(main_frame)
        
        # 右栏：单词详情
        self.setup_detail_panel(main_frame)

        # 暗黑模式按钮
        self.dark_mode_button = ttk.Button(self.root, text="暗黑模式", command=self.toggle_dark_mode)
        self.dark_mode_button.grid(row=1, column=0, sticky=tk.E, padx=10, pady=5)
    
    def setup_type_panel(self, parent):
        """设置左栏类型面板"""
        type_frame = ttk.LabelFrame(parent, text="类型", padding="5")
        type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 搜索框
        search_frame = ttk.Frame(type_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=12)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        self.search_entry.bind('<Return>', self.on_search)
        
        # 类型列表
        self.type_listbox = tk.Listbox(type_frame, width=15)
        self.type_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.type_listbox.bind('<<ListboxSelect>>', self.on_type_select)
        
        # 复习按钮框架
        review_button_frame = ttk.Frame(type_frame)
        review_button_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))

        self.review_menubutton = ttk.Menubutton(review_button_frame, text="复习")
        self.review_menubutton.pack(fill=tk.X)

        review_menu = tk.Menu(self.review_menubutton, tearoff=0)
        self.review_menubutton['menu'] = review_menu
        
        review_menu.add_command(label="随机复习", command=lambda: self.start_review_session(word_type=None))
        review_menu.add_separator()
        
        for word_type_enum in WordType:
            review_menu.add_command(
                label=f"{word_type_enum.value} 复习", 
                command=lambda wt=word_type_enum.value: self.start_review_session(word_type=wt)
            )

        self.end_review_button = ttk.Button(review_button_frame, text="结束复习", command=self.end_review_session)
        
        # 配置网格权重
        type_frame.columnconfigure(0, weight=1)
        type_frame.rowconfigure(1, weight=1)
    
    def setup_word_panel(self, parent):
        """设置中栏单词面板"""
        word_frame = ttk.LabelFrame(parent, text="单词列表", padding="5")
        word_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 单词列表（使用Treeview支持多选）
        columns = ('Japanese', 'Remembered')
        self.word_tree = ttk.Treeview(word_frame, columns=columns, show='tree headings', selectmode='extended')
        
        # 设置列标题
        self.word_tree.heading('#0', text='ID', anchor=tk.W)
        self.word_tree.heading('Japanese', text='日语', anchor=tk.W)
        self.word_tree.heading('Remembered', text='已记住', anchor=tk.CENTER)
        
        # 设置列宽
        self.word_tree.column('#0', width=0, stretch=False)  # 隐藏ID列
        self.word_tree.column('Japanese', width=150)
        self.word_tree.column('Remembered', width=80)
        
        self.word_tree.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.word_tree.bind('<<TreeviewSelect>>', self.on_word_select)
        
        # 滚动条
        word_scrollbar = ttk.Scrollbar(word_frame, orient=tk.VERTICAL, command=self.word_tree.yview)
        word_scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.word_tree.configure(yscrollcommand=word_scrollbar.set)
        
        # 按钮框架
        button_frame = ttk.Frame(word_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # 添加和删除按钮
        ttk.Button(button_frame, text="添加", command=self.add_word_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除", command=self.delete_selected_words).pack(side=tk.LEFT)
        
        # 配置网格权重
        word_frame.columnconfigure(0, weight=1)
        word_frame.rowconfigure(0, weight=1)
    
    def setup_detail_panel(self, parent):
        """设置右栏详情面板"""
        detail_frame = ttk.LabelFrame(parent, text="单词详情", padding="5")
        detail_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 详情显示区域
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        detail_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        # 记住按钮
        self.remember_button = ttk.Button(detail_frame, text="标记为已记住", command=self.toggle_remember)
        self.remember_button.grid(row=1, column=0, pady=(10, 0))
        self.remember_button.config(state=tk.DISABLED)
        
        # 配置网格权重
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
    
    def start_review_session(self, word_type=None):
        """开始复习会话"""
        self.review_words = self.word_manager.get_review_words(word_type=word_type)
        if not self.review_words:
            messagebox.showinfo("提示", "没有需要复习的单词。")
            return
        
        # 更新被选中复习的单词的 last_review_time
        today_iso = datetime.now().date().isoformat()
        for word in self.review_words:
            self.word_manager.update_word(word.id, last_review_time=today_iso)
            word.last_review_time = today_iso # 同时更新本地对象状态

        self.is_review_mode = True
        self.review_menubutton.pack_forget()
        self.end_review_button.pack(fill=tk.X)
        
        self.refresh_type_list()
        self.type_listbox.selection_set(0)
        self.on_type_select(None)

    def end_review_session(self):
        """结束复习会话"""
        self.is_review_mode = False
        self.review_words = []
        self.end_review_button.pack_forget()
        self.review_menubutton.pack(fill=tk.X)
        
        self.refresh_type_list()
        self.word_tree.delete(*self.word_tree.get_children())
        self.current_word = None
        self.update_detail_display()

    def refresh_type_list(self):
        """刷新类型列表"""
        current_selection_text = None
        selection_indices = self.type_listbox.curselection()
        if selection_indices:
            current_selection_text = self.type_listbox.get(selection_indices[0])

        self.type_listbox.delete(0, tk.END)
        
        list_items = []
        
        if self.is_review_mode:
            list_items.append(f"复习 ({len(self.review_words)})")

        if self.current_search_keyword:
            search_results = self.word_manager.search_words(self.current_search_keyword)
            search_count = len(search_results)
            list_items.append(f"搜索结果 ({search_count})")
        
        for word_type in WordType:
            count = len(self.word_manager.get_words_by_type(word_type.value))
            list_items.append(f"{word_type.value} ({count})")

        for item in list_items:
            self.type_listbox.insert(tk.END, item)

        if current_selection_text and current_selection_text in list_items:
            try:
                idx = list_items.index(current_selection_text)
                self.type_listbox.selection_set(idx)
                self.type_listbox.activate(idx)
            except ValueError:
                pass # Item no longer exists
    
    def on_search(self, event=None):
        """搜索事件处理"""
        keyword = self.search_entry.get().strip()
        self.current_search_keyword = keyword
        
        # 刷新类型列表（会显示搜索结果）
        self.refresh_type_list()
        
        # 如果有搜索关键词，自动显示搜索结果
        if keyword:
            self.refresh_word_list("搜索结果")
    
    def on_type_select(self, event):
        """类型选择事件"""
        selection = self.type_listbox.curselection()
        if not selection:
            return
        
        # 获取选中的类型
        selected_text = self.type_listbox.get(selection[0])
        
        if selected_text.startswith("复习"):
            self.refresh_word_list("复习")
        elif selected_text.startswith("搜索结果"):
            # 选中的是搜索结果
            self.refresh_word_list("搜索结果")
        else:
            # 选中的是普通类型
            word_type = selected_text.split(' ')[0]  # 提取类型名称（去掉计数）
            self.refresh_word_list(word_type)
    
    def refresh_word_list(self, word_type_or_search):
        """刷新单词列表"""
        # 清空当前列表
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 获取单词列表
        if word_type_or_search == "复习":
            words = self.review_words
        elif word_type_or_search == "搜索结果":
            words = self.word_manager.search_words(self.current_search_keyword)
        else:
            words = self.word_manager.get_words_by_type(word_type_or_search)
        
        # 添加单词到列表
        for word in words:
            remembered_text = "✓" if word.remembered else "✗"
            # 如果是搜索结果或复习，在单词后显示类型信息
            if word_type_or_search == "搜索结果" or word_type_or_search == "复习":
                display_text = f"{word.japanese} [{word.word_type}]"
            else:
                display_text = word.japanese
            self.word_tree.insert('', tk.END, text=word.id, values=(display_text, remembered_text))
    
    def on_word_select(self, event):
        """单词选择事件"""
        selection = self.word_tree.selection()
        if not selection:
            self.current_word = None
            self.update_detail_display()
            return
        
        # 获取第一个选中的单词（用于详情显示）
        item = selection[0]
        word_id = self.word_tree.item(item, 'text')
        self.current_word = self.word_manager.get_word_by_id(word_id)
        
        # 更新选中的单词ID列表
        self.selected_word_ids = [self.word_tree.item(item, 'text') for item in selection]
        
        # 更新详情显示
        self.update_detail_display()
    
    def update_detail_display(self):
        """更新详情显示"""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        if self.current_word:
            detail_info = f"日语单词：{self.current_word.japanese}\n\n"
            detail_info += f"词性：{self.current_word.word_type}\n\n"
            detail_info += f"解释：\n{self.current_word.explanation}\n\n"
            detail_info += f"状态：{'已记住' if self.current_word.remembered else '未记住'}\n\n"
            if self.current_word.last_review_time:
                detail_info += f"最后复习：{self.current_word.last_review_time}"
            
            self.detail_text.insert(1.0, detail_info)
            
            # 更新按钮状态和文本
            self.remember_button.config(state=tk.NORMAL)
            if self.current_word.remembered:
                self.remember_button.config(text="标记为未记住")
            else:
                self.remember_button.config(text="标记为已记住")
        else:
            self.detail_text.insert(1.0, "请选择一个单词查看详情")
            self.remember_button.config(state=tk.DISABLED)
        
        self.detail_text.config(state=tk.DISABLED)
    
    def toggle_remember(self):
        """切换记住状态"""
        if not self.current_word:
            return
        
        new_status = not self.current_word.remembered
        self.word_manager.update_word(
            self.current_word.id, 
            remembered=new_status
        )
        self.current_word.remembered = new_status
        
        # 更新显示
        self.update_detail_display()
        # 重新刷新单词列表以更新记住状态显示
        if self.is_review_mode:
            self.refresh_word_list("复习")
        elif self.current_search_keyword:
            self.refresh_word_list("搜索结果")
        else:
            selection = self.type_listbox.curselection()
            if selection:
                selected_text = self.type_listbox.get(selection[0])
                if not selected_text.startswith("搜索结果"):
                    word_type = selected_text.split(' ')[0]
                    self.refresh_word_list(word_type)
        self.refresh_type_list()
    
    def add_word_dialog(self):
        """添加单词对话框"""
        dialog = AddWordDialog(self.root, self.word_manager)
        if dialog.result:
            self.refresh_type_list()
            # 如果当前有搜索关键词，保持搜索结果显示
            if self.current_search_keyword:
                self.refresh_word_list("搜索结果")
            else:
                # 如果当前有选中的类型，刷新单词列表
                selection = self.type_listbox.curselection()
                if selection:
                    selected_text = self.type_listbox.get(selection[0])
                    if not selected_text.startswith("搜索结果"):
                        word_type = selected_text.split(' ')[0]
                        self.refresh_word_list(word_type)
    
    def delete_selected_words(self):
        """删除选中的单词"""
        if not self.selected_word_ids:
            messagebox.showwarning("警告", "请先选择要删除的单词")
            return
        
        count = len(self.selected_word_ids)
        if messagebox.askyesno("确认删除", f"确定要删除选中的 {count} 个单词吗？"):
            self.word_manager.delete_words(self.selected_word_ids)
            self.selected_word_ids = []
            self.current_word = None
            
            # 刷新界面
            self.refresh_type_list()
            # 如果当前有搜索关键词，保持搜索结果显示
            if self.current_search_keyword:
                self.refresh_word_list("搜索结果")
            else:
                selection = self.type_listbox.curselection()
                if selection:
                    selected_text = self.type_listbox.get(selection[0])
                    if not selected_text.startswith("搜索结果"):
                        word_type = selected_text.split(' ')[0]
                        self.refresh_word_list(word_type)
            self.update_detail_display()

class AddWordDialog:
    def __init__(self, parent, word_manager):
        self.word_manager = word_manager
        self.result = None
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加单词")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog_ui()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def setup_dialog_ui(self):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日语单词输入
        ttk.Label(main_frame, text="日语单词:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.japanese_entry = ttk.Entry(main_frame, width=30)
        self.japanese_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.japanese_entry.focus()
        
        # 词性选择
        ttk.Label(main_frame, text="词性:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.type_combo = ttk.Combobox(main_frame, width=27, state="readonly")
        self.type_combo['values'] = [word_type.value for word_type in WordType]
        self.type_combo.current(0)
        self.type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 解释输入
        ttk.Label(main_frame, text="解释:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.explanation_text = tk.Text(main_frame, width=30, height=8)
        self.explanation_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="添加", command=self.add_word).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.add_word())
    
    def add_word(self):
        """添加单词"""
        japanese = self.japanese_entry.get().strip()
        word_type = self.type_combo.get()
        explanation = self.explanation_text.get(1.0, tk.END).strip()
        
        if not japanese:
            messagebox.showwarning("警告", "请输入日语单词")
            return
        
        if not explanation:
            messagebox.showwarning("警告", "请输入解释内容")
            return
        
        # 添加单词
        word = self.word_manager.add_word(japanese, word_type, explanation)
        self.result = word
        self.dialog.destroy()

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"未捕获的异常:\n{error_message}")
    messagebox.showerror("未知错误", "发生了一个未知的错误。详情请查看 app.log 文件。")

def main():
    root = tk.Tk()
    root.report_callback_exception = global_exception_handler
    app = JapaneseWordApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 