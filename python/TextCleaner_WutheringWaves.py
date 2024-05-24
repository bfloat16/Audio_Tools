import sqlite3
import json

def clean_bin_data(data):
    start_index = data.find(b'[{')
    end_index = data.rfind(b'}]')
    if start_index != -1 and end_index != -1:
        cleaned_data = data[start_index:end_index+2]
        return cleaned_data
    return None

def extract_talk_items(data):
    result = []
    for dictionary_A in data:
        if dictionary_A.get("Name") == "ShowTalk":
            talk_items = dictionary_A.get("Params", {}).get("TalkItems", [])
            for dictionary_B in talk_items:
                if dictionary_B.get("Type") == "Talk" and dictionary_B.get("PlayVoice"):
                    result.append({
                        "TidTalk": dictionary_B.get("TidTalk"),
                        "WhoId": dictionary_B.get("WhoId")
                    })
    return result

def get_speaker_name(cursor, who_id):
    speaker_id = f"Speaker_{who_id}_Name"
    cursor.execute("SELECT Content FROM MultiText WHERE Id=?", (speaker_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return who_id

def get_talk_text(cursor, tid_talk):
    cursor.execute("SELECT Content FROM MultiText WHERE Id=?", (tid_talk,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

db_flowstate_file = r"D:\Wuthering Waves Game\Client\Content\Paks\pakchunk10-WindowsNoEditor\Client\Content\Aki\ConfigDB\db_flowState.db"
db_lang_file = r"D:\Wuthering Waves Game\Client\Content\Paks\pakchunk10-WindowsNoEditor\Client\Content\Aki\ConfigDB\zh-Hans\lang_multi_text.db"
output_file = 'WutheringWaves_CHS_index.json'

conn_flowstate = sqlite3.connect(db_flowstate_file)
cursor_flowstate = conn_flowstate.cursor()

conn_lang = sqlite3.connect(db_lang_file)
cursor_lang = conn_lang.cursor()

cursor_flowstate.execute("SELECT Statekey, binData FROM flowstate")
rows = cursor_flowstate.fetchall()

all_extracted_items = []

for row in rows:
    statekey = row[0]
    bin_data = row[1]
    print(f"Processing Statekey: {statekey}")
    if bin_data:
        cleaned_data = clean_bin_data(bin_data)
        if cleaned_data is None:
            continue
        try:
            cleaned_data_str = cleaned_data.decode('utf-8')
            json_data = json.loads(cleaned_data_str)
            extracted_items = extract_talk_items(json_data)
            for item in extracted_items:
                who_id = item["WhoId"]
                tid_talk = item["TidTalk"]
                speaker_name = get_speaker_name(cursor_lang, who_id)
                talk_text = get_talk_text(cursor_lang, tid_talk)
                item["WhoId"] = speaker_name
                item["Text"] = talk_text
            all_extracted_items.extend(extracted_items)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error decoding JSON for binData: {bin_data}, error: {e}")

conn_flowstate.close()
conn_lang.close()

print(f"Total extracted items: {len(all_extracted_items)}")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_extracted_items, f, ensure_ascii=False, indent=4)
