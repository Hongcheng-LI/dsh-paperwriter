# dsh-paperwriter

[Paperwriter](https://github.com/Hongcheng-LI/paperwriter) skill 的 DeepSeek Harness（DSH）插件封装。

Skill 的**真源（source of truth）**是 [`Hongcheng-LI/paperwriter`](https://github.com/Hongcheng-LI/paperwriter)（纯 skill 仓库）；本仓库只负责把它包装成可被 DSH 插件系统安装、可在 dsh-market 市场浏览的 bundle。`assets/paperwriter/` 是由 `scripts/sync_dsh.py` 从真源同步的快照（CI 强制校验不漂移）。

## 安装

### 方式一：dsh-market（推荐）

1. 打开 DSH Web 界面 → **Plugins** 页 → **Discover**（或 Settings 里的索引设置）
2. 添加本仓库的索引 URL：

   ```
   https://raw.githubusercontent.com/Hongcheng-LI/dsh-paperwriter/main/market-index.json
   ```

3. 搜索 **Paperwriter**，点击 Install。

### 方式二：git 直装

在启用了 Creator 模式的 DSH 会话中，用 `plugin_manager` 工具安装（target 填）：

```
git+https://github.com/Hongcheng-LI/dsh-paperwriter.git
```

（市场实际安装时会固定为 `git+<url>.git#<commit>`，同样可用。）

### 方式三：本地目录安装（开发）

```bash
git clone https://github.com/Hongcheng-LI/dsh-paperwriter.git
```

然后在 `plugin_manager` 的 `install_bundle` 里 target 填本地 clone 的绝对路径（link 安装，改代码后重启 DSH 生效）。

## 安装后怎么用

安装即注册 `paperwriter` skill，无需额外配置：

- **自动触发**：当任务涉及期刊论文写作（架构设计、初稿、返修、投稿信等）时，agent 会按 skill 的 `description` 自行调用；
- **点名触发**：对话中直接说「用 paperwriter 给我搭一个论文项目」。

skill 正文支持热重载；修改 `assets/paperwriter/SKILL.md` 的 description 等挂载期元数据后需重启 DSH。

## 维护流程（发新版本）

1. 在 `paperwriter` 仓库修改 skill，推送；
2. 本仓库：`python scripts/sync_dsh.py`（默认取同级目录 `../paperwriter` 检出，或 `--from <路径>`）；
3. `package.json` 里 bump `version`；
4. 更新 `market-index.json`：在 `plugins[0].versions` 前部新增/更新一条，`commit` 填本次代码提交的 SHA、`publishTimestamp` 填当前 unix 秒、`version` 与 package.json 一致（见下文两段式提交说明）；
5. 推送两个 commit：先推代码（拿到 SHA），再推索引。

> 两段式提交的原因：`market-index.json` 里的 git source 必须填写 40 位 commit SHA，而索引文件本身也在这个仓库里，首版索引只能指向「前一个」代码提交。

## 文件结构

```
dsh-paperwriter/
├── index.js                  # skill provider（注册 paperwriter skill 到 ctx.skills）
├── cordis.patch.yml          # bundle 清单：把 index.js 挂载为 cordis 插件
├── package.json              # dsh.bundle.patch 声明 + engines.dsh 兼容范围
├── locale/zh.json en.json    # 插件面板显示名/描述
├── icon.svg                  # 插件图标
├── assets/paperwriter/       # skill 快照（sync_dsh.py 从真源同步，勿手改）
├── market-index.json         # dsh-market 索引（format 1）
├── scripts/sync_dsh.py       # 同步/漂移检查（--check）
└── .github/workflows/validate.yml
```

## CI

每次 push / PR 自动执行：

- `sync_dsh.py --check`：确认 `assets/paperwriter/` 与 `Hongcheng-LI/paperwriter` main 分支逐字节一致（防漂移）；
- `node --check index.js`：语法校验。

## License

MIT（skill 内容本体见 [paperwriter](https://github.com/Hongcheng-LI/paperwriter) 仓库）。
