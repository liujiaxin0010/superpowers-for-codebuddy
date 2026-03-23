# Windows 路径处理

本文件只在 Windows 环境、且路径包含空格时读取。

## 禁止写法

以下写法在带空格路径里容易失败：

```bash
cmd.exe /c "cd \"d:\\AI Agent\\test\\disk-configurator\" && python create_xlsx.py"
```

## 推荐写法

方式一：直接执行完整脚本路径

```bash
python "d:/AI Agent/test/disk-configurator/create_xlsx.py"
```

方式二：先切目录，再执行脚本

```bash
cd "d:/AI Agent/test/disk-configurator"
python create_xlsx.py
```

## 路径规则

1. 路径有空格时必须整体加引号
2. 优先使用正斜杠或 `pathlib.Path`
3. 不要在 `cmd.exe` 嵌套引号里赌运气
