---
title: 2025年十月到十二月学习计划
description: ↖(^ω^)↗加油哇该死的小人儿
slug: 2025-q4-plan
date: 2025-10-01
image: cover.webp
categories:
    - 技术笔记
tags:
    - 学习计划
    - Python
    - 大模型
    - 项目实战
weight: 2
---

加油呀！！！！窝要加油变强💪

## 📅 十月：夯实基础

### 国庆假期（9.29 - 10.1）

**没离职海尔的时候**
- JSON格式处理
- SMTP邮件发送
- **设计模式学习**：
  - 多线程
  - 单例模式
  - 工厂模式
- **Python3内置库深入**：
  - MongoDB, urllib, pip
  - operator, math, requests, random
  - OpenAI, statistics, hashlib
  - pyecharts, sys, pickle, subprocess
  - queue, StringIO, logging
  - datetime, re, csv
  - threading, asyncio（没学完，都只是看了个皮毛🥲后面用到再补）

**假期期间**
- 个人网站搭建（就是现在这个博客！）

### 国庆假后

**核心学习内容**
- Python基础巩固
- OOP编程
- SQL数据库
- Pandas, NumPy, Matplotlib

**三个实战项目**
1. **学生成绩管理系统（面向过程版）**
2. **学生成绩管理系统（OOP重构版）**
3. **Kaggle数据集分析**
   - 选择基础数据集
   - 数据探索与清洗
   - 可视化分析

---

##  十一月：深入AI

### 主要学习内容
- 大模型课程深入学习
- RAG技术栈
- 检索算法
- LoRA微调
- 深度学习复习
- 机器学习复习
- 强化学习入门

### 实践要求
- 手写复现课程代码
- 理解每个算法原理
- 做好笔记和总结

### 多线程实践
在RAG项目中，尝试用多线程并行处理多个文件向量化

---

##  十二月：学习企业的开发方法和思想

### 学习内容
- Linux基础
- Docker基础
- Web编程基础
- Elasticsearch基础
- HTTP协议
- RESTful API（FastAPI）

### 核心项目：智能电影推荐系统

这个项目将串联所有技术点：

**技术栈应用**

1. **Web编程（FastAPI）** - 后端API服务
   - `GET /search?q=科幻`：接收搜索关键词，返回相关电影
   - `POST /recommend`：接收用户喜欢的电影ID，返回推荐列表

2. **Elasticsearch** - 搜索引擎
   - 导入电影数据（标题、简介、演员等）
   - 快速检索，替代慢速数据库查询
   - 支持全文搜索和相关性排序

3. **机器学习模型**
   - Pandas处理电影数据
   - Scikit-learn训练协同过滤推荐模型
   - FastAPI调用模型提供推荐服务

4. **Docker** - 容器化部署
   - 编写Dockerfile，定义环境依赖
   - docker-compose一键启动FastAPI + ES
   - 确保跨平台一致运行
   - 便于云服务器部署

**解决的实际问题**
> 问题：Docker、Web编程、ES这些在实践中怎么应用？  
> 答案：通过这个智能电影推荐系统，将所有技术点串联起来，形成完整的应用。

### 代码管理
将所有代码上传到GitHub并分类整理

### 多线程实践
在Web服务项目中，用线程池处理并发请求

---

## 一月：重构

### 核心任务
重构之前在幂律做的合同抽取系统

- 使用企业级开发规范
- 代码模块化、可维护
- 添加完整的文档
- Docker容器化部署

### 多线程实践
多线程并行处理多个合同文件，提升处理效率

---


**路漫漫其修远兮，吾将上下而求索。**


