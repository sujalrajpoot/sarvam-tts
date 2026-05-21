import time
import requests
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from multilingual_tokenizer import MultilingualSentenceTokenizer
from typing import List

class SarvamTTS:
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        self.api_url = "https://www.sarvam.ai/api/playground/tts"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://www.sarvam.ai',
            'priority': 'u=1, i',
            'referer': 'https://www.sarvam.ai/apis/text-to-speech',
            'sec-ch-ua': '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
        }
        self.tokenizer = MultilingualSentenceTokenizer()

    def get_voices(self) -> list:
        return ['shreya', 'shubh', 'manan', 'ishita', 'priya', 'suhani', 'ashutosh', 'ritu', 'amit', 'sumit', 'pooja', 'simran', 'rahul', 'kavya', 'ratan', 'shruti', 'aditya', 'soham', 'rehan', 'vijay', 'tarun', 'anand', 'aayan', 'rohan', 'dev', 'sunny', 'kabir', 'varun', 'neha', 'mani', 'mohit', 'rupali', 'advait', 'roopa', 'tanya', 'gokul', 'kavitha']
    
    def get_languages(self) -> dict:
        return {
            "english": "en-IN",
            "hindi": "hi-IN",
            "bengali": "bn-IN",
            "tamil": "ta-IN",
            "telugu": "te-IN",
            "kannada": "kn-IN",
            "malayalam": "ml-IN",
            "marathi": "mr-IN",
            "gujarati": "gu-IN",
            "punjabi": "pa-IN",
            "odia": "od-IN"
        }
    
    def _save_audio(self, audio_data: bytes, output_filepath: str) -> None:
        with open(output_filepath, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved to {output_filepath}")

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        # Convenience function to split text into sentences using SentenceTokenizer.
        
        Args:
            text (str): Input text to split into sentences.
        
        Returns:
            List[str]: List of properly formatted sentences.
        """
        return self.tokenizer.tokenize(text.strip())

    def tts(self, text: str, language: str, voice: str, pace: float = 1.0, temperature: float = 0.6, sample_rate: int = 22050, output_filepath: str = "sarvam-tts.mp3") -> bytes:
        """
        Converts text to speech using the SarvamTTS API and saves it to a file.
        """
        if temperature < 0.0 or temperature > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        
        if pace < 0.5 or pace > 2.0:
            raise ValueError("Pace must be between 0.5 and 2.0")
        
        if sample_rate not in [22050, 8000, 48000]:
            raise ValueError("Sample rate must be one of 22050, 8000, or 48000")
        
        # Split text into sentences
        sentences = self.tokenizer.tokenize(text, language=language)
        for index, sen in enumerate(sentences):
            print(f"{index}. Sentence: {sen}\n")

        languages = self.get_languages()

        # Function to request audio for each chunk
        def generate_audio_for_chunk(part_text: str, part_number: int):
            while True:
                try:
                    json_data = {
                        'text': part_text,
                        'target_language_code': languages.get(language.lower(), 'en-IN'),
                        'speaker': voice,
                        'model': 'bulbul:v3-beta',
                        'pace': pace,
                        'speech_sample_rate': sample_rate,
                        'temperature': temperature,
                        'enable_preprocessing': True,
                        'output_audio_codec': 'mp3',
                    }
                    response = requests.post(self.api_url, headers=self.headers, json=json_data)
                    if response.content:
                        try:
                            # Try parsing response as JSON
                            json_response = response.json()
                            print(f"Received JSON response for chunk {part_number}: {json_response}")
                        except ValueError:
                            # If not JSON, treat it as audio data
                            audio_data = response.content
                            
                            if self.verbose:
                                print(f"Chunk {part_number} processed successfully.")
                            return part_number, audio_data
                    else:
                        if self.verbose:
                            print(f"No data received for chunk {part_number}. Retrying...")
                except requests.RequestException as e:
                    if self.verbose:
                        print(f"Error for chunk {part_number}: {e}. Retrying...")
                    time.sleep(1)
        try:
            # Using ThreadPoolExecutor to handle requests concurrently
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(generate_audio_for_chunk, sentence.strip(), chunk_num): chunk_num 
                        for chunk_num, sentence in enumerate(sentences, start=1)}
                
                # Dictionary to store results with order preserved
                audio_chunks = {}

                for future in as_completed(futures):
                    chunk_num = futures[future]
                    try:
                        part_number, audio_data = future.result()
                        audio_chunks[part_number] = audio_data  # Store the audio data in correct sequence
                    except Exception as e:
                        if self.verbose:
                            print(f"Failed to generate audio for chunk {chunk_num}: {e}")

            # Combine audio chunks in the correct sequence
            combined_audio = BytesIO()
            for part_number in sorted(audio_chunks.keys()):
                combined_audio.write(audio_chunks[part_number])
                if self.verbose:
                    print(f"Added chunk {part_number} to the combined file.")

            # Save the combined audio data to a single file
            with open(output_filepath, 'wb') as f:
                f.write(combined_audio.getvalue())
            if self.verbose:print(f"\033[1;93mFinal Audio Saved as {output_filepath}.\033[0m")
            return f"\033[1;93mFinal Audio Saved as {output_filepath}.\033[0m"

        except requests.exceptions.RequestException as e:
            raise requests.RequestException(
                f"Failed to perform the operation: {e}"
            )

if __name__ == "__main__":
    # Initialize the tokenizer and TTS class
    tokenizer = MultilingualSentenceTokenizer()
    sarvam_tts = SarvamTTS()

    # Test cases for different languages
    test_texts = {
        'english': (
            "Dr. Smith visited a small village near the mountains during his summer vacation. "
            "He spent time with local families, learned about their traditions, and tasted homemade food. "
            "Every evening, children gathered near the lake to listen to stories and play games together. "
            "The peaceful environment and friendly people made his journey unforgettable and deeply meaningful."
        ),

        'hindi': (
            "राहुल अपने परिवार के साथ गाँव गया था। वहाँ उसने खेतों में काम करते किसानों को देखा और "
            "बच्चों के साथ खेला। शाम को सभी लोग मंदिर के पास इकट्ठा होकर बातें कर रहे थे। "
            "उसकी दादी ने उसे पुराने समय की कई रोचक कहानियाँ सुनाईं। गाँव का शांत वातावरण राहुल को "
            "बहुत पसंद आया और उसने फिर से वहाँ आने का वादा किया।"
        ),

        'tamil': (
            "ரவி தனது நண்பர்களுடன் கடற்கரைக்கு சென்றான். அவர்கள் அங்கு மணலில் விளையாடி, கடல் அலைகளை "
            "ரசித்தனர். பின்னர் அருகிலிருந்த உணவகத்தில் சுவையான உணவுகளை சாப்பிட்டனர். மாலை நேரத்தில் "
            "சூரியன் மறையும் காட்சியை பார்த்து அனைவரும் மகிழ்ந்தனர். அந்த நாள் ரவிக்கு மிகவும் "
            "மகிழ்ச்சியான அனுபவமாக இருந்தது மற்றும் அவர் அதை நீண்ட நாட்கள் நினைவில் வைத்திருந்தான்."
        ),

        'telugu': (
            "రాము తన స్నేహితులతో కలిసి పార్క్‌కు వెళ్లాడు. అక్కడ వారు చెట్ల నీడలో కూర్చొని చాలా సేపు "
            "మాట్లాడుకున్నారు. పిల్లలు ఆటలు ఆడుతూ ఆనందంగా గడిపారు. తరువాత అందరూ కలిసి ఐస్‌క్రీమ్ తిన్నారు "
            "మరియు ఫోటోలు తీసుకున్నారు. సాయంత్రం సూర్యాస్తమయం చాలా అందంగా కనిపించింది. ఆ రోజు రాముకు "
            "మరచిపోలేని అనుభవంగా మారింది."
        ),

        'odia': (
            "ରାହୁଲ ସକାଳେ ତାଙ୍କ ବନ୍ଧୁମାନଙ୍କ ସହିତ ନଦୀ କୂଳକୁ ଯାଇଥିଲେ। ସେମାନେ ସେଠାରେ ଖେଳିଲେ ଏବଂ "
            "ପ୍ରକୃତିର ସୁନ୍ଦର ଦୃଶ୍ୟ ଉପଭୋଗ କଲେ। ମଧ୍ୟାହ୍ନରେ ସମସ୍ତେ ମିଶି ଖାଦ୍ୟ ଖାଇଥିଲେ ଏବଂ ଗୀତ ଗାଇଥିଲେ। "
            "ସନ୍ଧ୍ୟାବେଳେ ସୂର୍ଯ୍ୟାସ୍ତ ଦେଖି ସେମାନେ ବହୁତ ଖୁସି ହେଲେ। ସେହି ଦିନଟି ରାହୁଲଙ୍କ ପାଇଁ ଅତ୍ୟନ୍ତ "
            "ସ୍ମରଣୀୟ ଅନୁଭବ ହେଇରହିଲା।"
        ),

        'bengali': (
            "সুমন তার পরিবারের সাথে গ্রামের বাড়িতে বেড়াতে গিয়েছিল। সেখানে সে পুকুরে মাছ ধরতে দেখল "
            "এবং বন্ধুদের সাথে মাঠে খেলাধুলা করল। বিকেলে সবাই একসাথে বসে চা এবং নাস্তা খেয়েছিল। "
            "তার দাদু তাকে গ্রামের পুরোনো দিনের অনেক গল্প শোনালেন। গ্রামের শান্ত পরিবেশ ও মানুষের "
            "আতিথেয়তা সুমনের খুব ভালো লেগেছিল।"
        ),

        'marathi': (
            "अमोल आपल्या मित्रांसोबत सहलीला गेला होता। त्यांनी डोंगरांवर फिरत सुंदर निसर्गाचा आनंद घेतला। "
            "दुपारी सर्वांनी मिळून जेवण केले आणि अनेक फोटो काढले। संध्याकाळी त्यांनी नदीकिनारी बसून गाणी "
            "गायली आणि गप्पा मारल्या। त्या दिवसातील प्रत्येक क्षण अमोलसाठी खूप खास होता आणि त्याने "
            "पुन्हा तिथे जाण्याचा निर्णय घेतला।"
        ),

        'kannada': (
            "ರಾಹುಲ್ ತನ್ನ ಕುಟುಂಬದವರೊಂದಿಗೆ ಉದ್ಯಾನವನಕ್ಕೆ ಹೋಗಿದ್ದನು. ಅಲ್ಲಿ ಮಕ್ಕಳು ಆಟವಾಡುತ್ತಿದ್ದರು ಮತ್ತು "
            "ಹೂಗಳ ಸೌಂದರ್ಯವನ್ನು ಎಲ್ಲರೂ ಆನಂದಿಸುತ್ತಿದ್ದರು. ನಂತರ ಅವರು ಮರಗಳ ನೆರಳಿನಲ್ಲಿ ಕೂತು ತಿಂಡಿ ತಿಂದರು. "
            "ಸಂಜೆಯ ವೇಳೆಗೆ ತಂಪಾದ ಗಾಳಿ ಬೀಸತೊಡಗಿತು ಮತ್ತು ಎಲ್ಲರೂ ಸಂತೋಷಪಟ್ಟರು. ಆ ದಿನದ ಸುಂದರ ನೆನಪುಗಳು "
            "ರಾಹುಲ್ ಮನಸ್ಸಿನಲ್ಲಿ ದೀರ್ಘಕಾಲ ಉಳಿದವು."
        ),

        'malayalam': (
            "അരുൺ തന്റെ കൂട്ടുകാരുമായി കടൽത്തീരത്തേക്ക് പോയി. അവിടെ അവർ മണലിൽ കളിക്കുകയും കടൽതിരകൾ "
            "ആസ്വദിക്കുകയും ചെയ്തു. ശേഷം സമീപത്തെ ഹോട്ടലിൽ നിന്ന് ഭക്ഷണം കഴിച്ചു. വൈകുന്നേരത്തിൽ സൂര്യാസ്തമയത്തിന്റെ "
            "സൗന്ദര്യം കണ്ടപ്പോൾ എല്ലാവർക്കും വളരെ സന്തോഷമായി. ആ ദിവസം അരുണിന് ഏറെ മനോഹരമായ അനുഭവമായി "
            "മാറി, അവൻ അത് എപ്പോഴും ഓർമ്മിച്ചു."
        ),

        'gujarati': (
            "રવિ પોતાના પરિવાર સાથે ગામમાં ગયો હતો. ત્યાં તેણે ખેતરોમાં કામ કરતા ખેડૂતોને જોયા અને "
            "બાળકો સાથે રમ્યો. સાંજે બધા લોકો એકત્રિત થઈને વાતો કરતા હતા અને સ્વાદિષ્ટ ભોજન માણતા હતા. "
            "રવિએ પોતાના દાદાથી જૂના સમયની રસપ્રદ વાર્તાઓ સાંભળી. ગામનું શાંત વાતાવરણ અને લોકોનો પ્રેમ "
            "તેને ખૂબ ગમ્યો."
        ),

        'punjabi': (
            "ਅਮਨ ਆਪਣੇ ਦੋਸਤਾਂ ਨਾਲ ਪਿੰਡ ਗਿਆ ਸੀ। ਉੱਥੇ ਉਹਨਾਂ ਨੇ ਖੇਤਾਂ ਵਿੱਚ ਘੁੰਮ ਕੇ ਪ੍ਰਕਿਰਤੀ ਦਾ ਆਨੰਦ ਮਾਣਿਆ। "
            "ਬੱਚੇ ਮਿਲ ਕੇ ਖੇਡਦੇ ਰਹੇ ਅਤੇ ਸਭ ਨੇ ਇਕੱਠੇ ਬੈਠ ਕੇ ਖਾਣਾ ਖਾਧਾ। ਸ਼ਾਮ ਦੇ ਸਮੇਂ ਉਹਨਾਂ ਨੇ ਦਰਿਆ ਦੇ ਕਿਨਾਰੇ "
            "ਬੈਠ ਕੇ ਗੱਲਾਂ ਕੀਤੀਆਂ ਅਤੇ ਗੀਤ ਗਾਏ। ਉਹ ਦਿਨ ਅਮਨ ਲਈ ਬਹੁਤ ਯਾਦਗਾਰ ਬਣ ਗਿਆ।"
        )
    }
    
    print("Multilingual Sentence Tokenizer Test Results\n" + "="*50)
    
    for lang, text in test_texts.items():
        print(f"\n{lang.upper()}:")
        print(f"Input: {text}")
        sentences = tokenizer.tokenize(text, language=lang)
        voice = "shreya"
        # sarvam_tts.tts(text=text, language=lang, voice=voice, output_filepath=f"output_{lang}.mp3")