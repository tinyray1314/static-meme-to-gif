# 测试案例 / Test cases

四个案例来自本技能首次实践测试：三张手绘文字表情和一张立体角色图。每组包含用户提供的原图、实际生成提示词、一张 4×3 动作网格、12 张独立帧、manifest、两个 GIF 和来源/检查记录。

| 案例 | 轻量 GIF | 大尺寸 GIF | 动作网格 | 轻量体积 |
| --- | --- | --- | --- | --- |
| 允许一切发生 | [240×240](allow-everything/small.gif) | [362×362](allow-everything/master.gif) | [12 格](allow-everything/sprite-sheet.png) | 104,429 bytes ≈ 102.0 KiB |
| 不服来战 | [240×240](bring-it-on/small.gif) | [362×362](bring-it-on/master.gif) | [12 格](bring-it-on/sprite-sheet.png) | 94,260 bytes ≈ 92.1 KiB |
| 方向比努力重要 | [240×240](direction-matters/small.gif) | [362×362](direction-matters/master.gif) | [12 格](direction-matters/sprite-sheet.png) | 95,988 bytes ≈ 93.7 KiB |
| 派对小怪兽 | [240×240](party-creature/small.gif) | [362×362](party-creature/master.gif) | [12 格](party-creature/sprite-sheet.png) | 302,540 bytes ≈ 295.4 KiB |

所有 GIF 均为 12 个编码帧、2000ms、无限循环。大尺寸指生成网格拆出的 362×362 单帧，不是原始输入图的尺寸。

## 文件与复现

```text
examples/<case>/
  source.png          原始输入图
  prompt.txt          当时发送给图像工具的提示词
  sprite-sheet.png    实际生成的 1448×1086 网格
  frames/01.png …     按从左到右、从上到下顺序拆出的 12 帧
  manifest.json       路径与总时长，可直接用于脚本
  master.gif          362×362
  small.gif           240×240
  report.json         编码后的检查数据
  provenance.json     来源、生成方式和验收边界
```

在仓库根目录安装依赖后运行，例如：

```bash
python scripts/build_gif.py --manifest examples/party-creature/manifest.json --out output/party-creature
```

也可先用 `scripts/split_sheet.py` 从网格重新拆帧。提示词中的 2048×1536 是期望尺寸；实际工具返回的是 1448×1086，应始终以输出实测为准。所有素材均采用白色/浅色不透明底。

## 已验证与尚未验证

- 已验证：四组文件能解码，尺寸、帧数、时长、无限循环和体积数据正确；从已保存帧重新合成时这些指标保持一致。
- 已检查：生成帧网格和 240 像素首帧，文字可读，主体保留。
- 未独立验证：连续播放的完整视觉验收、微信实际导入。
- 保留的问题：逐帧重绘带来轻微位置、线条或材质变化。挥手与出拳并非严格物理模拟，派对吹卷伸缩也有形状变化。不要把这些样例解释成模型一致性基准测试。

## English notes

These four cases include source images, the actual generation prompts, sheets, extracted frames, manifests, GIFs, and reports. The requested sheet size may differ from the actual result: all saved sheets are 1448×1086 and each cell is 362×362.

All GIFs contain 12 encoded frames, last 2000ms, and loop indefinitely. Encoding metrics and rebuilding from saved frames have been checked. Sheet inspection and first-frame inspection were performed; continuous playback and WeChat import were not independently verified. Minor redraw variations remain. See [ASSET_NOTICE.md](ASSET_NOTICE.md) for media rights information.
