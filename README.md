# 广州理工学院查寝脚本 🏫

**当前版本**：单线程版 

[⚠️ 免责声明](#免责声明)
本脚本仅供技术交流学习，请勿用于违法犯罪行为，否则后果自负。

---

## 📖 项目简介
本脚本为广州理工学院学生宿舍查寝流程自动化工具，通过模拟网络请求实现状态查询功能。项目主要用于技术学习交流，涵盖网络请求处理、数据解析等实践场景。

---

## 🛠 功能特性
- ✅ 自动化查寝

- 📌 *注：当前仅发布单线程版本，示例功能请以实际代码为准*

---

## 🚀 快速开始

### 环境要求
- ✅ Linux 服务器 已装Docker环境
- ✅ 推荐使用1panel简化部署

### 部署步骤
1. 安装 ddddocr api，[ddddocr-fastapi](https://github.com/sml2h3/ddddocr-fastapi)
2. 安装 青龙面板 [青龙面板](https://qinglong.online/guide/getting-started/installation-guide/docker)
3. 拉取本仓库
    ![image](/dcos/images/1.png)
4. 配置环境变量ACCOUNT_LIST（格式：学号;密码#），OCR_API（格式ip:port）
    ![image](/dcos/images/3.png)
    ![image](/dcos/images/4.png)
5. 安装依赖：
    - feapder
    - httpx
    - pyexecjs2
    - requests
    - retrying
    ![image](/dcos/images/2.png)    


