"""Multilingual phrases for the Agentforce assistant.

The assistant's answers are *templates* with data poured into them, which is what makes
translating them honest and offline. The structure — headings, field labels, the non-fraud
contract — is translated here and committed; the data poured in is never translated.

**What is deliberately not translated, and why.**

Work references, agency names, MP names and rupee figures stay exactly as they are. A work
reference is an identifier, not a word. An implementing agency's name is how it appears on
its own letterhead. Translating either would produce something an officer could not search
for and could not quote back to anyone.

**What must always be translated.** The contract line. A reader in Tamil who is shown a
list of flagged works and an English disclaimer has, in practice, been shown a list of
flagged works. That is the one sentence with a duty to arrive in the reader's language.

Nothing here is machine-translated at runtime — that would need the live model, and with no
credits the fallback would silently be English. These are committed strings, so a Tamil
answer is a Tamil answer whether or not billing is connected.
"""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)

#: The phrases the answer templates are built from. Anything not listed falls back to
#: English rather than to a guess.
PHRASES: dict[str, dict[str, str]] = {
    "en": {
        "brief": "Agentforce Investigation Brief",
        "location": "Location & ownership",
        "state": "State / constituency",
        "agency": "Implementing agency",
        "mp": "Recommended by",
        "financial": "Financial & risk assessment",
        "recommended": "Recommended sanction",
        "exposure": "Exposure at risk",
        "confidence": "Confidence band",
        "families": "independent signal families",
        "casework": "Salesforce casework & Path",
        "stage": "Current investigation stage",
        "tier": "Escalation tier",
        "review_by": "Target review date",
        "guidance": "Officer guidance at this stage",
        "evidence": "Corroborating evidence",
        "next_step": "Recommended next step",
        "audit_plan": "Agentforce audit plan",
        "auditor_days": "auditor-days",
        "what_it_buys": "What this budget buys",
        "works": "works",
        "visits": "agency visits",
        "in_states": "states",
        "covered": "of exposure covered",
        "no_extra_travel": "of those works cost no extra travel",
        "start_here": "Start here",
        "same_trip": "same trip",
        "casework_status": "Agentforce casework status",
        "cases_loaded": "investigation cases are loaded in Salesforce",
        "not_yet_seen": "have not been looked at by a person yet",
        "contract": (
            "This is an investigation lead supported by evidence. It is not a finding of "
            "fraud or wrongdoing. A human reviews the evidence and decides what happens."
        ),
        "plan_contract": (
            "This allocates attention. It does not allege anything about any work, agency "
            "or person, and a human approves the plan."
        ),
        "english_note": "",
    },
    "hi": {
        "brief": "एजेंटफोर्स जाँच सारांश",
        "location": "स्थान एवं उत्तरदायित्व",
        "state": "राज्य / निर्वाचन क्षेत्र",
        "agency": "क्रियान्वयन एजेंसी",
        "mp": "अनुशंसाकर्ता",
        "financial": "वित्तीय एवं जोखिम आकलन",
        "recommended": "अनुशंसित स्वीकृति",
        "exposure": "जोखिम राशि",
        "confidence": "विश्वास श्रेणी",
        "families": "स्वतंत्र संकेत श्रेणियाँ",
        "casework": "सेल्सफोर्स प्रकरण एवं चरण",
        "stage": "वर्तमान जाँच चरण",
        "tier": "उच्चीकरण स्तर",
        "review_by": "लक्षित समीक्षा तिथि",
        "guidance": "इस चरण पर अधिकारी हेतु मार्गदर्शन",
        "evidence": "पुष्टिकारक साक्ष्य",
        "next_step": "अनुशंसित अगला कदम",
        "audit_plan": "एजेंटफोर्स अंकेक्षण योजना",
        "auditor_days": "अंकेक्षक-दिवस",
        "what_it_buys": "इस बजट से क्या मिलता है",
        "works": "कार्य",
        "visits": "एजेंसी दौरे",
        "in_states": "राज्यों में",
        "covered": "जोखिम राशि सम्मिलित",
        "no_extra_travel": "कार्यों पर कोई अतिरिक्त यात्रा व्यय नहीं",
        "start_here": "यहाँ से आरंभ करें",
        "same_trip": "उसी दौरे में",
        "casework_status": "एजेंटफोर्स प्रकरण स्थिति",
        "cases_loaded": "जाँच प्रकरण सेल्सफोर्स में उपलब्ध हैं",
        "not_yet_seen": "अब तक किसी व्यक्ति द्वारा नहीं देखे गए",
        "contract": (
            "यह साक्ष्य-आधारित जाँच संकेत है। यह धोखाधड़ी या अनियमितता का निष्कर्ष नहीं है। "
            "साक्ष्य की समीक्षा कर निर्णय एक मनुष्य लेता है।"
        ),
        "plan_contract": (
            "यह केवल ध्यान का आवंटन करता है। यह किसी कार्य, एजेंसी या व्यक्ति पर कोई आरोप "
            "नहीं लगाता, और योजना को एक मनुष्य स्वीकृत करता है।"
        ),
        "english_note": "विवरण अंग्रेज़ी में है; आँकड़े और संदर्भ मूल रूप में रखे गए हैं।",
    },
    "bn": {
        "brief": "এজেন্টফোর্স তদন্ত সারসংক্ষেপ",
        "location": "অবস্থান ও দায়িত্ব",
        "state": "রাজ্য / কেন্দ্র",
        "agency": "বাস্তবায়নকারী সংস্থা",
        "mp": "সুপারিশকারী",
        "financial": "আর্থিক ও ঝুঁকি মূল্যায়ন",
        "recommended": "সুপারিশকৃত অনুমোদন",
        "exposure": "ঝুঁকিতে থাকা অর্থ",
        "confidence": "নির্ভরযোগ্যতা স্তর",
        "families": "স্বাধীন সংকেত শ্রেণি",
        "casework": "সেলসফোর্স মামলা ও ধাপ",
        "stage": "বর্তমান তদন্ত ধাপ",
        "tier": "ঊর্ধ্বতন স্তর",
        "review_by": "পর্যালোচনার লক্ষ্য তারিখ",
        "guidance": "এই ধাপে কর্মকর্তার নির্দেশনা",
        "evidence": "সমর্থনকারী প্রমাণ",
        "next_step": "সুপারিশকৃত পরবর্তী পদক্ষেপ",
        "audit_plan": "এজেন্টফোর্স নিরীক্ষা পরিকল্পনা",
        "auditor_days": "নিরীক্ষক-দিবস",
        "what_it_buys": "এই বাজেটে যা পাওয়া যায়",
        "works": "কাজ",
        "visits": "সংস্থা পরিদর্শন",
        "in_states": "রাজ্যে",
        "covered": "ঝুঁকির অর্থ অন্তর্ভুক্ত",
        "no_extra_travel": "কাজে অতিরিক্ত ভ্রমণ ব্যয় নেই",
        "start_here": "এখান থেকে শুরু করুন",
        "same_trip": "একই সফরে",
        "casework_status": "এজেন্টফোর্স মামলার অবস্থা",
        "cases_loaded": "তদন্ত মামলা সেলসফোর্সে রয়েছে",
        "not_yet_seen": "এখনও কেউ দেখেননি",
        "contract": (
            "এটি প্রমাণসহ একটি তদন্ত সূত্র। এটি জালিয়াতি বা অনিয়মের সিদ্ধান্ত নয়। "
            "প্রমাণ পর্যালোচনা করে একজন মানুষ সিদ্ধান্ত নেন।"
        ),
        "plan_contract": (
            "এটি কেবল মনোযোগ বণ্টন করে। এটি কোনো কাজ, সংস্থা বা ব্যক্তির বিরুদ্ধে কিছু "
            "দাবি করে না, এবং পরিকল্পনা একজন মানুষ অনুমোদন করেন।"
        ),
        "english_note": "বিবরণ ইংরেজিতে; সংখ্যা ও রেফারেন্স অপরিবর্তিত রাখা হয়েছে।",
    },
    "ta": {
        "brief": "ஏஜென்ட்ஃபோர்ஸ் விசாரணைச் சுருக்கம்",
        "location": "இடம் மற்றும் பொறுப்பு",
        "state": "மாநிலம் / தொகுதி",
        "agency": "செயல்படுத்தும் நிறுவனம்",
        "mp": "பரிந்துரைத்தவர்",
        "financial": "நிதி மற்றும் இடர் மதிப்பீடு",
        "recommended": "பரிந்துரைக்கப்பட்ட ஒப்புதல்",
        "exposure": "இடரில் உள்ள தொகை",
        "confidence": "நம்பகத்தன்மை நிலை",
        "families": "தனித்த சமிக்ஞைக் குழுக்கள்",
        "casework": "சேல்ஸ்ஃபோர்ஸ் வழக்கு மற்றும் நிலை",
        "stage": "தற்போதைய விசாரணை நிலை",
        "tier": "மேல்முறையீட்டு நிலை",
        "review_by": "மறுஆய்வு இலக்கு நாள்",
        "guidance": "இந்த நிலையில் அலுவலருக்கான வழிகாட்டுதல்",
        "evidence": "உறுதிப்படுத்தும் சான்றுகள்",
        "next_step": "பரிந்துரைக்கப்பட்ட அடுத்த படி",
        "audit_plan": "ஏஜென்ட்ஃபோர்ஸ் தணிக்கைத் திட்டம்",
        "auditor_days": "தணிக்கையாளர்-நாட்கள்",
        "what_it_buys": "இந்த நிதியில் கிடைப்பது",
        "works": "பணிகள்",
        "visits": "நிறுவன வருகைகள்",
        "in_states": "மாநிலங்களில்",
        "covered": "இடர்த் தொகை உள்ளடக்கப்பட்டது",
        "no_extra_travel": "பணிகளுக்கு கூடுதல் பயணச் செலவு இல்லை",
        "start_here": "இங்கிருந்து தொடங்குங்கள்",
        "same_trip": "அதே பயணத்தில்",
        "casework_status": "ஏஜென்ட்ஃபோர்ஸ் வழக்கு நிலை",
        "cases_loaded": "விசாரணை வழக்குகள் சேல்ஸ்ஃபோர்ஸில் உள்ளன",
        "not_yet_seen": "இதுவரை யாரும் பார்க்கவில்லை",
        "contract": (
            "இது சான்றுகளுடன் கூடிய விசாரணைத் தடயம். இது மோசடி அல்லது முறைகேடு என்ற "
            "முடிவு அல்ல. சான்றுகளை ஆய்ந்து ஒரு மனிதர் முடிவு எடுக்கிறார்."
        ),
        "plan_contract": (
            "இது கவனத்தை ஒதுக்குகிறது. எந்தப் பணி, நிறுவனம் அல்லது நபர் மீதும் குற்றம் "
            "சாட்டவில்லை; திட்டத்தை ஒரு மனிதர் ஒப்புதல் அளிக்கிறார்."
        ),
        "english_note": "விவரங்கள் ஆங்கிலத்தில்; எண்களும் குறிப்புகளும் மாற்றப்படவில்லை.",
    },
    "te": {
        "brief": "ఏజెంట్‌ఫోర్స్ దర్యాప్తు సారాంశం",
        "location": "ప్రదేశం మరియు బాధ్యత",
        "state": "రాష్ట్రం / నియోజకవర్గం",
        "agency": "అమలు సంస్థ",
        "mp": "సిఫారసు చేసినవారు",
        "financial": "ఆర్థిక మరియు ప్రమాద అంచనా",
        "recommended": "సిఫారసు చేసిన మంజూరు",
        "exposure": "ప్రమాదంలో ఉన్న మొత్తం",
        "confidence": "విశ్వాస స్థాయి",
        "families": "స్వతంత్ర సంకేత వర్గాలు",
        "casework": "సేల్స్‌ఫోర్స్ కేసు మరియు దశ",
        "stage": "ప్రస్తుత దర్యాప్తు దశ",
        "tier": "ఉన్నత స్థాయి",
        "review_by": "సమీక్ష లక్ష్య తేదీ",
        "guidance": "ఈ దశలో అధికారికి మార్గదర్శకం",
        "evidence": "ధృవీకరించే ఆధారాలు",
        "next_step": "సిఫారసు చేసిన తదుపరి చర్య",
        "audit_plan": "ఏజెంట్‌ఫోర్స్ ఆడిట్ ప్రణాళిక",
        "auditor_days": "ఆడిటర్-రోజులు",
        "what_it_buys": "ఈ బడ్జెట్‌తో లభించేది",
        "works": "పనులు",
        "visits": "సంస్థ సందర్శనలు",
        "in_states": "రాష్ట్రాలలో",
        "covered": "ప్రమాద మొత్తం కవర్ చేయబడింది",
        "no_extra_travel": "పనులకు అదనపు ప్రయాణ ఖర్చు లేదు",
        "start_here": "ఇక్కడ నుండి ప్రారంభించండి",
        "same_trip": "అదే పర్యటనలో",
        "casework_status": "ఏజెంట్‌ఫోర్స్ కేసు స్థితి",
        "cases_loaded": "దర్యాప్తు కేసులు సేల్స్‌ఫోర్స్‌లో ఉన్నాయి",
        "not_yet_seen": "ఇంకా ఎవరూ చూడలేదు",
        "contract": (
            "ఇది ఆధారాలతో కూడిన దర్యాప్తు సూచన. ఇది మోసం లేదా అక్రమం అనే నిర్ధారణ కాదు. "
            "ఆధారాలను సమీక్షించి ఒక వ్యక్తి నిర్ణయిస్తారు."
        ),
        "plan_contract": (
            "ఇది శ్రద్ధను కేటాయిస్తుంది. ఏ పని, సంస్థ లేదా వ్యక్తిపైనా ఆరోపణ చేయదు; "
            "ప్రణాళికను ఒక వ్యక్తి ఆమోదిస్తారు."
        ),
        "english_note": "వివరాలు ఆంగ్లంలో; సంఖ్యలు, సూచనలు యథాతథంగా ఉంచబడ్డాయి.",
    },
    "mr": {
        "brief": "एजंटफोर्स तपास सारांश",
        "location": "स्थान व जबाबदारी",
        "state": "राज्य / मतदारसंघ",
        "agency": "अंमलबजावणी संस्था",
        "mp": "शिफारस करणारे",
        "financial": "आर्थिक व जोखीम मूल्यांकन",
        "recommended": "शिफारस केलेली मंजुरी",
        "exposure": "जोखमीतील रक्कम",
        "confidence": "विश्वास श्रेणी",
        "families": "स्वतंत्र संकेत श्रेणी",
        "casework": "सेल्सफोर्स प्रकरण व टप्पा",
        "stage": "सध्याचा तपास टप्पा",
        "tier": "वरिष्ठ स्तर",
        "review_by": "पुनरावलोकन लक्ष्य दिनांक",
        "guidance": "या टप्प्यावर अधिकाऱ्यासाठी मार्गदर्शन",
        "evidence": "पुष्टी करणारे पुरावे",
        "next_step": "शिफारस केलेले पुढील पाऊल",
        "audit_plan": "एजंटफोर्स लेखापरीक्षण योजना",
        "auditor_days": "लेखापरीक्षक-दिवस",
        "what_it_buys": "या अर्थसंकल्पातून काय मिळते",
        "works": "कामे",
        "visits": "संस्था भेटी",
        "in_states": "राज्यांमध्ये",
        "covered": "जोखमीची रक्कम समाविष्ट",
        "no_extra_travel": "कामांसाठी अतिरिक्त प्रवास खर्च नाही",
        "start_here": "येथून सुरुवात करा",
        "same_trip": "त्याच दौऱ्यात",
        "casework_status": "एजंटफोर्स प्रकरण स्थिती",
        "cases_loaded": "तपास प्रकरणे सेल्सफोर्समध्ये आहेत",
        "not_yet_seen": "अद्याप कोणीही पाहिलेली नाहीत",
        "contract": (
            "हा पुराव्यांसह तपास संकेत आहे. हा फसवणूक किंवा गैरप्रकाराचा निष्कर्ष नाही. "
            "पुराव्यांचे पुनरावलोकन करून एक व्यक्ती निर्णय घेते."
        ),
        "plan_contract": (
            "हे केवळ लक्ष वाटप करते. कोणत्याही कामावर, संस्थेवर किंवा व्यक्तीवर आरोप करत "
            "नाही, आणि योजनेला एक व्यक्ती मान्यता देते."
        ),
        "english_note": "तपशील इंग्रजीत; आकडे व संदर्भ जसेच्या तसे ठेवले आहेत.",
    },
    "gu": {
        "brief": "એજન્ટફોર્સ તપાસ સારાંશ",
        "location": "સ્થાન અને જવાબદારી",
        "state": "રાજ્ય / મતવિસ્તાર",
        "agency": "અમલીકરણ સંસ્થા",
        "mp": "ભલામણ કરનાર",
        "financial": "નાણાકીય અને જોખમ મૂલ્યાંકન",
        "recommended": "ભલામણ કરેલ મંજૂરી",
        "exposure": "જોખમમાં રહેલી રકમ",
        "confidence": "વિશ્વાસ શ્રેણી",
        "families": "સ્વતંત્ર સંકેત શ્રેણીઓ",
        "casework": "સેલ્સફોર્સ કેસ અને તબક્કો",
        "stage": "વર્તમાન તપાસ તબક્કો",
        "tier": "ઉચ્ચ સ્તર",
        "review_by": "સમીક્ષા લક્ષ્ય તારીખ",
        "guidance": "આ તબક્કે અધિકારી માટે માર્ગદર્શન",
        "evidence": "પુષ્ટિ કરતા પુરાવા",
        "next_step": "ભલામણ કરેલ આગળનું પગલું",
        "audit_plan": "એજન્ટફોર્સ ઓડિટ યોજના",
        "auditor_days": "ઓડિટર-દિવસ",
        "what_it_buys": "આ બજેટમાં શું મળે છે",
        "works": "કામો",
        "visits": "સંસ્થા મુલાકાતો",
        "in_states": "રાજ્યોમાં",
        "covered": "જોખમની રકમ આવરી લેવાઈ",
        "no_extra_travel": "કામો માટે વધારાનો પ્રવાસ ખર્ચ નથી",
        "start_here": "અહીંથી શરૂ કરો",
        "same_trip": "એ જ પ્રવાસમાં",
        "casework_status": "એજન્ટફોર્સ કેસ સ્થિતિ",
        "cases_loaded": "તપાસ કેસ સેલ્સફોર્સમાં છે",
        "not_yet_seen": "હજુ સુધી કોઈએ જોયા નથી",
        "contract": (
            "આ પુરાવા સાથેનો તપાસ સંકેત છે. આ છેતરપિંડી કે ગેરરીતિનો નિષ્કર્ષ નથી. "
            "પુરાવાની સમીક્ષા કરીને એક વ્યક્તિ નિર્ણય લે છે."
        ),
        "plan_contract": (
            "આ માત્ર ધ્યાન ફાળવે છે. કોઈ કામ, સંસ્થા કે વ્યક્તિ પર આરોપ મૂકતું નથી, અને "
            "યોજનાને એક વ્યક્તિ મંજૂરી આપે છે."
        ),
        "english_note": "વિગતો અંગ્રેજીમાં; આંકડા અને સંદર્ભ યથાવત રાખ્યા છે.",
    },
    "kn": {
        "brief": "ಏಜೆಂಟ್‌ಫೋರ್ಸ್ ತನಿಖಾ ಸಾರಾಂಶ",
        "location": "ಸ್ಥಳ ಮತ್ತು ಜವಾಬ್ದಾರಿ",
        "state": "ರಾಜ್ಯ / ಕ್ಷೇತ್ರ",
        "agency": "ಅನುಷ್ಠಾನ ಸಂಸ್ಥೆ",
        "mp": "ಶಿಫಾರಸು ಮಾಡಿದವರು",
        "financial": "ಆರ್ಥಿಕ ಮತ್ತು ಅಪಾಯ ಮೌಲ್ಯಮಾಪನ",
        "recommended": "ಶಿಫಾರಸು ಮಾಡಿದ ಮಂಜೂರಾತಿ",
        "exposure": "ಅಪಾಯದಲ್ಲಿರುವ ಮೊತ್ತ",
        "confidence": "ವಿಶ್ವಾಸ ಶ್ರೇಣಿ",
        "families": "ಸ್ವತಂತ್ರ ಸಂಕೇತ ವರ್ಗಗಳು",
        "casework": "ಸೇಲ್ಸ್‌ಫೋರ್ಸ್ ಪ್ರಕರಣ ಮತ್ತು ಹಂತ",
        "stage": "ಪ್ರಸ್ತುತ ತನಿಖಾ ಹಂತ",
        "tier": "ಉನ್ನತ ಮಟ್ಟ",
        "review_by": "ಪರಿಶೀಲನೆ ಗುರಿ ದಿನಾಂಕ",
        "guidance": "ಈ ಹಂತದಲ್ಲಿ ಅಧಿಕಾರಿಗೆ ಮಾರ್ಗದರ್ಶನ",
        "evidence": "ದೃಢೀಕರಿಸುವ ಸಾಕ್ಷ್ಯ",
        "next_step": "ಶಿಫಾರಸು ಮಾಡಿದ ಮುಂದಿನ ಹೆಜ್ಜೆ",
        "audit_plan": "ಏಜೆಂಟ್‌ಫೋರ್ಸ್ ಲೆಕ್ಕಪರಿಶೋಧನಾ ಯೋಜನೆ",
        "auditor_days": "ಲೆಕ್ಕಪರಿಶೋಧಕ-ದಿನಗಳು",
        "what_it_buys": "ಈ ಬಜೆಟ್‌ನಿಂದ ಸಿಗುವುದು",
        "works": "ಕಾಮಗಾರಿಗಳು",
        "visits": "ಸಂಸ್ಥೆ ಭೇಟಿಗಳು",
        "in_states": "ರಾಜ್ಯಗಳಲ್ಲಿ",
        "covered": "ಅಪಾಯದ ಮೊತ್ತ ಒಳಗೊಂಡಿದೆ",
        "no_extra_travel": "ಕಾಮಗಾರಿಗಳಿಗೆ ಹೆಚ್ಚುವರಿ ಪ್ರಯಾಣ ವೆಚ್ಚವಿಲ್ಲ",
        "start_here": "ಇಲ್ಲಿಂದ ಪ್ರಾರಂಭಿಸಿ",
        "same_trip": "ಅದೇ ಪ್ರವಾಸದಲ್ಲಿ",
        "casework_status": "ಏಜೆಂಟ್‌ಫೋರ್ಸ್ ಪ್ರಕರಣ ಸ್ಥಿತಿ",
        "cases_loaded": "ತನಿಖಾ ಪ್ರಕರಣಗಳು ಸೇಲ್ಸ್‌ಫೋರ್ಸ್‌ನಲ್ಲಿವೆ",
        "not_yet_seen": "ಇನ್ನೂ ಯಾರೂ ನೋಡಿಲ್ಲ",
        "contract": (
            "ಇದು ಸಾಕ್ಷ್ಯ ಸಹಿತ ತನಿಖಾ ಸುಳಿವು. ಇದು ವಂಚನೆ ಅಥವಾ ಅಕ್ರಮದ ತೀರ್ಮಾನವಲ್ಲ. "
            "ಸಾಕ್ಷ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ ಒಬ್ಬ ವ್ಯಕ್ತಿ ನಿರ್ಧರಿಸುತ್ತಾರೆ."
        ),
        "plan_contract": (
            "ಇದು ಗಮನವನ್ನು ಹಂಚುತ್ತದೆ. ಯಾವುದೇ ಕಾಮಗಾರಿ, ಸಂಸ್ಥೆ ಅಥವಾ ವ್ಯಕ್ತಿಯ ಮೇಲೆ ಆರೋಪ "
            "ಮಾಡುವುದಿಲ್ಲ, ಮತ್ತು ಯೋಜನೆಯನ್ನು ಒಬ್ಬ ವ್ಯಕ್ತಿ ಅನುಮೋದಿಸುತ್ತಾರೆ."
        ),
        "english_note": "ವಿವರಗಳು ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ; ಸಂಖ್ಯೆಗಳು ಮತ್ತು ಉಲ್ಲೇಖಗಳು ಯಥಾವತ್ತಾಗಿವೆ.",
    },
    "ml": {
        "brief": "ഏജന്റ്ഫോഴ്സ് അന്വേഷണ സംഗ്രഹം",
        "location": "സ്ഥലവും ഉത്തരവാദിത്വവും",
        "state": "സംസ്ഥാനം / മണ്ഡലം",
        "agency": "നിർവഹണ ഏജൻസി",
        "mp": "ശുപാർശ ചെയ്തത്",
        "financial": "സാമ്പത്തിക, അപകടസാധ്യത വിലയിരുത്തൽ",
        "recommended": "ശുപാർശ ചെയ്ത അനുമതി",
        "exposure": "അപകടസാധ്യതയിലുള്ള തുക",
        "confidence": "വിശ്വാസ്യതാ നില",
        "families": "സ്വതന്ത്ര സൂചനാ വിഭാഗങ്ങൾ",
        "casework": "സെയിൽസ്ഫോഴ്സ് കേസും ഘട്ടവും",
        "stage": "നിലവിലെ അന്വേഷണ ഘട്ടം",
        "tier": "ഉയർന്ന തലം",
        "review_by": "അവലോകന ലക്ഷ്യ തീയതി",
        "guidance": "ഈ ഘട്ടത്തിൽ ഉദ്യോഗസ്ഥനുള്ള മാർഗനിർദേശം",
        "evidence": "സ്ഥിരീകരിക്കുന്ന തെളിവുകൾ",
        "next_step": "ശുപാർശ ചെയ്ത അടുത്ത നടപടി",
        "audit_plan": "ഏജന്റ്ഫോഴ്സ് ഓഡിറ്റ് പദ്ധതി",
        "auditor_days": "ഓഡിറ്റർ-ദിവസങ്ങൾ",
        "what_it_buys": "ഈ ബജറ്റിൽ ലഭിക്കുന്നത്",
        "works": "പ്രവൃത്തികൾ",
        "visits": "ഏജൻസി സന്ദർശനങ്ങൾ",
        "in_states": "സംസ്ഥാനങ്ങളിൽ",
        "covered": "അപകടസാധ്യത തുക ഉൾപ്പെടുത്തി",
        "no_extra_travel": "പ്രവൃത്തികൾക്ക് അധിക യാത്രാച്ചെലവില്ല",
        "start_here": "ഇവിടെ നിന്ന് തുടങ്ങുക",
        "same_trip": "അതേ യാത്രയിൽ",
        "casework_status": "ഏജന്റ്ഫോഴ്സ് കേസ് നില",
        "cases_loaded": "അന്വേഷണ കേസുകൾ സെയിൽസ്ഫോഴ്സിൽ ഉണ്ട്",
        "not_yet_seen": "ഇതുവരെ ആരും കണ്ടിട്ടില്ല",
        "contract": (
            "ഇത് തെളിവുകളോടു കൂടിയ അന്വേഷണ സൂചനയാണ്. ഇത് വഞ്ചനയുടെയോ ക്രമക്കേടിന്റെയോ "
            "നിഗമനമല്ല. തെളിവുകൾ പരിശോധിച്ച് ഒരു മനുഷ്യൻ തീരുമാനിക്കുന്നു."
        ),
        "plan_contract": (
            "ഇത് ശ്രദ്ധ വിനിയോഗിക്കുന്നു. ഒരു പ്രവൃത്തിക്കോ ഏജൻസിക്കോ വ്യക്തിക്കോ എതിരെ "
            "ആരോപണം ഉന്നയിക്കുന്നില്ല; പദ്ധതി ഒരു മനുഷ്യൻ അംഗീകരിക്കുന്നു."
        ),
        "english_note": "വിശദാംശങ്ങൾ ഇംഗ്ലീഷിൽ; സംഖ്യകളും റഫറൻസുകളും മാറ്റിയിട്ടില്ല.",
    },
    "pa": {
        "brief": "ਏਜੰਟਫੋਰਸ ਜਾਂਚ ਸਾਰ",
        "location": "ਸਥਾਨ ਅਤੇ ਜ਼ਿੰਮੇਵਾਰੀ",
        "state": "ਰਾਜ / ਹਲਕਾ",
        "agency": "ਲਾਗੂ ਕਰਨ ਵਾਲੀ ਸੰਸਥਾ",
        "mp": "ਸਿਫ਼ਾਰਸ਼ ਕਰਨ ਵਾਲੇ",
        "financial": "ਵਿੱਤੀ ਅਤੇ ਜੋਖਮ ਮੁਲਾਂਕਣ",
        "recommended": "ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀ ਮਨਜ਼ੂਰੀ",
        "exposure": "ਜੋਖਮ ਵਿੱਚ ਰਕਮ",
        "confidence": "ਭਰੋਸਾ ਸ਼੍ਰੇਣੀ",
        "families": "ਸੁਤੰਤਰ ਸੰਕੇਤ ਸ਼੍ਰੇਣੀਆਂ",
        "casework": "ਸੇਲਜ਼ਫੋਰਸ ਕੇਸ ਅਤੇ ਪੜਾਅ",
        "stage": "ਮੌਜੂਦਾ ਜਾਂਚ ਪੜਾਅ",
        "tier": "ਉੱਚ ਪੱਧਰ",
        "review_by": "ਸਮੀਖਿਆ ਟੀਚਾ ਮਿਤੀ",
        "guidance": "ਇਸ ਪੜਾਅ ਉੱਤੇ ਅਧਿਕਾਰੀ ਲਈ ਸੇਧ",
        "evidence": "ਪੁਸ਼ਟੀ ਕਰਨ ਵਾਲੇ ਸਬੂਤ",
        "next_step": "ਸਿਫ਼ਾਰਸ਼ ਕੀਤਾ ਅਗਲਾ ਕਦਮ",
        "audit_plan": "ਏਜੰਟਫੋਰਸ ਆਡਿਟ ਯੋਜਨਾ",
        "auditor_days": "ਆਡੀਟਰ-ਦਿਨ",
        "what_it_buys": "ਇਸ ਬਜਟ ਨਾਲ ਕੀ ਮਿਲਦਾ ਹੈ",
        "works": "ਕੰਮ",
        "visits": "ਸੰਸਥਾ ਦੌਰੇ",
        "in_states": "ਰਾਜਾਂ ਵਿੱਚ",
        "covered": "ਜੋਖਮ ਰਕਮ ਸ਼ਾਮਲ",
        "no_extra_travel": "ਕੰਮਾਂ ਲਈ ਵਾਧੂ ਸਫ਼ਰ ਖਰਚ ਨਹੀਂ",
        "start_here": "ਇੱਥੋਂ ਸ਼ੁਰੂ ਕਰੋ",
        "same_trip": "ਉਸੇ ਦੌਰੇ ਵਿੱਚ",
        "casework_status": "ਏਜੰਟਫੋਰਸ ਕੇਸ ਸਥਿਤੀ",
        "cases_loaded": "ਜਾਂਚ ਕੇਸ ਸੇਲਜ਼ਫੋਰਸ ਵਿੱਚ ਹਨ",
        "not_yet_seen": "ਹਾਲੇ ਤੱਕ ਕਿਸੇ ਨੇ ਨਹੀਂ ਵੇਖੇ",
        "contract": (
            "ਇਹ ਸਬੂਤਾਂ ਸਹਿਤ ਜਾਂਚ ਸੰਕੇਤ ਹੈ। ਇਹ ਧੋਖਾਧੜੀ ਜਾਂ ਬੇਨਿਯਮੀ ਦਾ ਨਤੀਜਾ ਨਹੀਂ ਹੈ। "
            "ਸਬੂਤਾਂ ਦੀ ਸਮੀਖਿਆ ਕਰਕੇ ਇੱਕ ਵਿਅਕਤੀ ਫ਼ੈਸਲਾ ਕਰਦਾ ਹੈ।"
        ),
        "plan_contract": (
            "ਇਹ ਸਿਰਫ਼ ਧਿਆਨ ਵੰਡਦਾ ਹੈ। ਇਹ ਕਿਸੇ ਕੰਮ, ਸੰਸਥਾ ਜਾਂ ਵਿਅਕਤੀ ਉੱਤੇ ਦੋਸ਼ ਨਹੀਂ ਲਾਉਂਦਾ, "
            "ਅਤੇ ਯੋਜਨਾ ਨੂੰ ਇੱਕ ਵਿਅਕਤੀ ਮਨਜ਼ੂਰੀ ਦਿੰਦਾ ਹੈ।"
        ),
        "english_note": "ਵੇਰਵੇ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ; ਅੰਕੜੇ ਅਤੇ ਹਵਾਲੇ ਉਵੇਂ ਹੀ ਰੱਖੇ ਗਏ ਹਨ।",
    },
}


def phrase(key: str, lang: str = "en") -> str:
    """One phrase in the requested language, falling back to English.

    Falls back rather than raising: a missing phrase should degrade one label, not take
    down an officer's answer.
    """
    bundle = PHRASES.get(lang) or PHRASES["en"]
    return bundle.get(key) or PHRASES["en"].get(key, key)


def bundle(lang: str = "en") -> dict[str, str]:
    """The whole phrase set for one language, English-completed."""
    merged = dict(PHRASES["en"])
    merged.update(PHRASES.get(lang, {}))
    return merged


def supported() -> list[str]:
    return sorted(PHRASES)


def coverage(lang: str) -> float:
    """What share of the English phrases this language actually defines."""
    english = PHRASES["en"]
    target = PHRASES.get(lang, {})
    filled = sum(1 for key in english if target.get(key))
    return round(filled / len(english), 3) if english else 0.0
