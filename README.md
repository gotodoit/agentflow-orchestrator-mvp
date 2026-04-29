# AgentFlow Orchestrator MVP

这是一个可直接运行并可上传 GitHub 展示的最小可用项目，用于演示 **Agent 驱动工作流自动化** 的核心能力：

- 定义多步骤工作流
- 触发工作流执行（同步/异步）
- 查询执行状态、日志与结果上下文

## 1. 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后可访问：

- API 文档: `http://127.0.0.1:8000/docs`
- 健康检查: `http://127.0.0.1:8000/health`

## 3. 快速演示流程

### 创建工作流

```bash
curl -X POST "http://127.0.0.1:8000/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lead Follow-up Automation",
    "description": "自动跟进销售线索",
    "steps": [
      {
        "name": "写入线索信息",
        "action": "set_context",
        "params": { "values": { "user_name": "Alice", "product": "AI Copilot" } }
      },
      {
        "name": "生成通知文案",
        "action": "template",
        "params": {
          "template": "Hi {user_name}, welcome to {product}.",
          "output_key": "message"
        }
      },
      {
        "name": "发送模拟通知",
        "action": "notify_mock",
        "params": { "channel": "slack", "message": "{message}" }
      }
    ]
  }'
```

### 触发执行（同步）

把下面命令中的 `{workflow_id}` 替换为上一步返回的 id：

```bash
curl -X POST "http://127.0.0.1:8000/workflows/{workflow_id}/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_context": { "region": "APAC" },
    "run_in_background": false
  }'
```

### 查询执行记录

把下面命令中的 `{run_id}` 替换为上一步返回的 id：

```bash
curl "http://127.0.0.1:8000/runs/{run_id}"
```

## 4. 项目结构

```text
.
├── app
│   ├── engine.py      # 工作流步骤执行器
│   ├── main.py        # FastAPI 入口与路由
│   ├── models.py      # 数据模型定义
│   └── store.py       # 内存存储
├── tests
│   └── test_workflow_api.py
├── APPLICATION_TEXT.md
├── requirements.txt
└── README.md
```

## 5. 运行测试

```bash
pytest -q
```

## 6. 说明

- 当前版本使用内存存储，适合 Demo 和申请材料演示。
- 若要用于生产，可替换为数据库存储、消息队列和任务调度器（如 Celery）。

