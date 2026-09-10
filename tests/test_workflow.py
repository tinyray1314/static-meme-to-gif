"""Observable CLI behavior, using generated fixtures and isolated outputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, ImageDraw, ImageSequence

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        for i in range(12):
            im = Image.new('RGB', (100, 80), 'white')
            ImageDraw.Draw(im).rectangle((i * 4, 25, i * 4 + 15, 45), fill='black')
            im.save(self.work / f'{i:02}.png')
        self.data = dict(frames=[f'{i:02}.png' for i in range(12)], total_ms=2000)
        self.manifest = self.work / 'manifest.json'
        self.write_manifest()

    def write_manifest(self):
        self.manifest.write_text(json.dumps(self.data), encoding='utf-8')

    def run_script(self, script, *args, ok=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *map(str, args)],
                                capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def build(self, *extra, ok=True):
        return self.run_script('build_gif.py', '--manifest', self.manifest,
                               '--out', self.work / 'result', *extra, ok=ok)

    def test_timing_dimensions_loop_and_budget(self):
        self.build()
        report = json.loads((self.work / 'result/report.json').read_text())
        self.assertTrue(report['budget_met'])
        self.assertEqual(report['input_frames'], 12)
        for name, size in [('master.gif', (100, 80)), ('small.gif', (240, 240))]:
            with Image.open(self.work / 'result' / name) as im:
                self.assertEqual(im.size, size)
                self.assertEqual(im.n_frames, 12)
                self.assertEqual(im.info['loop'], 0)
                self.assertEqual(sum(f.info['duration'] for f in ImageSequence.Iterator(im)), 2000)

    def test_custom_timing_survives_gif_recompression(self):
        self.data['durations_ms'] = [200] * 8 + [100] * 4
        self.write_manifest()
        self.build()
        self.run_script('build_gif.py', '--gif', self.work / 'result/master.gif',
                        '--out', self.work / 'recompressed')
        with Image.open(self.work / 'recompressed/small.gif') as im:
            self.assertEqual([f.info['duration'] for f in ImageSequence.Iterator(im)],
                             self.data['durations_ms'])

    def test_invalid_timing_rejected(self):
        self.data['durations_ms'] = [100] * 12
        self.write_manifest()
        self.build(ok=False)
        self.assertFalse((self.work / 'result/master.gif').exists())

    def test_mismatched_dimensions_rejected(self):
        Image.new('RGB', (101, 80)).save(self.work / '00.png')
        self.build(ok=False)

    def test_budget_failure_is_explicit(self):
        self.build('--max-kb', 0.01)
        report = json.loads((self.work / 'result/report.json').read_text())
        self.assertFalse(report['budget_met'])
        self.assertEqual(len(report['palette_attempts']), 3)

    def test_no_overwrite(self):
        self.build()
        before = (self.work / 'result/master.gif').read_bytes()
        self.build(ok=False)
        self.assertEqual((self.work / 'result/master.gif').read_bytes(), before)

    def test_uniform_sheet_order_and_boundary_checks(self):
        sheet = Image.new('RGB', (40, 20))
        colors = ['red', 'green', 'blue', 'yellow']
        for i, color in enumerate(colors):
            sheet.paste(color, (i % 2 * 20, i // 2 * 10, i % 2 * 20 + 20, i // 2 * 10 + 10))
        source = self.work / 'sheet.png'
        sheet.save(source)
        self.run_script('split_sheet.py', '--image', source, '--columns', 2,
                        '--rows', 2, '--out', self.work / 'split')
        manifest = json.loads((self.work / 'split/manifest.json').read_text())
        self.assertEqual(len(manifest['frames']), 4)
        for i, name in enumerate(manifest['frames']):
            with Image.open(self.work / 'split' / name) as im:
                self.assertEqual(im.size, (20, 10))
                self.assertEqual(im.getpixel((0, 0)), Image.new('RGB', (1, 1), colors[i]).getpixel((0, 0)))
        self.run_script('split_sheet.py', '--image', source, '--columns', 3,
                        '--rows', 2, '--out', self.work / 'invalid', ok=False)
        self.assertFalse((self.work / 'invalid').exists())

    def test_transparency_flattened_to_requested_background(self):
        for i in range(12):
            im = Image.new('RGBA', (100, 80), (0, 0, 0, 0))
            ImageDraw.Draw(im).rectangle((i * 4, 25, i * 4 + 15, 45), fill=(0, 0, 0, 255))
            im.save(self.work / f'{i:02}.png')
        self.build('--background', '#FF0000')
        with Image.open(self.work / 'result/master.gif') as im:
            red, green, blue = im.convert('RGB').getpixel((99, 79))
            # Palette quantization may slightly shift colors; the alpha must
            # still be composited onto red, not black or default white.
            self.assertGreaterEqual(red, 250)
            self.assertLessEqual(max(green, blue), 5)


if __name__ == '__main__':
    unittest.main()
