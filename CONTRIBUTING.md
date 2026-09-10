# Contributing

欢迎提交修复、流程改进或测试案例。请先阅读 [README](README.md) 中的边界说明。

## 报告问题

请提供 Python/Pillow 版本、运行命令、错误输出及最小可复现的帧或 GIF。动作质量问题请说明希望发生的动作、实际变化，以及出问题的具体帧。不要提交密钥、个人本地路径、私有聊天截图或无权公开的素材。

## 修改代码

保持编码与动作生成分离。提交前运行：

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

改变时长、压缩或拆帧逻辑时，增加相应行为测试。不要只测试实现细节。输出应继续保留真实检查状态，不能把文件可解码当成视觉验收通过。

## 新增案例

使用 `examples/<english-slug>/`，提供可公开分享的原图、生成提示词、顺序帧、manifest、GIF、report 和来源/授权说明。注明使用的工具、已知模型版本（未知则写未知）、实际检查方式及残留问题。不要移除失败现象来暗示未经验证的质量保证。

Code contributions use the repository's MIT license. For media contributions, state the source and permission to share it; do not assume the code license applies to artwork. Include a minimal reproduction, expected behavior, actual behavior, and relevant Python/Pillow versions for bug reports.
