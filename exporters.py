import xml.etree.ElementTree as ET

def generate_srt(subtitles):
    srt_content = ""
    for i, sub in enumerate(subtitles, start=1):
        start_time = format_timestamp(sub['start'])
        end_time = format_timestamp(sub['end'])
        srt_content += f"{i}\n{start_time} --> {end_time}\n{sub['text']}\n\n"
    return srt_content

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(int((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_premiere_xml(subtitles, sequence_name="SharpSharpNaija", framerate=25):
    xmeml = ET.Element("xmeml", version="4")
    sequence = ET.SubElement(xmeml, "sequence", id="sequence-1")
    ET.SubElement(sequence, "name").text = sequence_name
    
    duration = int(subtitles[-1]['end'] * framerate) if subtitles else 100
    ET.SubElement(sequence, "duration").text = str(duration)
    
    rate = ET.SubElement(sequence, "rate")
    ET.SubElement(rate, "timebase").text = str(framerate)
    ET.SubElement(rate, "ntsc").text = "FALSE"
    
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    track = ET.SubElement(video, "track")
    
    for i, sub in enumerate(subtitles, start=1):
        start_frame = int(sub['start'] * framerate)
        end_frame = int(sub['end'] * framerate)
        clip_duration = end_frame - start_frame
        
        clipitem = ET.SubElement(track, "clipitem", id=f"clipitem-{i}")
        ET.SubElement(clipitem, "name").text = f"Sub_{i}"
        ET.SubElement(clipitem, "duration").text = str(clip_duration)
        
        clip_rate = ET.SubElement(clipitem, "rate")
        ET.SubElement(clip_rate, "timebase").text = str(framerate)
        ET.SubElement(clip_rate, "ntsc").text = "FALSE"
        
        ET.SubElement(clipitem, "start").text = str(start_frame)
        ET.SubElement(clipitem, "end").text = str(end_frame)
        ET.SubElement(clipitem, "in").text = "0"
        ET.SubElement(clipitem, "out").text = str(clip_duration)
        
        generator = ET.SubElement(clipitem, "generatoritem", id=f"generatoritem-{i}")
        ET.SubElement(generator, "name").text = sub['text']
        ET.SubElement(generator, "effect").text = "Text"
        
    return ET.tostring(xmeml, encoding="utf-8", xml_declaration=True).decode("utf-8")
