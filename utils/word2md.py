import os


def get_file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):  # 获取当前文件夹的信息
        # print(root)
        # print(dirs)
        # print(files)
        for file in files:                       # 扫描所有文件
            if os.path.splitext(file)[1] == ".docx":# 提取出所有后缀名为md的文件
                # print(root)
                os.chdir(root)

                print("转换开始：" + "pandoc " + file + " -o " + os.path.splitext(file)[0] + ".md")
                # 使用os.system调用pandoc进行格式转化
                os.system("pandoc " + file + " -o " + os.path.splitext(file)[0] + ".md")
                print("转换完成...")


if __name__ == "__main__":
    get_file_name(r"C:\Users\user\WORK\Projects\local_llm_usage\org-files\各中心反馈")  # 修改文件路径