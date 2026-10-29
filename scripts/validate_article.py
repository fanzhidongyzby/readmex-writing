#!/usr/bin/env python3
"""Check Markdown structure, references and local assets, with optional EvoMap rules."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import zlib

_module_spec = importlib.util.spec_from_file_location('writing_profile', Path(__file__).with_name('profile_utils.py'))
_profiles = importlib.util.module_from_spec(_module_spec)
_module_spec.loader.exec_module(_profiles)
load_settings = _profiles.load_settings


def units(text):
    return len(re.findall(r'[一-鿿]|[A-Za-z]+(?:-[A-Za-z]+)*|\d+(?:\.\d+)*', text))


def png_pixels(path, enforce_style=True):
    data = Path(path).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'Not a PNG'
    offset, compressed, header = 8, bytearray(), None
    ended = False
    while offset < len(data):
        assert offset+12 <= len(data), 'Truncated PNG chunk'
        length = struct.unpack_from('>I', data, offset)[0]
        assert offset+length+12 <= len(data), 'Truncated PNG chunk'
        tag = data[offset+4:offset+8]
        chunk = data[offset+8:offset+8+length]
        assert zlib.crc32(tag+chunk) & 0xffffffff == struct.unpack_from('>I', data, offset+8+length)[0], 'PNG CRC mismatch'
        if tag == b'IHDR': header = struct.unpack('>IIBBBBB', chunk)
        elif tag == b'IDAT': compressed.extend(chunk)
        elif tag == b'IEND': ended = True; break
        offset += length+12
    assert header is not None and ended, 'PNG header or end missing'
    width, height, depth, kind, compression, filtering, interlace = header
    assert 0 < width*height <= 50_000_000, 'PNG dimensions outside validation limit'
    digest = hashlib.sha256(data).hexdigest()
    supported = depth == 8 and kind in (2,6) and compression == filtering == interlace == 0
    if not supported:
        assert not enforce_style, 'EvoMap pixel checks need non-interlaced RGB/RGBA 8-bit PNG'
        return {'width':width,'height':height,'sha256':digest,'format':'png','pixel_checks':'metadata-only'}
    channels = 3 if kind == 2 else 4
    stride = width*channels
    expected = height*(stride+1)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(bytes(compressed), expected+1)
    assert len(raw) == expected and decoder.eof, 'Invalid PNG image data'
    previous = bytearray(stride)
    minimum_alpha, colored, white_corners = 255, 0, True
    position = 0
    for y in range(height):
        mode = raw[position]
        row = bytearray(raw[position+1:position+1+stride])
        position += stride+1
        assert mode <= 4, 'Unknown PNG row filter'
        if mode:
            for i in range(stride):
                left = row[i-channels] if i >= channels else 0
                above = previous[i]
                upper_left = previous[i-channels] if i >= channels else 0
                if mode == 1: predictor = left
                elif mode == 2: predictor = above
                elif mode == 3: predictor = (left+above)//2
                else:
                    p = left+above-upper_left
                    a,b,c = abs(p-left),abs(p-above),abs(p-upper_left)
                    predictor = left if a <= b and a <= c else above if b <= c else upper_left
                row[i] = (row[i]+predictor) & 255
        for i in range(0,stride,channels):
            red,green,blue = row[i],row[i+1],row[i+2]
            if channels == 4: minimum_alpha = min(minimum_alpha,row[i+3])
            if max(red,green,blue)-min(red,green,blue) > 8: colored += 1
        if y in (0,height-1):
            for x in (0,width-1):
                start = x*channels
                white_corners &= row[start:start+3] == b'\xff\xff\xff' and (channels == 3 or row[start+3] == 255)
        previous = row
    ratio = colored/(width*height)
    if enforce_style:
        assert minimum_alpha == 255, 'PNG contains transparent pixels'
        assert white_corners, 'PNG canvas corners are not white'
        assert ratio < .10, 'Colored area must be below 10%'
    return {'width':width,'height':height,'minimum_alpha':minimum_alpha,'white_corners':white_corners,
            'colored_pixel_ratio':ratio,'sha256':digest,'format':'png','pixel_checks':'decoded'}


def image_info(path, enforce_style=False):
    data = Path(path).read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return png_pixels(path,enforce_style)
    assert not enforce_style, 'EvoMap authored assets must be PNG'
    dimensions = None
    if data.startswith(b'\xff\xd8'):
        offset = 2
        while offset+4 <= len(data):
            while offset < len(data) and data[offset] == 255: offset += 1
            if offset >= len(data): break
            marker = data[offset];offset += 1
            if marker in (0xd8,0xd9) or 0xd0 <= marker <= 0xd7: continue
            length = struct.unpack_from('>H',data,offset)[0]
            assert length >= 2 and offset+length <= len(data), 'Truncated JPEG'
            if marker in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):
                height,width = struct.unpack_from('>HH',data,offset+3)
                dimensions = (width,height);break
            if marker == 0xda: break
            offset += length
        kind = 'jpeg'
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        tag = data[12:16]
        if tag == b'VP8X' and len(data) >= 30:
            dimensions = (1+int.from_bytes(data[24:27],'little'),1+int.from_bytes(data[27:30],'little'))
        elif tag == b'VP8L' and len(data) >= 25 and data[20] == 47:
            bits = int.from_bytes(data[21:25],'little');dimensions = ((bits & 0x3fff)+1,((bits >> 14)&0x3fff)+1)
        elif tag == b'VP8 ' and len(data) >= 30 and data[23:26] == b'\x9d\x01\x2a':
            width,height = struct.unpack_from('<HH',data,26);dimensions = (width&0x3fff,height&0x3fff)
        kind = 'webp'
    else: raise AssertionError('Use PNG, JPEG or WebP local assets')
    assert dimensions and 0 < dimensions[0]*dimensions[1] <= 50_000_000, 'Invalid image dimensions'
    return {'width':dimensions[0],'height':dimensions[1],'sha256':hashlib.sha256(data).hexdigest(),
            'format':kind,'pixel_checks':'metadata-only'}


def luminance(color):
    values = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))


def svg_check(path,title,profile='evomap'):
    root = ET.parse(path).getroot()
    namespace = '{http://www.w3.org/2000/svg}'
    assert root.tag == namespace+'svg', 'Not an SVG'
    for node in root.iter():
        assert node.tag not in (namespace+'script',namespace+'foreignObject',namespace+'style'), 'Active or externally styled SVG content is not allowed'
        for key,value in node.attrib.items():
            attribute = key.rsplit('}',1)[-1].lower()
            assert not attribute.startswith('on'), 'SVG event handlers are not allowed'
            if attribute == 'href': assert value.startswith('#'), 'SVG must not load external resources'
            if attribute == 'style':
                assert '@import' not in value.lower(), 'SVG styles must not import resources'
            for target in re.findall(r'url\(([^)]+)\)', value, re.I):
                assert target.strip(' \"\'').startswith('#'), 'SVG attributes must not load external resources'
    result = {'svg_self_contained':True}
    if profile != 'evomap': return result
    background = root.find(namespace+'rect')
    assert background is not None and background.get('fill','').upper() == '#FFFFFF', 'SVG needs full white background'
    assert float(background.get('width')) == float(root.get('width'))
    assert float(background.get('height')) == float(root.get('height'))
    minimum = 21.0
    for node in root.findall('.//'+namespace+'text'):
        text = ''.join(node.itertext()).strip()
        assert text != title, 'Remove the visible figure title'
        assert not re.search(r'EVOMAP\s*/|FIGURE\s*\d|图\s+\d+[：:]|DOCUMENT FIGURE|WHITE CANVAS|原创概念插图|概念示意|并非原始通信|仅展示当前文章',text,re.I), 'Remove page furniture or explanation'
        fill = node.get('fill','').upper()
        assert fill in ('#000000','#53565A'), 'Use black/dark gray text'
        for surface in ('#FFFFFF','#F7F7F6','#E9F2F4','#FFD880'):
            a,b = sorted((luminance(fill),luminance(surface)))
            contrast = (b+.05)/(a+.05)
            assert contrast >= 4.5, 'Text contrast below 4.5:1'
            minimum = min(minimum,contrast)
    return dict(result,minimum_text_contrast=minimum,no_page_furniture=True)


def mask_fenced_code(text):
    lines,fence = [],None
    for line in text.splitlines():
        if fence:
            if re.fullmatch(r' {0,3}'+re.escape(fence[0])+'{'+str(fence[1])+r',}\s*',line): fence = None
            lines.append('')
        else:
            match = re.match(r' {0,3}(`{3,}|~{3,})',line)
            if match: fence=(match[1][0],len(match[1]));lines.append('')
            else: lines.append(line)
    return '\n'.join(lines)


def markdown_links(text):
    """Read nested labels and balanced target parentheses, without executing Markdown."""
    results=[];index=0
    while index < len(text):
        if text[index]=='\\': index += 2;continue
        image = text[index:index+2]=='!['
        start = index+1 if image else index
        if text[start:start+1]!='[': index += 1;continue
        cursor=start+1;depth=1
        while cursor<len(text) and depth:
            if text[cursor]=='\\': cursor+=2;continue
            if text[cursor]=='[': depth+=1
            elif text[cursor]==']': depth-=1
            cursor+=1
        if depth or text[cursor:cursor+1]!='(': index+=1;continue
        end=cursor+1;depth=1
        while end<len(text) and depth:
            if text[end]=='\\': end+=2;continue
            if text[end]=='(': depth+=1
            elif text[end]==')': depth-=1
            end+=1
        if depth: index+=1;continue
        target=text[cursor+1:end-1].strip()
        if target.startswith('<'):
            close=target.find('>');target=target[1:close] if close>=0 else target
        else: target=target.split()[0] if target else ''
        target=re.sub(r'\\([\\()\[\] ])',r'\1',target)
        results.append({'image':image,'label':text[start+1:cursor-1],'target':target,'start':index,'end':end})
        index=end
    return results


def local_asset(base,value):
    path=Path(value)
    assert not path.is_absolute() and '..' not in path.parts, 'Asset paths must be relative and stay in the workspace'
    candidate=base/path
    resolved=candidate.resolve()
    assert resolved.is_relative_to(base.resolve()), 'Asset path escapes the workspace'
    assert candidate.is_file(), 'Local asset missing'
    return candidate


def validate(article,manifest,profile=None,use_local=True):
    article=Path(article).resolve();manifest=Path(manifest).resolve()
    text=article.read_text(encoding='utf-8');data=json.loads(manifest.read_text(encoding='utf-8'))
    options=load_settings(data,profile,use_local)
    branded=options['image_profile']=='evomap'
    scan=mask_fenced_code(text);lines=scan.splitlines()
    headings=[]
    for index,line in enumerate(lines):
        match=re.match(r'^(#{1,6})\s+(.+?)\s*$',line)
        if match: headings.append((index,len(match[1]),match[2]))
    if options['require_title']:
        assert headings and headings[0][1]==1, 'One article title required'
        assert sum(level==1 for _,level,_ in headings)==1, 'One article title required'
    has_title=bool(headings and headings[0][1]==1)
    reference_heading=data.get('reference_heading')
    allowed={reference_heading} if reference_heading else {'参考文献','参考资料','参考来源','来源','References'}
    has_references=bool(headings and headings[-1][2] in allowed)
    if options['require_references']: assert has_references and headings[-1][1]==2, 'Final heading must be unnumbered references'
    business=headings[1 if has_title else 0:len(headings)-1 if has_references else len(headings)]
    if options['require_subheadings']: assert business and any(level==3 for _,level,_ in business), 'Organize related content with a second level'
    counters,seen={},set()
    for _,level,label in business:
        depth=max(1,level-1)
        assert depth<=3, 'At most three business heading levels'
        match=re.match(r'^(\d+(?:\.\d+)*)(?:\.(?=\s))?\s+(.+)$',label)
        if match:
            number=tuple(int(part) for part in match[1].split('.'));title=match[2]
            assert len(number)==depth, 'Heading depth and number differ'
        else:
            assert options['heading_numbering']!='required', 'Business headings require numbering'
            parent=tuple(counters.get(tuple([1]*(i)),1) for i in range(depth-1))
            if depth>1:
                parents=[n for n in seen if len(n)==depth-1]
                assert parents, 'Missing parent heading';parent=max(parents)
            number=parent+(counters.get(parent,0)+1,);title=label
        assert len(number)==1 or number[:-1] in seen, 'Missing parent heading'
        assert number[-1]==counters.get(number[:-1],0)+1, 'Nonconsecutive heading number'
        counters[number[:-1]]=number[-1];seen.add(number)
        if options['max_heading_units'] is not None: assert units(title)<=options['max_heading_units'], 'Heading exceeds equivalent-character limit'
    first_business=business[0][0] if business else len(lines)
    if options['require_introduction']:
        subtitle='*'+data['subtitle']+'*' if data.get('subtitle') else None
        intro=[line for line in lines[1:first_business] if line.strip() and line!=subtitle and not line.startswith(('![','图 ','---'))]
        assert intro, 'Add a meaningful introduction before business sections'
    links=markdown_links(scan);images=[link for link in links if link['image']]
    figures=data.get('figures',[])
    assert len(images)==len(figures), 'Every Markdown image needs an asset manifest entry'
    if options['require_cover']:
        assert figures and figures[0].get('section')=='cover', 'First image is the cover'
        if business: assert scan.index('![')<scan.index(lines[first_business]), 'Cover precedes the numbered article'
    results=[];body_count=0
    for index,(image,figure) in enumerate(zip(images,figures)):
        cover=figure.get('section')=='cover'
        title=figure.get('title',image['label'])
        if cover:
            assert index==0 and figure.get('number') is None, 'Cover must be first and unnumbered'
            assert not re.match(r'^(?:图\s*)?\d',title), 'Cover name must be unnumbered'
            if branded: assert image['label']==title, 'Cover alt text is its unnumbered name'
        else:
            body_count+=1
            if branded or 'number' in figure: assert figure.get('number')==body_count, 'Body figures start at 1 and are consecutive'
            if branded:
                assert figure.get('description','').strip(), 'Describe the specific figure content'
                assert image['label']==f"图 {body_count}：{figure['description'].strip()}", 'Use 图 x：具体描述 in alt/caption'
        path_value=figure.get('path',figure.get('png'))
        assert path_value, 'A local path is required for asset validation'
        assert image['target'] in (path_value,figure.get('render_url')), 'Markdown image and manifest differ'
        image_path=local_asset(manifest.parent,path_value)
        if options['strict_asset_naming']:
            stem=title if cover else f'{body_count:02d}-{title}'
            assert image_path.name==stem+'.png', 'Use consistent numbered asset names'
        metrics=image_info(image_path,branded)
        cover_size=options['cover_size']
        if cover and cover_size is not None:
            assert len(cover_size)==2 and all(type(v) is int and v>0 for v in cover_size), 'Invalid cover size'
            assert (metrics['width'],metrics['height'])==tuple(cover_size), 'Cover PNG must have the expected actual pixel dimensions'
        svg_value=figure.get('svg')
        if options['require_svg_sources']: assert svg_value, 'Both PNG and SVG required'
        if svg_value:
            svg=local_asset(manifest.parent,svg_value)
            if options['strict_asset_naming']: assert svg.name==stem+'.svg'
            metrics.update(svg_check(svg,title,options['image_profile']))
            if cover and cover_size is not None:
                root=ET.parse(svg).getroot();assert (float(root.get('width')),float(root.get('height')))==tuple(cover_size), 'Cover SVG must use the same canvas dimensions'
        results.append(dict(metrics,number=None if cover else body_count,title=title))
    used_sections={f.get('section') for f in figures if f.get('section')!='cover'}
    required=data.get('required_figure_sections',sorted({str(n[0]) for n in seen}) if figures and branded else [])
    known={'.'.join(map(str,n)) for n in seen}
    for section in required:
        assert section in known, 'Required figure section does not exist'
        assert any(used and (used==section or used.startswith(section+'.')) for used in used_sections), 'A required business topic has no figure'
    reference_urls={}
    if has_references:
        ref_lines=[line for line in lines[headings[-1][0]+1:] if line.strip()]
        for index,line in enumerate(ref_lines,1):
            match=re.match(rf'^{index}\.\s+.+[：:]\s*(https://\S+)$',line)
            assert match, 'Use numbered article-name:URL references'
            url=match[1];parsed=urlparse(url)
            assert parsed.hostname and not parsed.username and not parsed.password, 'Use HTTPS sources without embedded credentials'
            assert not any(parsed.hostname==domain or parsed.hostname.endswith('.'+domain) for domain in options['private_reference_domains']), 'Private input domain is not a public reference'
            reference_urls[index]=url
        if options['require_references']: assert reference_urls, 'References required'
    citation_body='\n'.join(lines[:headings[-1][0]]) if has_references else scan
    citation_body=re.sub(r'`[^`\n]*`','',citation_body)
    for link in reversed(markdown_links(citation_body)):
        if link['image']: citation_body=citation_body[:link['start']]+citation_body[link['end']:]
    citations=[int(number) for number in re.findall(r'\[(\d+)\]',citation_body)]
    if reference_urls or citations:
        assert list(dict.fromkeys(citations))==list(reference_urls), 'Citations and references must match in first-use order'
    for link in markdown_links(citation_body):
        match=re.fullmatch(r'\[?(\d+)\]?',link['label'])
        if match: assert reference_urls.get(int(match[1]))==link['target'], 'Citation URL differs from its reference'
    return {'passed':True,'profile':options['image_profile'],'heading_count':len(business),'figure_count':body_count,
            'image_count':len(images),'reference_count':len(reference_urls),'cover_size':options['cover_size'],
            'figures':results,'semantic_and_public_access_checks':'manual'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--article',required=True);parser.add_argument('--manifest',required=True)
    parser.add_argument('--profile',choices=('generic','evomap'));parser.add_argument('--no-local',action='store_true')
    parser.add_argument('--output')
    args=parser.parse_args()
    try: result=validate(args.article,args.manifest,args.profile,not args.no_local)
    except (AssertionError,KeyError,ValueError,TypeError,OSError,ET.ParseError,zlib.error,struct.error) as error: raise SystemExit('FAIL: '+str(error))
    rendered=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output: Path(args.output).write_text(rendered,encoding='utf-8')
    print(rendered)
