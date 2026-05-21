import re
from typing import List, Dict, Set, Tuple, Pattern


class MultilingualSentenceTokenizer:
    """Advanced multilingual sentence tokenizer supporting Indian languages and English."""
    
    def __init__(self) -> None:
        # English abbreviations
        self.TITLES: Set[str] = {
            'mr', 'mrs', 'ms', 'dr', 'prof', 'rev', 'sr', 'jr', 'esq',
            'hon', 'pres', 'gov', 'atty', 'supt', 'det', 'rev', 'col', 'maj', 
            'gen', 'capt', 'cmdr', 'lt', 'sgt', 'cpl', 'pvt'
        }
        
        self.ACADEMIC: Set[str] = {
            'ph.d', 'phd', 'm.d', 'md', 'b.a', 'ba', 'm.a', 'ma', 'd.d.s', 'dds',
            'm.b.a', 'mba', 'b.sc', 'bsc', 'm.sc', 'msc', 'llb', 'll.b', 'bl'
        }
        
        self.ORGANIZATIONS: Set[str] = {
            'inc', 'ltd', 'co', 'corp', 'llc', 'llp', 'assn', 'bros', 'plc', 'cos',
            'intl', 'dept', 'est', 'dist', 'mfg', 'div'
        }
        
        self.MONTHS: Set[str] = {
            'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        }
        
        self.UNITS: Set[str] = {
            'oz', 'pt', 'qt', 'gal', 'ml', 'cc', 'km', 'cm', 'mm', 'ft', 'in',
            'kg', 'lb', 'lbs', 'hz', 'khz', 'mhz', 'ghz', 'kb', 'mb', 'gb', 'tb'
        }
        
        self.TECHNOLOGY: Set[str] = {
            'v', 'ver', 'app', 'sys', 'dir', 'exe', 'lib', 'api', 'sdk', 'url',
            'cpu', 'gpu', 'ram', 'rom', 'hdd', 'ssd', 'lan', 'wan', 'sql', 'html'
        }
        
        self.MISC: Set[str] = {
            'vs', 'etc', 'ie', 'eg', 'no', 'al', 'ca', 'cf', 'pp', 'est', 'st',
            'approx', 'appt', 'apt', 'dept', 'depts', 'min', 'max', 'avg'
        }

        # Combine all English abbreviations
        self.all_abbreviations: Set[str] = (
            self.TITLES | self.ACADEMIC | self.ORGANIZATIONS |
            self.MONTHS | self.UNITS | self.TECHNOLOGY | self.MISC
        )

        # Language-specific sentence terminators
        self.LANGUAGE_TERMINATORS: Dict[str, str] = {
            'hindi': '।॥',  # Devanagari Danda and Double Danda
            'english': '.!?',
            'tamil': '.!?',  # Tamil uses period from English
            'telugu': '.!?',  # Telugu uses period from English
            'odia': '।॥',  # Odia uses Devanagari-like Danda
            'bengali': '।॥',  # Bengali Danda
            'marathi': '।॥',  # Marathi uses Devanagari Danda
            'kannada': '.!?',  # Kannada uses period from English
            'malayalam': '.!?',  # Malayalam uses period from English
            'gujarati': '।॥',  # Gujarati uses Devanagari-like Danda
            'punjabi': '।॥'  # Punjabi uses Gurmukhi Danda
        }

        # Unicode ranges for each language script
        self.SCRIPT_RANGES: Dict[str, str] = {
            'hindi': r'\u0900-\u097F',  # Devanagari
            'english': r'A-Za-z',
            'tamil': r'\u0B80-\u0BFF',  # Tamil
            'telugu': r'\u0C00-\u0C7F',  # Telugu
            'odia': r'\u0B00-\u0B7F',  # Odia (Oriya)
            'bengali': r'\u0980-\u09FF',  # Bengali
            'marathi': r'\u0900-\u097F',  # Devanagari (same as Hindi)
            'kannada': r'\u0C80-\u0CFF',  # Kannada
            'malayalam': r'\u0D00-\u0D7F',  # Malayalam
            'gujarati': r'\u0A80-\u0AFF',  # Gujarati
            'punjabi': r'\u0A00-\u0A7F'  # Gurmukhi
        }

        # Common Indian language abbreviations (transliterated)
        self.INDIAN_ABBREVIATIONS: Set[str] = {
            'shri', 'smt', 'ku', 'dr', 'prof',  # Titles
        }

        # Special patterns
        self.ELLIPSIS: str = r'\.{2,}|…'
        self.URL_PATTERN: str = (
            r'(?:https?:\/\/|www\.)[\w\-\.]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?'
        )
        self.EMAIL_PATTERN: str = r'[\w\.-]+@[\w\.-]+\.\w+'
        self.NUMBER_PATTERN: str = (
            r'\d+(?:\.\d+)?(?:%|°|km|cm|mm|m|kg|g|lb|ft|in|mph|kmh|hz|mhz|ghz)?'
        )
        
        # Quote and bracket pairs
        self.QUOTE_PAIRS: Dict[str, str] = {
            '"': '"', "'": "'", '"': '"', "「": "」", "『": "』",
            "«": "»", "‹": "›", "'": "'", "‚": "'", '\'': '\''
        }
        
        self.BRACKETS: Dict[str, str] = {
            '(': ')', '[': ']', '{': '}', '⟨': '⟩', '「': '」',
            '『': '』', '【': '】', '〖': '〗', '｢': '｣'
        }

        # Supported languages
        self.SUPPORTED_LANGUAGES: Set[str] = {
            'hindi', 'english', 'tamil', 'telugu', 'odia', 
            'bengali', 'marathi', 'kannada', 'malayalam', 
            'gujarati', 'punjabi'
        }

        # Compile regex patterns
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance."""
        # Build combined script range for all supported languages
        all_scripts = ''.join([
            self.SCRIPT_RANGES[lang] for lang in self.SUPPORTED_LANGUAGES
        ])
        
        # Build combined terminators
        all_terminators = ''.join(set(''.join(
            self.LANGUAGE_TERMINATORS.values()
        )))
        
        # Pattern for finding potential sentence boundaries (multilingual)
        self.SENTENCE_END: Pattern = re.compile(
            rf'''
            # Group for sentence endings
            (?:
                # Standard endings with optional quotes/brackets
                (?<=[{re.escape(all_terminators)}])[\"\'\)\]\}}»›」』\s]*
                
                # Ellipsis
                |(?:\.{{2,}}|…)
            )
            
            # Must be followed by whitespace and capital letter, number, or script character
            (?=\s+(?:[A-Z0-9{all_scripts}]|["'({{[\[「『《‹〈][A-Z{all_scripts}]))
            ''',
            re.VERBOSE | re.UNICODE
        )

        # Pattern for English abbreviations
        abbrev_pattern = '|'.join(re.escape(abbr) for abbr in self.all_abbreviations)
        self.ABBREV_PATTERN: Pattern = re.compile(
            fr'\b(?:{abbrev_pattern})\.?',
            re.IGNORECASE
        )

    def _detect_language(self, text: str) -> str:
        """Detect the primary language of the text based on script."""
        # Count characters from each script
        script_counts: Dict[str, int] = {lang: 0 for lang in self.SUPPORTED_LANGUAGES}
        
        for lang, script_range in self.SCRIPT_RANGES.items():
            pattern = re.compile(f'[{script_range}]', re.UNICODE)
            script_counts[lang] = len(pattern.findall(text))
        
        # Return language with most characters
        detected_lang = max(script_counts.items(), key=lambda x: x[1])[0]
        
        # If no script detected (very short text), default to English
        if script_counts[detected_lang] == 0:
            return 'english'
        
        return detected_lang

    def _protect_special_cases(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Protect URLs, emails, and other special cases from being split."""
        protected = text
        placeholders: Dict[str, str] = {}
        counter = 0

        # Protect URLs and emails
        for pattern in [self.URL_PATTERN, self.EMAIL_PATTERN]:
            for match in re.finditer(pattern, protected):
                placeholder = f'__PROTECTED_{counter}__'
                placeholders[placeholder] = match.group()
                protected = protected.replace(match.group(), placeholder, 1)
                counter += 1

        # Protect quoted content
        protected_chars = list(protected)
        i = 0
        while i < len(protected_chars):
            char = protected_chars[i]
            if char in self.QUOTE_PAIRS:
                # Find closing quote
                closing = self.QUOTE_PAIRS[char]
                j = i + 1
                while j < len(protected_chars) and protected_chars[j] != closing:
                    j += 1
                
                if j < len(protected_chars):
                    content = ''.join(protected_chars[i:j + 1])
                    placeholder = f'__PROTECTED_{counter}__'
                    placeholders[placeholder] = content
                    protected_chars[i:j + 1] = list(placeholder)
                    counter += 1
                    i = i + len(placeholder) - 1
            i += 1

        return ''.join(protected_chars), placeholders

    def _restore_special_cases(self, text: str, placeholders: Dict[str, str]) -> str:
        """Restore protected content."""
        restored = text
        for placeholder, original in placeholders.items():
            restored = restored.replace(placeholder, original)
        return restored

    def _handle_abbreviations(self, text: str) -> str:
        """Handle abbreviations to prevent incorrect sentence splitting."""
        def replace_abbrev(match: re.Match) -> str:
            abbr = match.group().lower().rstrip('.')
            if abbr in self.all_abbreviations or abbr in self.INDIAN_ABBREVIATIONS:
                return match.group().replace('.', '__DOT__')
            return match.group()

        return self.ABBREV_PATTERN.sub(replace_abbrev, text)

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving paragraph breaks."""
        # Replace multiple newlines with special marker
        text = re.sub(r'\n\s*\n', ' __PARA__ ', text)
        # Normalize remaining whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _restore_formatting(self, sentences: List[str], language: str) -> List[str]:
        """Restore original formatting and clean up sentences."""
        restored = []
        script_range = self.SCRIPT_RANGES.get(language, self.SCRIPT_RANGES['english'])
        script_pattern = re.compile(f'[{script_range}]', re.UNICODE)
        
        for sentence in sentences:
            # Restore dots in abbreviations
            sentence = sentence.replace('__DOT__', '.')
            
            # Restore paragraph breaks
            sentence = sentence.replace('__PARA__', '\n\n')
            
            # Clean up whitespace
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            
            # Capitalize first letter for English/Latin scripts
            if language == 'english' and sentence:
                words = sentence.split()
                if words and words[0].lower() not in self.all_abbreviations:
                    sentence = sentence[0].upper() + sentence[1:]
            
            if sentence:
                restored.append(sentence)
        
        return restored
    
    def _sanitize_text(self, text: str) -> str:
        """Removes emojis from text."""
        return re.sub(
            r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
            r'\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF'
            r'\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF'
            r'\U00002702-\U000027B0\U000024C2-\U0001F251]+', 
            '', text
        )

    def tokenize(self, text: str, language: str = None) -> List[str]:
        """
        Split text into sentences while handling complex cases and multiple languages.
        
        Args:
            text (str): Input text to split into sentences.
            language (str, optional): Language of the text. If None, auto-detects.
            
        Returns:
            List[str]: List of properly formatted sentences.
        """
        if not text or not text.strip():
            return []
        
        # Auto-detect language if not provided
        if language is None:
            language = self._detect_language(text)
        
        # Validate language
        if language.lower() not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )
        
        language = language.lower()
        text = self._sanitize_text(text)

        # Step 1: Protect special cases
        protected_text, placeholders = self._protect_special_cases(text)
        
        # Step 2: Normalize whitespace
        protected_text = self._normalize_whitespace(protected_text)
        
        # Step 3: Handle abbreviations (mainly for English)
        if language == 'english':
            protected_text = self._handle_abbreviations(protected_text)
        
        # Step 4: Split into potential sentences
        potential_sentences = self.SENTENCE_END.split(protected_text)
        
        # Step 5: Process and restore formatting
        sentences = self._restore_formatting(potential_sentences, language)
        
        # Step 6: Restore special cases
        sentences = [self._restore_special_cases(s, placeholders) for s in sentences]
        
        # Step 7: Post-process sentences
        final_sentences = []
        current_sentence = []
        
        for sentence in sentences:
            # Skip empty sentences
            if not sentence.strip():
                continue
                
            # Check if sentence might be continuation of previous
            # (mainly for English - lowercase start)
            if language == 'english' and current_sentence and sentence and sentence[0].islower():
                current_sentence.append(sentence)
            else:
                if current_sentence:
                    final_sentences.append(' '.join(current_sentence))
                current_sentence = [sentence]
        
        # Add last sentence if exists
        if current_sentence:
            final_sentences.append(' '.join(current_sentence))
        
        return final_sentences

# Example usage and testing
if __name__ == "__main__":
    tokenizer = MultilingualSentenceTokenizer()
    
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
        print(f"Output ({len(sentences)} sentences):")
        for i, sent in enumerate(sentences, 1):
            print(f"  {i}. {sent}")