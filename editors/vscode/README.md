# Oort for Visual Studio Code

Oort 语言的 VSCode 基础支持（P0）：TextMate 语法高亮、括号匹配、注释与自动闭合。

## 功能

- `.ort` 文件自动使用 Oort 语言模式（`source.oort`）。
- 关键字、控制流、声明、内建类型、字面量、容器与运算符高亮。
- `enum` / `class` 声明名作为类型实体着色；`match`、`=>` 与 `Unit` 高亮。
- 导入语句：`import` / `from` / `as` 统一使用 import 关键字 scope
  （`keyword.control.import.oort`）。
- 首行 `#lang oort-object` 作为方言指令单独着色。
- `def operator "+"` 中的运算符名单独着色。
- `#` 行注释、`{}` / `[]` / `()` 括号匹配与自动闭合。
- 基于花括号的基础缩进规则。
- `.ort` 文件图标：倾斜轨道 + 中心太阳 + 彗星，O 形轨道呼应 Oort 的首字母，
  不再使用 Lua 式蓝底月牙。通过 `contributes.languages[].icon` 提供，在文件
  图标主题没有 `.ort` 映射时作为语言默认图标显示。若当前主题是 `None` /
  `Minimal` 这类不带文件图标的主题，则不会显示；可切换到 Seti 或 Modern Icons。

## 本地开发

```bash
cd editors/vscode
code .
```

在 VSCode 中按 `F5`，会打开 Extension Development Host 并加载本插件。打开任意
`.ort` 文件即可看到高亮效果。

调试 scope：命令面板执行 `Developer: Inspect Editor Tokens and Scopes`，
把光标放到 token 上查看 TextMate scope。

## 打包与安装

需要 Node.js（仅用于打包，运行插件不需要）：

```bash
cd editors/vscode
npm install
npm run package
code --install-extension oort-lang-0.1.3.vsix
```

如果 `code` 不在 PATH 中，可以在 VSCode 里执行
`Extensions: Install from VSIX...` 选择生成的 `.vsix`。

重新打包并覆盖安装：

```bash
npm run install-local
```

安装后重载窗口（`Developer: Reload Window`）即可生效。

## 已知限制

这是纯 TextMate 高亮，不做语法/语义检查：

- 不报告语法错误、类型错误；
- 不提供跳转、补全、悬停、重命名；
- 跨行结构（长字符串、嵌套括号）依赖正则近似，极端写法可能着色不准。

语义能力属于后续 LSP 阶段。关键字与运算符列表需要与
`grammars/Oort.g4` 保持同步。

## 目录结构

```text
editors/vscode/
├── package.json                  # 插件清单与语言/语法注册
├── language-configuration.json   # 注释、括号、自动闭合、缩进
├── syntaxes/oort.tmLanguage.json # TextMate 语法
├── icons/                         # oort-light.svg / oort-dark.svg 文件图标
├── test/syntax.test.ort           # TextMate scope 测试
└── README.md
```
