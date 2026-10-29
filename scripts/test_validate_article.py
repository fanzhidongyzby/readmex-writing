#!/usr/bin/env python3
"""Regression tests for article structure and actual PNG validation."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
import zlib

path = Path(__file__).with_name("validate_article.py")
spec = importlib.util.spec_from_file_location("article_validator", path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
_raw_validate = validator.validate


def evo_validate(article, manifest):
    return _raw_validate(article, manifest, profile="evomap", use_local=False)


validator.validate = evo_validate


def chunk(tag, data):
    return struct.pack(">I", len(data))+tag+data+struct.pack(">I", zlib.crc32(tag+data) & 0xffffffff)


def make_png(path, mode=0, transparent=False, colored=False):
    rows = []
    previous = bytes(32)
    for y in range(8):
        row = bytearray()
        for x in range(8):
            inside = 1 <= x <= 6 and 1 <= y <= 6
            color = (255, 0, 0) if colored and inside else (80, 80, 80) if inside else (255, 255, 255)
            row.extend((*color, 0 if transparent and x == y == 4 else 255))
        encoded = bytearray(32)
        for i in range(32):
            left = row[i-4] if i >= 4 else 0
            above = previous[i]
            upper_left = previous[i-4] if i >= 4 else 0
            if mode == 0:
                prediction = 0
            elif mode == 1:
                prediction = left
            elif mode == 2:
                prediction = above
            elif mode == 3:
                prediction = (left+above)//2
            else:
                p = left+above-upper_left
                a, b, c = abs(p-left), abs(p-above), abs(p-upper_left)
                prediction = left if a <= b and a <= c else above if b <= c else upper_left
            encoded[i] = (row[i]-prediction) & 255
        rows.append(bytes([mode])+encoded)
        previous = row
    data = b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(b"".join(rows)))+chunk(b"IEND", b"")
    path.write_bytes(data)


def make_cover_png(path, width=1200, height=511):
    rows = (b"\0"+b"\xff"*(width*4))*height
    data = b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(rows))+chunk(b"IEND", b"")
    path.write_bytes(data)


class ArticleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/"figures").mkdir()
        self.md = self.root/"article.md"
        self.manifest = self.root/"manifest.json"
        self.content = """# 文章标题

![封面](figures/封面.png)

这里介绍读者熟悉的行业背景和实际问题，解释为什么组织机制值得讨论，并说明接下来将从真实观察出发理解这个判断。

## 1. 问题驱动
### 1.1 机制

两个完整句子形成一个段落。这里说明对象与机制，而不是单句口号。[[1]](https://example.com/source)

![图 1：节点按依赖连接](figures/01-机制.png)

## 参考文献

1. 来源：https://example.com/source
"""
        self.md.write_text(self.content)
        self.data = {"figures": [
            {"title": "封面", "png": "figures/封面.png", "svg": "figures/封面.svg", "section": "cover"},
            {"number": 1, "title": "机制", "description": "节点按依赖连接", "png": "figures/01-机制.png", "svg": "figures/01-机制.svg", "section": "1.1"},
        ]}
        self.manifest.write_text(json.dumps(self.data, ensure_ascii=False))
        for index, image in enumerate(self.data["figures"]):
            if index == 0:
                make_cover_png(self.root/image["png"])
                width, height = 1200, 511
            else:
                make_png(self.root/image["png"])
                width, height = 8, 8
            (self.root/image["svg"]).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><title>metadata</title><rect width="{width}" height="{height}" fill="#FFFFFF"/><text x="1" y="4" fill="#000000">A</text></svg>')

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_article(self):
        result = validator.validate(self.md, self.manifest)
        self.assertTrue(result["passed"])
        self.assertEqual(result["figure_count"], 1)
        self.assertEqual(result["image_count"], 2)
        self.assertEqual(result["cover_size"], [1200, 511])
        self.assertIsNone(result["figures"][0]["number"])

    def test_equivalent_heading_units(self):
        self.assertEqual(validator.units("Agent Team 4.7 递归"), 5)

    def test_numbered_references_rejected(self):
        self.md.write_text(self.content.replace("## 参考文献", "## 2. 参考文献"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_long_heading_rejected(self):
        self.md.write_text(self.content.replace("### 1.1 机制", "### 1.1 这个章节标题非常长而且没有凝练"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_flat_directory_rejected(self):
        self.md.write_text(self.content.replace("### 1.1 机制", "## 2. 机制"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_cover_required(self):
        self.data["figures"][0]["section"] = "1.1"
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_page_furniture_rejected(self):
        p = self.root/self.data["figures"][0]["svg"]
        p.write_text(p.read_text().replace(">A<", ">EVOMAP / DOCUMENT FIGURE<"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_missing_source_asset_rejected(self):
        (self.root/self.data["figures"][1]["svg"]).unlink()
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_cover_number_rejected(self):
        self.data["figures"][0]["number"] = 1
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_numbered_cover_alt_rejected(self):
        self.md.write_text(self.content.replace("![封面]", "![图 1 封面]"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_wrong_cover_pixel_size_rejected(self):
        make_cover_png(self.root/self.data["figures"][0]["png"], width=2400, height=1022)
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_wrong_cover_svg_canvas_rejected(self):
        p = self.root/self.data["figures"][0]["svg"]
        p.write_text(p.read_text().replace('width="1200"', 'width="2400"'))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_explicit_other_cover_size(self):
        self.data["cover_size"] = [8, 8]
        self.manifest.write_text(json.dumps(self.data))
        make_png(self.root/self.data["figures"][0]["png"])
        p = self.root/self.data["figures"][0]["svg"]
        p.write_text(p.read_text().replace('width="1200"', 'width="8"').replace('height="511"', 'height="8"'))
        self.assertTrue(validator.validate(self.md, self.manifest)["passed"])

    def test_old_caption_format_rejected(self):
        self.md.write_text(self.content.replace("图 1：节点按依赖连接", "图 1 机制"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_body_numbering_starts_at_one(self):
        self.data["figures"][1]["number"] = 2
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_caption_inside_art_rejected(self):
        p = self.root/self.data["figures"][1]["svg"]
        p.write_text(p.read_text().replace(">A<", ">图 1：节点按依赖连接<"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_private_reference_rejected(self):
        self.data['private_reference_domains'] = ['example.feishu.cn']
        self.manifest.write_text(json.dumps(self.data))
        self.md.write_text(self.content.replace("https://example.com/source", "https://example.feishu.cn/docx/internal"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_citation_url_mismatch_rejected(self):
        self.md.write_text(self.content.replace("[[1]](https://example.com/source)", "[[1]](https://example.com/wrong)"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_uncited_reference_rejected(self):
        self.md.write_text(self.content.replace("[[1]](https://example.com/source)", ""))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_first_use_order_rejected(self):
        text = self.content.replace("[[1]](https://example.com/source)", "[[2]](https://example.com/other) [[1]](https://example.com/source)")
        self.md.write_text(text+"\n2. 另一来源：https://example.com/other\n")
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_single_bracket_wrong_url_rejected(self):
        self.md.write_text(self.content.replace("[[1]](https://example.com/source)", "[1](https://example.com/wrong)"))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_bold_intro_accepted(self):
        lines = self.content.splitlines()
        lines[4] = "**"+lines[4]+"**"
        self.md.write_text("\n".join(lines)+"\n")
        self.assertTrue(validator.validate(self.md, self.manifest)["passed"])

    def test_fenced_comment_ignored(self):
        self.md.write_text(self.content.replace("## 参考文献", "```python\n# a code comment\nx = 1\n```\n\n## 参考文献"))
        self.assertTrue(validator.validate(self.md, self.manifest)["passed"])

    def test_major_topic_coverage_allows_shared_figure(self):
        self.md.write_text(self.content.replace("## 参考文献", "### 1.2 边界\n\nA boundary of the same topic.\n\n## 参考文献"))
        self.assertTrue(validator.validate(self.md, self.manifest)["passed"])

    def test_explicit_leaf_coverage_requires_each(self):
        self.md.write_text(self.content.replace("## 参考文献", "### 1.2 边界\n\nA boundary of the same topic.\n\n## 参考文献"))
        self.data["required_figure_sections"] = ["1.1", "1.2"]
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaises(AssertionError): validator.validate(self.md, self.manifest)

    def test_custom_reference_heading_accepted(self):
        self.data["reference_heading"] = "参考资料"
        self.manifest.write_text(json.dumps(self.data))
        self.md.write_text(self.content.replace("## 参考文献", "## 参考资料"))
        self.assertTrue(validator.validate(self.md, self.manifest)["passed"])

    def test_generic_text_without_images_or_references(self):
        self.md.write_text('# 一个判断\n\n这是一段不含外部事实引用的原创观点。\n')
        self.manifest.write_text('{}')
        result = _raw_validate(self.md, self.manifest, profile='generic', use_local=False)
        self.assertEqual(result['image_count'], 0)
        self.assertEqual(result['reference_count'], 0)

    def test_generic_accepts_flat_headings(self):
        self.md.write_text(self.content.replace('### 1.1 机制', '## 2. 机制'))
        self.assertTrue(_raw_validate(self.md, self.manifest, profile='generic', use_local=False)['passed'])

    def test_generic_color_and_transparency_without_svg(self):
        make_png(self.root/self.data['figures'][1]['png'], transparent=True, colored=True)
        self.data['figures'][1].pop('svg')
        self.manifest.write_text(json.dumps(self.data))
        self.assertTrue(_raw_validate(self.md, self.manifest, profile='generic', use_local=False)['passed'])

    def test_nested_url_parentheses(self):
        self.md.write_text(self.content.replace('https://example.com/source', 'https://example.com/source_(topic)'))
        self.assertTrue(validator.validate(self.md, self.manifest)['passed'])

    def test_nested_image_label_brackets(self):
        self.data['figures'][1]['description'] = '节点 [A] 与 [B] 按依赖连接'
        self.manifest.write_text(json.dumps(self.data))
        self.md.write_text(self.content.replace('节点按依赖连接', '节点 [A] 与 [B] 按依赖连接'))
        self.assertTrue(validator.validate(self.md, self.manifest)['passed'])

    def test_generic_reference_domain_is_not_access_proof(self):
        self.md.write_text(self.content.replace('https://example.com/source', 'https://example.feishu.cn/docx/public-note'))
        result = _raw_validate(self.md, self.manifest, profile='generic', use_local=False)
        self.assertEqual(result['semantic_and_public_access_checks'], 'manual')

    def test_asset_paths_cannot_escape(self):
        for value in ('../private.png', str(self.root/'figures/封面.png')):
            with self.assertRaises(AssertionError): validator.local_asset(self.root, value)

    def test_external_svg_resources_rejected(self):
        p = self.root/'external.svg'
        p.write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.com/private.png"/></svg>')
        with self.assertRaises(AssertionError): validator.svg_check(p, 'demo', 'generic')

    def test_local_defaults_do_not_leak_into_explicit_generic_profile(self):
        local = self.root/'.local';local.mkdir()
        (local/'profile.json').write_text(json.dumps({'illustration_profile':'evomap','require_svg_sources':True,'max_heading_units':10}))
        with mock.patch.object(validator._profiles, 'SKILL_DIR', self.root):
            personal = validator.load_settings()
            public = validator.load_settings(profile='generic')
        self.assertEqual(personal['image_profile'], 'evomap')
        self.assertTrue(personal['require_svg_sources'])
        self.assertEqual(public['image_profile'], 'generic')
        self.assertFalse(public['require_svg_sources'])
        self.assertIsNone(public['max_heading_units'])

    def test_jpeg_metadata_dimensions(self):
        p = self.root/'frame.jpg'
        frame = bytes([8])+struct.pack('>HH',3,5)+bytes([1,1,17,0])
        p.write_bytes(b'\xff\xd8\xff\xc0'+struct.pack('>H',len(frame)+2)+frame+b'\xff\xd9')
        result = validator.image_info(p)
        self.assertEqual((result['width'],result['height']),(5,3))
        self.assertEqual(result['pixel_checks'],'metadata-only')

    def test_webp_metadata_dimensions(self):
        p = self.root/'frame.webp'
        body = b'\0'*4+(4).to_bytes(3,'little')+(2).to_bytes(3,'little')
        p.write_bytes(b'RIFF'+struct.pack('<I',22)+b'WEBPVP8X'+struct.pack('<I',10)+body)
        result = validator.image_info(p)
        self.assertEqual((result['width'],result['height']),(5,3))

    def test_symlink_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other)/'asset.png';make_png(outside)
            link = self.root/'escape.png';link.symlink_to(outside)
            with self.assertRaises(AssertionError): validator.local_asset(self.root,'escape.png')

    def test_svg_css_external_resource_rejected(self):
        p = self.root/'external-fill.svg'
        p.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="url(https://example.com/asset.svg)"/></svg>')
        with self.assertRaises(AssertionError): validator.svg_check(p,'demo','generic')

    def test_png_all_row_filters(self):
        for mode in range(5):
            with self.subTest(mode=mode):
                p = self.root/f"filter-{mode}.png"
                make_png(p, mode=mode)
                result = validator.png_pixels(p)
                self.assertEqual(result["minimum_alpha"], 255)
                self.assertEqual(result["colored_pixel_ratio"], 0)

    def test_transparent_png_rejected(self):
        p = self.root/"transparent.png"
        make_png(p, transparent=True)
        with self.assertRaises(AssertionError): validator.png_pixels(p)

    def test_excessive_color_rejected(self):
        p = self.root/"color.png"
        make_png(p, colored=True)
        with self.assertRaises(AssertionError): validator.png_pixels(p)

    def test_png_crc_checked(self):
        p = self.root/"crc.png"
        make_png(p)
        data = bytearray(p.read_bytes())
        data[20] ^= 1
        p.write_bytes(data)
        with self.assertRaises(AssertionError): validator.png_pixels(p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
