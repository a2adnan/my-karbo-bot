import asyncio
import random
import requests
import json
import os
import traceback
from karbo import KarboBot, KarboBotWS

BOT_TOKEN = "9588878f62c6d982f37c79730ca11bcb8725ad20c19f6d869c834b9e7e206c191e70ee72b718e5a158e0587f0bfccc79b8f0f9c59edf4e85dc3b5f6ac99351b4"

bot = KarboBot(BOT_TOKEN)
ws = KarboBotWS(BOT_TOKEN)

# الذاكرة المحلية والبيانات ونظام التتبع العكسي الذكي
PROCESSED_MESSAGE_IDS = set()
PROCESSED_SYSTEM_IDS = set() # 🛡️ ذاكرة مستقلة حاسمة لمنع سبام وتكرار الترحيب والمغادرة
CATCHED_MESSAGES = []       # مصفوفة التتبع العكسي لآيديات الرسائل
CURRENT_CHAT_ID = None
LAST_MESSAGE_ID = None

# إعدادات الإدارة والتحكم الذكي مالت حجي عدنان
BOT_PHOTO_WAITING = False
MARK_READ_STATUS = "on"
LOG_GROUPS = set()
MUTED_USERS = set()      # لستة المكتومين بالجروب
ALLOWED_USERS = set()    # القائمة البيضاء: الأشخاص المسموح لهم باستخدام البوت عند القفل
BOT_LOCKED = False       # حالة قفل البوت العام عن المجموعة
USER_SPAM = {}
USER_WARNINGS = {}

BAD_WORDS = [
    "كسم",
    "كس",
    "كص",
    "زب",
    "منيوك",
    "قحبة",
    "كحبة",
    "شرموطة",
    "عرص",
    "متناك",
    "ابن الكلب",
    "ابن كلب",
    "حيوان",
    "خرا",
    "تفو",
    "يلعن",
    "لعنة"
    "كسكم"
    "بكسكم"
    "شريفه"
    "عاهره"
]

# بنك عدادات الأعضاء والفعاليات
MESSAGE_COUNT_STATS = {} 
USER_POINTS = {}          
USER_NICKNAMES = {}       
CURRENT_QUIZ = {
    "question": None,
    "answer": None,
    "active": False
}

ATHKAR_BANK = [
    "🌿 تذكير تلقائي: سبحان الله وبحمده، سبحان الله العظيم. ✨",
    "✨ تذكير تلقائي: اللهم صلِّ وسلم وبارك على نبينا محمد وعلى آله وصحبه أجمعين. ❤️",
    "🌿 تذكير تلقائي: لا إله إلا أنت سبحانك إني كنت من الظالمين. 💎",
    "✨ تذكير تلقائي: استغفر الله العظيم وأتوب إليه. 🌿",
    "🌿 تذكير تلقائي: لا حول ولا قوة إلا بالله العلي العظيم. ⚡"
]

MATCH_SCENARIOS = [
    "المباراة راح تنتهي بنتيجة مدوية 3 - 1 لصالح {team1}! 🔥 {team1} راح يسيطرون بالملعب والهدف الأول يجي بالدقيقة 15 يجلط الحارس!",
    "توقعي الصارم هو تعادل إيجابي قاتل 2 - 2! ⚽ جولة حماسية وأهداف بآخر الدقائق تقلب الموازين غصباً على السيرفر الحين!",
    "راح تنتهي 2 - 0 بفوز ساحق لـ {team1}! 😎 دفاع حديدي مستحيل يعبر منه مهاجم {team2}، وصاحب الهدف الأول راح يفجر الروم حماس الحين!",
    "صدمة كبيرة بالملعب! {team2} راح يفجرها ويفوز بنتيجة 1 - 0 بضربة جزاء مثيرة للجدل بالدقيقة 90! 😱"
]

FORTUNES = [
    "حظك اليوم 95%! 😍 اكو عضو بالجروب جاي يراقبك ويحبك بالسر، شيك قائمة الصدارة الحين!",
    "حظك اليوم 40%! 🌚 اليوم وضعك كولش تعبان، انصحك تروح تشرب استكان شاي وتطفي المبردة.",
    "حظك اليوم 88%! 🔥 راح تجيك نقاط مجانية قريباً بالفعاليات، خليك منتبه ومفتح باللبن.",
    "حظك اليوم 15%! 😭 اليوم السحكات مالتك راح توصل للستار، التزم الصمت أحسن الك الحين.",
    "حظك اليوم 70%! 👍 وضعك مستقر بجروب الأنمي، بس تحتاج تغير الزخرفة مالت اسمك لتجذب الانتباه.",
    "حظك اليوم 100%! 👑 أنت ملك الروم اليوم، وبكلمة منك تكدر تشعل الشات تفاعل وحماس!"
]

ARABIC_QUIZ_BANK = [
    {"q": "من هو صاحب رتبة قبعة القش في أنمي ون بيس؟", "a": "لوفي"},
    {"q": "ما اسم الأنمي الذي يحتوي على مفكرة الموت؟", "a": "ديث نوت"},
    {"q": "من هو قاتل الشياطين صاحب التنفس الشمسي؟", "a": "تانجيرو"},
    {"q": "ما اسم والد ناروتو؟", "a": "ميناتو"},
    {"q": "أنمي مشهور عن قتال العمالقة الجدران، ما اسمه؟", "a": "هجوم العمالقة"},
    {"q": "شيء يتكلم جميع اللغات ولكنه بلا لسان، ما هو؟", "a": "الصدى"},
    {"q": "ما هو الشيء الذي كلما أخذت منه كبر؟", "a": "الحفرة"},
    {"q": "من هو قائد الفرسان في أنمي هجوم العمالقة؟", "a": "ليفاي"},
    {"q": "ما هو أسرع كائن حي على وجه الأرض؟", "a": "الفهد"},
    {"q": "كائن يرى بأذنيه، ما هو؟", "a": "الخفاش"},
    {"q": "من هو أخو لوفي وسابو بالتبني？", "a": "ايس"},
    {"q": "ما هو الشيء الذي يقرأ ويكتب ولكنه لا يرى؟", "a": "القلم"}
]

AUTO_REPLIES = {
    "هلاو": "هلاوو99وووات نورت/ي ❤️🙈", "هلو": "هلاوات 🙈❤️", "شلونكم": "الحمدلله وانته 🌚🍃",
    "دووم": "يدوم نبضك ❤️🍃", "شونك": "الحمدلله وانته", "شلونك": "الحمدلله وانته",
    "غنيلي": " قنيتلك قنية وعش ماجيت يلقالي 🌝😹", "شغل المبردة": " تم تشغيل المبردة بنجاح ❄️",
    "طفي المبردة": "طفيتهه 😒🍃", "شغل السبلت": "شغلته 🌚🍃 بس حثلجون معليه ترا ",
    "مايا خليفه": " 😂 عيب صايمين", "فطور": "واخيراً 😍😍 خل اروح افطر ",
    "الزمة الية": "شرد شرد مراح تلحك بيه  ", "شيخ": " ❤️هلا يروح الشيخ هلا يعمري جعل محد يصيحني غيرك  ",
    "تخليني": "🌞🔺عيب منا العالم تعال وره 12 نايمين واشتغلك 🌝✋🏿",
    "زاحف": "ارتقي شوي شوكت تكبر 🌝🍃", "تركيا": "😐🍃 فديتهه", "عدنان": "هذا الي صنعني فديت ربه 🙈❤️",
    "الدولة الاسلامية": "انته داعشي ؟؟ 😒💔", "سني": "لتصير طائفي 😒🖐", "شيعي": "لتصير طائفي 😕",
    "تبادل": "عزيزي هےـِذٌٱ مو قروب تبادل 😕✋🏿 ", "العراقيين": "احلى ناس ولله 😍🙈", "من وين": "من قلبك ❤️  ",
    "هاي": "هاي حليـــــــب وويا هيل همينه وشكر زايد😹💔", "البوت": "معاجبك ؟ 😕😒🍃", "البوت واكف": "لتجذب 😒",
    "منو ديحذف رسائلي": "محد 😐🍃", "كلاش اوف كلانس": "تلعبهه ؟ شكد لفلك ؟", "جوني": "😂 مأذيك ؟",
    "ازحف": " ركبك تكشمن يول  🌚🍃 ", "محمد": " شتريد منه ؟ ", "منتظر": " شتريد منه ؟ ",
    "اسماعيل": " عم الكل الاسطورة اسماعيل ", "كرار": "هذا الوكيل دندوش القلب هذا ", "اشور": " الـحـب والـحـرب ",
    "ابراهيم": " شتريد منه ؟ ", "فرح": " امـيرة قـروب الـنـخـبة ❤️", "المدرسه": " 😒🍃 الله لا يراوينه ",
    "تحبني": " اموت عليك 🙊", "يعني شكد": " فوك متتوقع ", "😂": " دوم حبي ❤️", "هههه": " دوم حبي ❤️",
    "ههههه": " دوم حبي ❤️", "😹": " دوم حبي ❤️", "🌚": " منور صخام الجدر 🌚🍃", "😍": " مح فديتك",
    "مح": "😻وووفف جـعـل محد يبوس غيرك 😻", "المطور": "  هذا حسابه\nhttps://karboai.com/user/ims2t 🙈❤️",
    "منحرف": " وينه حطرده 🌚🌚", "😭": " 😢😢 لتبجي", "😢": " لتبجي 😭😭", "شكد عمرك": "الاعمار بيد الله ",
    "شكد عمرج": " انته شعلييييييك", "اقرالي دعاء": " اللهم عذب المدرسين 😢 منهم الاحياء والاموات 😭🔥 اللهم عذب ام الانكليزي 😭💔 وكهربها بلتيار الرئيسي 😇 اللهم عذب ام الرياضيات وحولها الى غساله بطانيات 🙊 اللهم عذب ام الاسلاميه واجعلها بائعة الشاميه 😭🍃 اللهم عذب ام العربي وحولها الى بائعه البلبي اللهم عذب ام الجغرافيه واجعلها كلدجاجه الحافية اللهم عذب ام التاريخ وزحلقها بقشره من البطيخ وارسلها الى المريخ اللهم عذب ام الاحياء واجعلها كل مومياء اللهم عذب المعاون اقتله بلمدرسه بهاون 😂😂😂",
    "غبي": " انته الاغبى", "دي": "امشي ابوك بيها 🌝✋🏿", "منو حبيبك": " انـــتـه 🙈", "تكرهني": " يي 😈",
    "اكرهك": " بـس انـي اححـبـك😻😹✋🏿🍃", "الاعضميه": " احسن ناس وربي❤️", "الكرادة": " احسن ناس وربي❤️",
    "شارع فلسطين": " احسن ناس وربي❤️", "ببكن ملف": " دي تحلم 😒😒", "😇": " اته مو ملاك اته جهنم بنفسهه 😂",
    "😐": " شبيك صافن 😒🔥", "انجب": "😭😡انجبو انتو فوك محامي كروبكم 😡😭", "حارة": "يي كولش 😭🍃🔥",
    "خالتك": " راح اطردك لك 😒", "اطرد البوت": " راح ابقة احترمك❤️", "هه": " شدتحس", "شدتحس": " بالامان والاستقرار",
    "اكولك": " كول بعد عمري ❤️🍃", "اكلك": " قول ماقول لحد 😹✋🏿🍃", "بغداد": " 😍 فديتهه",
    "البصرة": " احسن ناس وربي❤️", "تركماني": " والنعم منك❤️", "منو ابوك": "😇😍👈عـدنـان ابــوي👉😍😇",
    "باي": " بايات ❤️🍃", "تنح": "عيب ابني 😒🍃", "جوعان": "تعال اكلني 😐😂", "عطشان": "روح اشرب مي",
    "0": "نــورتــو الــكـروب وشــعــشــعـتو 🍃", "☹️": "لضوج حبيبي 😢❤️🍃", "😔": " ليش الحلو ضايج ❤️🍃",
    "فرخ": "👑ترى اذا اطلعه بطولك واليكرم ابو اكرم👑", "كسمك": " تاك لوالدتك 🌝✋🏿", "نعال": " بوجهك 😐😂",
    "حروح اسبح": " واخيراً 😂", "حروح اغسل": " واخيراً 😂", "حروح اطب للحمام": " واخيراً 😂",
    "حبيبتي": " بخت كلها كبلت ✿بُْـﮩ❁ﮩـس↜ ٲني بقيت 💔🚶", "كبلت": " بخت كلها كبلت ✿بُْـﮩ❁ﮩـس↜ ٲني بقيت 💔🚶",
    "البوت عاوي": " مثل امڪ 🌝🍃", "منور": " بنورك حبي 😍🍷", "حفلش": " افلش راسك", "كردي": "والنعم منك ❤️",
    "طفي السبلت": " تم اطفاء السبلت بنجاح 🌚🍃", "🌝": "هه", "اذن المغرب": "استحرم 🌚🍃", "حلو": "انت الاحلى 🌚❤️",
    "احبك": " اني اكثر 😍🍃", "😑": " شبيك 🍃☹", "😒": "😐 شبيك كالب وجهك ", "منو تحب": "خالتك الشكرة",
    "اباجر العيد": "كل عام وانت بالف خير حبي 😇❤️", "فديت": "فداك الكون وماي العيون", "مضغوط": "دي انضغظ منك ؟ 😂😂",
    "fdiit": "فداك الكون وماي العيون", "فديتك": "فداك الكون وماي العيون", "فديتج": "فداك الكون وماي العيون", "شوف خاصك": "شدازله 😱😨",
    "تعال خاص": "شحسوون 😱", "تعالي خاص": "شحسوون 😱", "1": "😂روز الـغـبـية روز الـغـبـية غـبـية غبية 😂", "😎": "يلا عود انته فد نعال 😐🍃",
    "😱": "خير خوفتني 😨", "كحبه": "اختڪ", "بيش ساعة": "ما اعرف 🌚🍃", "🚶🏻": "خير 🌝",
    "منو اكثر واحد تحبه": "عـدنـان والـنـسوان", "نضوري": "الــحـب و الحـرب  ", "طاسه": "امك حلوة ورقاصه 💃🏻",
    "عشرين": "تاكل جدر خنين 😫", "صباح الخير": "صباح النور والسرور", "اربعة": "😂لحيه ابوك مربعه", "فارة": "😂دفترك كله صفارة",
    "ميتين": "😂فوك راسك قندرتين", "مات": "ابو الحمامات 🐦", "توفه": "ابو اللفه 🌯", "احترك": "🍾البو العرك",
    "غرك": "ابو العرك 🍾", "طار": "ابن الطيار", "ديسحك": "😂😂 هاي بعده", "لتسحك": "😐😂 وك",
    "اندرويد": "افشل نظام بلعالم 🌝🍷", "ios": "احسن نظام بلعالم🌚❤️", "ايفون": "فديتك اته والايفون 🌚🔥",
    "كلكسي": "فاشل اخرة نوع تلفون🔥☹", "سامسونك": "فاشل اخرة نوع تلفون🔥☹", "لتزحف": "وك اسف 🙁😔",
    "النخبة": "https://karboai.com/chat/k7tz4 هـذا قـروب الـنـخـبة نـورنا ياغالي ❤️",
    "النخبه": "https://karboai.com/chat/k7tz4 هـذا قـروب الـنـخـبة نـورنا ياغالي ❤️",
    "مصطفى": "اويلي يابه مصطفى الاسطورة وينه وينه", "عنان": "🙈❤️ هذا الي صنعني فديت ربه ",
    "منو اني": "انته احلى شي بحياتي ❤️🍃", "ابن الكلب": "لاتغلط على ابوي 🙁😿 انته ابن الكلب 🌝✋🏿",
    "انجب انته": "وك وك 😭😔", "حطردك": "اعصابك 😨 لتتهور", "مطور": "عدنان تلكاه بكروب النخبة ",
    "منو اكثر واحد تكرهه": "انته", "شباب": "نعم حبي 🌝❤️", "اته زلمه": "تعال لزمه 😐😂",
    "الاحد": "هذا اليوم نحس بلنسبه الي", "الاثنين": "يوم اجة بي ناس عزيزين وفقدت بي ناس هم ☹",
    "هلاوو": "هلاوات ❤️🍃", "اتفل": "خـۣۛـۣۛ﴿تۣۛـۣۛـفـۣۛـۣۛـہٰ୭ۭۢ💦﴾ـخـۣۛخــہۢ'ۦ✿⇣",
    "كواد": "هيه الكواده حلوه بس سمعتها خره 🙁😹✋🏿", "😌": "المطلوب ؟", "هلا": " هلاوات",
    "مرحبا": "مرحبتين 😍🍃", "اسِلام عليكم": "عليكم السلام  🌝🍃", "سلام عليكم": "عليكم السلام  🌝🍃",
    "السلام عليكم": "عليكم السلام 🌝🍃", "تسلم": "الله يسلمك 😍", "منو امك": "🙁😭ماعندي ام يتيم والله عااا😭🙁",
    "كرير": "هےـِذٌٱ الاثول صديق ابويه بس احبه 😻😹🍃", "كس": "امك",
    "الحب": "الحب!  ليس عندما تلعب بشعر حبيبتك!  الحب هو عندما تلعب بعقلها 😹✋🏿",
    "اخوي": "دود وخنافس سود كون بخصوتك ياعفن يجايف ياعر اخوتك 😹✋🏿", "ضوجه": "☹️اي ضوجه وماكو تكبيل وكذا تجي نطلع☹️",
    "يله": "😹اوكف خلي البس الحذاء  😹", "شنو رئيك بهذا": "😻صاك فديته لو اندل بيته 😻🙊",
    "شنو رئيك بهايه": "❤️🙈يومه فديت آلحاته ببكن حلق 😻😹", "🚶💔": "لماذا مقسور 🙁✋ثل",
    "غنيلي راب": "والمضروب بوري تلكا بالسعدون يسكُر بشارع وتـتـ بجي كُبدهأإ كٌبل اسبوع دكٌلها طأبع مأإ قطـت صأإحبهأإ تبجيُ وأإلمصرف عليهأإ قأإطع  أو هيـه اجرت نيجتهأإ من ينزل الأيفون ألـساأإبع وأإني ألمحدق تلكٌوني عفت أإلفيس ورحـت الجامع  مو مال انقط بهداية جيبي طاطا طيزه طالع ياوسفه خلوني للجامع ارب مو حته صابون ماعندي يعني رأس ماكدر أضرب أصلاً هل ليلة تلكوني ادشرب ويه العفطية وصاحبتي دوماًها زعلانه صاحبتي جنهأخفاش شو الي راح يطك هذي الليله الي عنده صيدليه  راح يصير واحد زنكيل هلكد ماحيبع فلاش يا عمو يابو الهداية صدكني الكحبه متوب  جيب أيفون أحسلك والله بعد مايفيد الدبدوب الزينه الي ماتناج من الزب تسوي سوب ولت أيام الخلاق كامن يدورن زبزو هابي فالنتاين بجز  👑 #Dev: https://karboai.com/chat/k7tz4",
    "كلخره": "اعذرني ما اكلك 🌝✋🏿", "كلخرا": "اعذرني ما اكلك 🌝✋🏿", "كلخراا": "اعذرني ما اكلك 🌝✋🏿",
    "وينكم": "نايمين بلخاص 24 ساعة 😹👉", "الوو": "ما اسمعك الشبكة ضعيفة 😕🍃", "الووو": "ما اسمعك الشبكة ضعيفه",
    "حيدر": "هےـِذٌٱ الاثول صديق ابويه بس احبه 😻😹🍃", "يلةة": "😹اوكف خلي افتح السحاب😹",
    "كس اختك": "وختك ويايه ع الواهس اختي تضوج وحدهة", "كسختك": "وختك ويايه ع الواهس اختي تضوج وحدهة",
    "تف": "عليك 🌝✋🏿", "اتفل ع عمك": "خخخخخخـتتتتتتتـ﴿💦﴾ـــففففففففففففففف",
    "بوس عمتك": "اووومحححححح 🙊", "جب": "اجب عليك 😹✋🏿", "☺️": "صدقه للخشول ❤️🙊",
    "🚶": "﴿ويۙـۧـﮩـﮯۙﻦ﴾ رايح نبض 🙁❤️🍃", "🌚🎈": "مدري ليش تعجبيني🙁✋🏿", "🌝🚶": "لو تمشي لو تبقة 🐸💔",
    "واتس": "اكتب يم اسمك ساحف 🐸💔", "🌝🌝": "عود ثكال 🐸💔",
    "خيو": "لَاَ تَكَولَيَ عَنَيَ خَيَيَ واَنَيَ شَيَبَ طَيَزَّيَ مَنَهَنَ مَولَجَلَ خَيَيَ وخَويَهَ اَنَهَ مَاَ اَسَتَنَكَفَ مَنَهَنَ اَلَسَواَلَفَ ذنَيَ عَيَبَ كَدَاَمَ اَلَرَبَعَ واَلَصَحَبَهَ يَعَنَيَ تَقَبَلَيَنَ يَكَولَونَ شيخ اَخَ كَحَبَه 🌝✋🏿",
    "احمد": "كله بالفراش امدد", "حسن": "24 ساعة يشرب لبن😹", "شبح": "شبح لو ظهر😹💔",
    "هاني": "هاني واخوتي واهلي كلهم😹✋🏿", "سامر": "سامر روحه من السطح😹✋🏿", "شعبان": "شعبان وبعد مااكدر😹😹",
    "نوح": "نوح وتعال😹✋🏿", "شكر": "شكر وعربده واعتداء على المواطنين🙁💔", "تعال": "تعال ابو الاصبع",
    "اثير": "أثير بحرب إيران😹✋🏿", "اه":" وجـعـا", "آه": "وجــعــاااا",
    "عيد الحب": "هذي الليله عيد الكفار واذا بنحدق انهز الزار بنكضيهأإ شرب بالبأر نضرب اوزو بصحت الكٌحبه😹💔"
}

def get_online_horoscope(sign_name):
    mapping = {
        "الحمل": "aries", "الثور": "taurus", "الجوزاء": "gemini", 
        "السرطان": "cancer", "الأسد": "leo", "العذراء": "virgo",
        "الميزان": "libra", "العقرب": "scorpio", "القوس": "sagittarius",
        "الجدي": "capricorn", "الدلو": "aquarius", "الحوت": "pisces"
    }
    en_sign = mapping.get(sign_name)
    if not en_sign: return None
    try:
        res = requests.get(f"https://horoscope-app-api.vercel.app/api/v1/horoscope/today/?sign={en_sign}", timeout=5)
        if res.status_code == 200:
            data = res.json()
            horoscope_text = data.get("data", {}).get("horoscope_data", "")
            if horoscope_text:
                return f"🔮 توقعات برجك الحية لليوم من الإنترنت:\n> {horoscope_text}\n\n🔥 طاقة اليوم متغيرة، تفاعل بالروم وصعد واهسك حجي!"
    except Exception as e:
        print(e)
    return f"✨ برج {sign_name}: طاقتك اليوم كولش قوية ومثيرة، ومحتاج تدخل مسابقة البوت الحين وتسيطر على الصدارة!"

def change_arabic_font(name):
    ar_map1 = {"ا":"آ","أ":"ٲ","ب":"بّـ","ت":"تُـ","ث":"ثًـ","ج":"جَـ","ح":"حًـ","خ":"خٌـ","د":"دُ","ذ":"ذٌ","ر":"رَمِـ","ز":"زَ","س":"سًـ","ش":"شّـ","ص":"صِـ","ض":"ضًـ","ط":"طٌـ","ظ":"ظٌـ","ع":"عَـ","غ":"غّـ","ف":"فُـ","ق":"قَـ","ك":"كَـ","ل":"لَ","م":"مِـ","n":"نِـ","ه":"هےـِ","و":"وُ","ي":"يّـ","ى":"ى","ة":"ة"}
    return ["".join(ar_map1.get(c, c) for c in name)]

def change_english_font(name):
    en_italic = {"a":"𝘢","b":"𝘣","c":"𝘤","d":"𝘥","e":"𝘦","f":"𝘧","g":"𝘨","h":"𝘩","i":"𝘪","j":"𝘫","k":"鍵","l":"𝘭","m":"𝘮","n":"𝘯","o":"𝘰","p":"𝘱","q":"𝘲","r":"𝘳","s":"𝘴","t":"𝘵","u":"𝘶","v":"𝘷","w":"𝘸","x":"𝘹","y":"𝘺","z":"𝘻"}
    return ["".join(en_italic.get(c.lower(), c) for c in name)]

async def trigger_new_quiz(chat_id):
    global CURRENT_QUIZ
    await asyncio.sleep(10) 
    quiz = random.choice(ARABIC_QUIZ_BANK)
    CURRENT_QUIZ["question"] = quiz["q"]
    CURRENT_QUIZ["answer"] = quiz["a"]
    CURRENT_QUIZ["active"] = True
    await bot.send_message(chat_id, f"🎮 ⚡ [ جـولـة عـربـيـة جـديـدة ] ⚡ 🎮\n====================================\nأسرع واحد يجاوب يكسب 5 نقاط! 🌟\n\n🤔 الـسـؤال التالي:\n{quiz['q']}\n====================================\nجاوب الحين وصعد تفاعلك!")

@ws.on_message
async def on_message(message):
    global PROCESSED_MESSAGE_IDS, PROCESSED_SYSTEM_IDS, USER_POINTS, USER_NICKNAMES, CURRENT_QUIZ, CURRENT_CHAT_ID, BOT_PHOTO_WAITING, MARK_READ_STATUS, LOG_GROUPS, MESSAGE_COUNT_STATS, MUTED_USERS, ALLOWED_USERS, BOT_LOCKED, CATCHED_MESSAGES, USER_WARNINGS, LAST_MESSAGE_ID
    try:
        content, chat_id, nickname, user_id, message_id = "", "", "", "", ""
        raw_reply_id = None
        system_action = None

        # 📥 تفكيك البيانات الأولي الحاسم بدون قفل أو حجب مبكر للأكشينات
        if hasattr(message, 'content'):
            content = getattr(message, 'content', '')
            chat_id = getattr(message, 'chat_id', '')
            message_id = getattr(message, 'id', '') or getattr(message, 'message_id', '')
            raw_reply_id = getattr(message, 'reply_to_id', None) or getattr(message, 'reply_message_id', None)
            system_action = getattr(message, 'action', None)
            if hasattr(message, 'author') and message.author:
                nickname = getattr(message.author, 'nickname', '')
                user_id = getattr(message.author, 'id', None) or getattr(message.author, 'user_id', None)
        elif isinstance(message, dict):
            content = message.get("content", "")
            chat_id = message.get("chat_id", "")
            message_id = message.get("id", "") or message.get("message_id", "")
            raw_reply_id = message.get("reply_to_id") or message.get("reply_message_id")
            system_action = message.get("action") or message.get("type")
            author_info = message.get("author", {})
            nickname = author_info.get("nickname", "")
            user_id = author_info.get("user_id") or author_info.get("id")

        content = content.strip() if content else ""
        uid_str = str(user_id).strip() if user_id else ""

        if message_id and message_id == LAST_MESSAGE_ID:
            return
        if message_id:
            LAST_MESSAGE_ID = message_id

        if nickname == "الـنـخـبة":
            return

        if not chat_id:
            return

        CURRENT_CHAT_ID = chat_id

        # �🚫 [ نظام الشتم المتراكم قبل أي أوامر أخرى ]
        if content and uid_str:
            msg_lower = content.lower()
            if any(word in msg_lower for word in BAD_WORDS):
                USER_WARNINGS[uid_str] = USER_WARNINGS.get(uid_str, 0) + 1
                warning_count = USER_WARNINGS[uid_str]

                if warning_count == 1:
                    try:
                        await bot.send_message(chat_id, f"⚠️ {nickname} هذا إنذار أول بسبب الألفاظ غير اللائقة. التكرار مرة أخرى يؤدي للطرد.")
                    except Exception as e:
                        print(f"[DEV] Send warning message failed: {e}")
                    return

                if warning_count == 2:
                    try:
                        await bot.send_message(chat_id, f"⚠️ {nickname} هذا إنذار ثاني بسبب الألفاظ غير اللائقة. سيتم طردك الآن لأنك لم تلتزم.")
                    except Exception as e:
                        print(f"[DEV] Send warning message failed: {e}")

                    print(f"Attempting to kick user: {nickname} with ID: {uid_str}")
                    try:
                        if not hasattr(bot, 'kick_user'):
                            raise AttributeError("bot.kick_user is not available in this KarboAI build")

                        await bot.kick_user(chat_id, uid_str)
                        print(f"[DEV] bot.kick_user succeeded for {nickname} ({uid_str}).")
                    except Exception as e:
                        print(f"[DEV] bot.kick_user failed for {nickname} ({uid_str}): {e}")
                        print(f"[DEV] bot.kick_user details:\n{traceback.format_exc()}")

                    try:
                        await bot.send_message(chat_id, f"🚫 تم طرد {nickname} من المجموعة بسبب تكرار الألفاظ غير اللائقة.")
                    except Exception as e:
                        print(f"[DEV] Send success/failure message failed: {e}")

                USER_WARNINGS.pop(uid_str, None)
                return

        # ----------------- [ 📥 1️⃣ نظام الترحيب والمغادرة الفوري ذو البصمة المستقلة ومنع السبام ] -----------------
        sys_key = f"{chat_id}_{uid_str}_{system_action}_{content}"

        if system_action == "user_join" or "انضم" in content or "joined" in content.lower():
            if sys_key not in PROCESSED_SYSTEM_IDS:
                PROCESSED_SYSTEM_IDS.add(sys_key)
                join_name = nickname if nickname else "يا غالي"
                welcome_msg = (
                    "👑 🌸 [ مـرحـبـاً بـك فـي جـروب الـنـخـبـة ] 🌸 👑\n"
                    "====================================\n"
                    f"ياهلا ومية هلا بنورنا الجديد الحين 🥳 『 {join_name} 』 ✨\n\n"
                    "📌 نورت الروم يا غالي، تفاعل معنا الحين وصعد نقاطك!\n"
                    "📜 اكتب [ مساعدة ] لعرض كل أوامر وألعاب البوت التفاعلية 🎲\n"
                    "====================================\n"
                    "🍃 المطور والمالك الحصري: @Adnan Saleh 👑"
                )
                await bot.send_message(chat_id, welcome_msg)
                return


        # 🛑 [ 2️⃣ جدار منع السبام والرسائل المتكررة والعادية الحاسم ]
        if not content:
            return

        if message_id and message_id in PROCESSED_MESSAGE_IDS:
            return
            
        if message_id: 
            PROCESSED_MESSAGE_IDS.add(message_id)

        IS_CREATOR = (uid_str == "0412225c-55ee-4044-82d0-00ff1217f614")
        IS_ADMIN = IS_CREATOR 

        # 💾 [ نظام التتبع العكسي بالرد ]
        if uid_str and content:
            CATCHED_MESSAGES.append({
                "msg_id": str(message_id).strip(), 
                "user_id": uid_str, 
                "name": nickname if nickname else "العضو"
            })
            if len(CATCHED_MESSAGES) > 500: 
                CATCHED_MESSAGES.pop(0)


        # 🔒 [ نظام قفل البوت ]
        if BOT_LOCKED and not IS_ADMIN and uid_str not in ALLOWED_USERS:
            return

        if nickname and ("بوت" in nickname or "النخبة" in nickname or "bot" in nickname.lower()):
            return

        if uid_str and nickname:
            USER_NICKNAMES[uid_str] = nickname

        if uid_str:
            MESSAGE_COUNT_STATS[uid_str] = MESSAGE_COUNT_STATS.get(uid_str, 0) + 1

        USER_RANK = "الـمـطـوّر والـمـتـحـكّـم الـوحـيـد 👑" if IS_CREATOR else "عضو متفاعل 👤"

        # ----------------- [ 🛠️ نظام الإدارة "دي" و "طرد" بالطرد الرباعي ] -----------------
        if content in ["طرد", "دي", "حظر", "كتم", "العاب الكتم", "الغاء الكتم", "إلغاء الكتم"] and IS_ADMIN:
            target_uid = None
            target_name = "العضو"
            
            if raw_reply_id:
                lookup_id = str(raw_reply_id).strip()
                for cached in reversed(CATCHED_MESSAGES):
                    if cached["msg_id"] == lookup_id:
                        target_uid = cached["user_id"]
                        target_name = cached["name"]
                        break

            if target_uid:
                target_uid = str(target_uid).strip()
                if content in ["طرد", "دي"]:
                    await bot.send_message(chat_id, f"⚠️ أمر الطرد معطل مؤقتاً حتى نحدد الدالة الصحيحة من مكتبة KarboAI.")
                    return

                if content == "حظر":
                    await bot.send_message(chat_id, f"⚠️ أمر الحظر معطل مؤقتاً حتى نحدد الدالة الصحيحة من مكتبة KarboAI.")
                    return

                if content == "كتم":
                    MUTED_USERS.add(target_uid)
                    await bot.send_message(chat_id, f"🤐 تم كتم العضو [{target_name}]! أي رسالة يدزها هسة تنحذف تلقائياً.")
                    return

                if content in ["الغاء الكتم", "إلغاء الكتم"]:
                    if target_uid in MUTED_USERS:
                        MUTED_USERS.remove(target_uid)
                    await bot.send_message(chat_id, f"🔊 تم إلغاء الكتم بنجاح عن [{target_name}].")
                    return
            else:
                await bot.send_message(chat_id, "⚠️ حجي عدنان، النظام لم يتعرف على الرسالة الأصلية بالذاكرة هسة، يرجى تكرار الرد الحين لتفعيل التتبع!")
                return

        # ----------------- [ 🔐 أوامر الإدارة مالت المالك عدنان ] -----------------
        if IS_ADMIN:
            if content == "قفل البوت":
                BOT_LOCKED = True
                await bot.send_message(chat_id, "🔒 تم قفل البوت بنجاح! هسة محد يقدر يستخدم أوامر البوت عدا المطورين والأشخاص المسموح لهم خاص.")
                return

            if content == "فتح البوت":
                BOT_LOCKED = False
                await bot.send_message(chat_id, "🔓 تم فتح البوت عام للكل الحين بالجروب! تفاعلوا مية مية.")
                return

            if content.startswith("سماح خاص "):
                target_id_input = content.replace("سماح خاص ", "").strip()
                ALLOWED_USERS.add(target_id_input)
                await bot.send_message(chat_id, f"🔓 تم السماح للآيدي [{target_id_input}] باستخدام البوت بنجاح حجي.")
                return

            if content.startswith("الغاء السماح "):
                target_id_input = content.replace("الغاء السماح ", "").strip()
                if target_id_input in ALLOWED_USERS:
                    ALLOWED_USERS.remove(target_id_input)
                    await bot.send_message(chat_id, f"🔒 تم إلغاء السماح للآيدي [{target_id_input}] بنجاح.")
                return

            if content == "العمل":
                stats_text = ""
                if MESSAGE_COUNT_STATS:
                    sorted_stats = sorted(MESSAGE_COUNT_STATS.items(), key=lambda x: x[1], reverse=True)
                    for idx, (u_id, m_cnt) in enumerate(sorted_stats, start=1):
                        u_name = USER_NICKNAMES.get(u_id, f"عضو [{u_id}]")
                        stats_text += f"{idx} - {u_name} = {m_cnt}\n"
                else:
                    stats_text = "No message history recorded yet.\n"

                all_report_data = (
                    "All the things I know about this group\n\n"
                    f"Group ID: {chat_id}\n"
                    "Group Type: SuperGroup\n"
                    "Rules: يمنع الطائفية، يمنع السبام، التفاعل مستمر غصباً على السيرفر الحين\n"
                    "About: جروب النخبة للأنمي والتفاعل الحماسي اليومي الحين\n"
                    f"Link: https://karboai.com/chat/{chat_id}\n"
                    f"Owner/Mods: @Adnan Saleh [{uid_str}]\n"
                    f"Muted Users Status: {len(MUTED_USERS)} users\n"
                    "-----------------------------------------\n"
                    "Chat stats:\n"
                    f"{stats_text}"
                )

                file_path = f"all_{chat_id}.txt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(all_report_data)
                
                await bot.send_message(chat_id, f"📋 أبشر حجي عدنان! ولدت كشف 'العمل' بالكامل وتم حفظه كملف نصي بنجاح! 📁")
                return

        # ----------------- [ 📑 القائمة والفعاليات والردود ] -----------------
        content_lower = content.lower()
        if content in ["مساعدة", "مساعده", "الاوامر", "الأوامر"]:
            main_menu = (
                "▀▄ ▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀\n"
                " ▄▀              القائمة الرئيسية للأوامر              ▀▄ ▄▀\n"
                "▀▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀\n"
                "✔️ جميع الأوامر مقسمة لسهولة وسرعة التصفح منعاً لتعليق الهاتف:\n\n"
                "👑 اكتب [ f1 ] : لعرض أوامر الرفع والطرد والإدارة 🛠️\n"
                "🎮 اكتب [ f2 ] : لعرض أوامر المسابقات والفعاليات والتسلية 🎲\n"
                "🔐 اكتب [ f3 ] : لعرض أوامر الأمان والحماية وقفل البوت 🔒\n\n"
                "__________________\n"
                "🍃❤️ - Sole Dev - عــدنــان"
            )
            await bot.send_message(chat_id, main_menu)
            return

        if content_lower == "f1":
            if IS_ADMIN:
                f1_menu = (
                    "▀▄ ▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▀▄▄▀▀▄▄▀▀▄▄▀▀\n"
                    " ▄▀            [ F1 ] : أوامر الرفع والإدارة             ▀▄ ▄▀\n"
                    "▀▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀\n\n"
                    "🔰💠 - أوامر الرفع والمنصب:\n"
                    "♨️- رفع اداري / تنزيل اداري\n"
                    "♨️- رفع المدير / رفع ادمن / تنزيل ادمن\n"
                    "♨️- الادمنيه / مدير المجموعه\n\n"
                    "🔰✔️ - أوامر الإدارة والطرد بالرد:\n"
                    "💡- دي | طرد | حظر | كتم | الغاء الكتم (نفذ بالرد عالعضو ⚠️)\n"
                    "📋- العمل : جلب كشف حساب كامل للمجموعة داخل ملف نصي 📂\n\n"
                    "☯️ للعودة للقائمة الرئيسية: اكتب مساعدة"
                )
                await bot.send_message(chat_id, f1_menu)
            else:
                await bot.send_message(chat_id, "للمشرفين فقط 😎")
            return

        if content_lower == "f2":
            f2_menu = (
                "▀▄ ▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▀▄▄▀▀▄▄▀▀▄▄▀▀\n"
                " ▄▀           [ F2 ] : المسابقات والتسلية والجروب          ▀▄ ▄▀\n"
                "▀▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀\n\n"
                "🎲- فعالية : تشغيل جولات ألعاب وحزورات أنمي عربية\n"
                "🎲- الغاء الفعالية / نقاطي / الصدارة والمتفاعلين\n\n"
                "🔮- حظي : كشف نسبة حظك اليوم بالجروب تحشيشياً\n"
                "⚽- توقع + فريق ضد فريق : تخمين نتيجة مباراة قادمة\n"
                "✨- زخرفة (بالعربي) / زخرف (بالإنكليزي) + الاسم\n\n"
                "👤- معلوماتي : لعرض بياناتك ورتبتك بالروم\n\n"
                "☯️ للعودة للقائمة الرئيسية: اكتب مساعدة"
            )
            await bot.send_message(chat_id, f2_menu)
            return

        if content_lower == "f3":
            if IS_ADMIN:
                f3_menu = (
                    "▀▄ ▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▄▀▀▄▀▄▄▀▀▄▄▀▀▄▄▀▀\n"
                    " ▄▀             [ F3 ] : أوامر الحماية والأمان             ▀▄ ▄▀\n"
                    "▀▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀▄▄▀▀▄▄▀▀▄▄▀\n\n"
                    "🔐- قفل البوت : لحظر ومنع أوامر الاستخدام عن المجموعة 🔒\n"
                    "🔐- فتح البوت : لفتح أوامر البوت عام للكل بالجروب 🔓\n\n"
                    "✔️- تشغيل القراءة / اطفاء القراءة مالت الرسائل التلقائية\n"
                    "📸- تغيير الصورة : لتغيير صورة البوت فوراً\n"
                    "⚙️- سماح خاص / الغاء السماح + آيدي العضو\n\n"
                    "☯️ للعودة للقائمة الرئيسية: اكتب مساعدة"
                )
                await bot.send_message(chat_id, f3_menu)
            else:
                await bot.send_message(chat_id, "للمشرفين فقط 😎")
            return

        if content == "معلوماتي":
            my_pts = USER_POINTS.get(uid_str, 0)
            my_msgs = MESSAGE_COUNT_STATS.get(uid_str, 1)
            info_card = (
                "👤 💎 [ كـارت مـعـلـومـات الـعـضـو ] 💎 👤\n"
                "=========================================\n"
                f"👤 اسـمـك: {nickname}\n"
                f"🆔 الآيـدي: {uid_str}\n"
                f"👑 الـمـنـصـب: {USER_RANK}\n"
                f"🌟 نـقـاط الفعاليات: {my_pts} نقطة 🏆\n"
                f"✉️ رسـائـل التفاعل: {my_msgs} رسالة بالروم الحين 🔥\n"
                "=========================================\n"
                "ثبت تفاعلك الحين واصعد الصدارة حجي!"
            )
            await bot.send_message(chat_id, info_card)
            return

        if content == "تغيير الصورة" and IS_ADMIN:
            BOT_PHOTO_WAITING = True
            await bot.send_message(chat_id, "دزلي صورة البوت الجديدة هسة حجي 📸")
            return

        if content == "تشغيل القراءة" and IS_ADMIN:
            MARK_READ_STATUS = "on"
            await bot.send_message(chat_id, "تم تفعيل قراءة الرسائل التلقائية ✔️")
            return

        if content == "اطفاء القراءة" and IS_ADMIN:
            MARK_READ_STATUS = "off"
            await bot.send_message(chat_id, "تم إيقاف قراءة الرسائل التلقائية ❌")
            return

        if content == "المكتومين" and IS_ADMIN:
            if not MUTED_USERS:
                await bot.send_message(chat_id, "🔈 لستة المكتومين فارغة هسة حجي!")
            else:
                await bot.send_message(chat_id, f"🔈 عدد الأعضاء المكتومين بالروم حالياً: {len(MUTED_USERS)} عضو.")
            return

        if CURRENT_QUIZ["active"] and content.strip() == str(CURRENT_QUIZ["answer"]).strip():
            CURRENT_QUIZ["active"] = False
            USER_POINTS[uid_str] = USER_POINTS.get(uid_str, 0) + 5
            await bot.send_message(chat_id, f"🎉 كفوووو يا {nickname}! إجابتك صحيحة ({content}) وكسبت 5 نقاط! 🏆\n📊 نقاطك الحالية: {USER_POINTS[uid_str]} نقطة.\n\n⏱️ انتظروا 10 ثواني.. جاري اختيار سؤال عربي جديد تلقائياً! 🚀")
            asyncio.create_task(trigger_new_quiz(chat_id))
            return

        if content.startswith("توقع "):
            teams = content.replace("توقع ", "").strip()
            if "ضد" in teams:
                parts = teams.split("ضد")
                team1, team2 = parts[0].strip(), parts[1].strip()
                scenario = random.choice(MATCH_SCENARIOS).format(team1=team1, team2=team2)
                if "مدريد" in team1 or "ريال" in team1 or "مدريد" in team2 or "ريال" in team2:
                    scenario += "\n\n👑 طبعاً التوقع يميل لملوك السانتياغو، هلا مدريد دائماً وأبعداً! 🤍"
                await bot.send_message(chat_id, f"⚽ [ تـوقـعـات مـبـاريـات بـوت الـنخـبـة ] ⚽\n====================================\n📊 المباراة: {team1} ✖️ {team2}\n\n🔮 {scenario}")
                return

        if content.startswith("برجي "):
            sign = content.replace("برجي ", "").strip()
            online_fortune = get_online_horoscope(sign)
            if online_fortune:
                await bot.send_message(chat_id, f"✨ [ تـوقـعـات أونـلايـن حـيـة لـبـرجـك ] ✨\n====================================\n{online_fortune}")
            return

        if content in ["حظي اليوم", "حظي"]:
            fortune = random.choice(FORTUNES)
            await bot.send_message(chat_id, f"🔮 [ حـظـك الـيـوم بـوت الـنخـبـة ] 🔮\n====================================\n👤 العضو: {nickname}\n🌟 {fortune}")
            return

        if content.startswith("زخرفة "):
            target_name = content.replace("زخرفة ", "").strip()
            if target_name:
                fonts = change_arabic_font(target_name)
                await bot.send_message(chat_id, f"✨ 💖 [ تـغـيـيـر الـخـطـوط ] 💖 ✨\n➔ 👑 『 {fonts[0]} 』 👑")
                return

        if content.startswith("زخرف "):
            target_name = content.replace("زخرف ", "").strip()
            if target_name:
                fonts = change_english_font(target_name)
                await bot.send_message(chat_id, f"⭐ 💎 [ 𝓕𝓸نّت 𝓢𝓽𝔂للّه ] 💎 ⭐\n➔ 亗 『 {fonts[0].upper()} 』 亗")
                return

        if content in ["فعالية", "مسابقة", "فعاليه"]:
            if CURRENT_QUIZ["active"]:
                await bot.send_message(chat_id, f"⚠️ اكو سؤال شغال هسة:\n📌 {CURRENT_QUIZ['question']}\nاكتب 'الغاء الفعالية' لتغييره.")
                return
            quiz = random.choice(ARABIC_QUIZ_BANK)
            CURRENT_QUIZ["question"] = quiz["q"]
            CURRENT_QUIZ["answer"] = quiz["a"]
            CURRENT_QUIZ["active"] = True
            await bot.send_message(chat_id, f"🎮 ⚡ [ فعاليات بوت النخبة ] ⚡ 🎮\n====================================\nأسرع واحد يجاوب ويكسب 5 نقاط! 🌟\n\n🤔 الـسـؤال:\n{quiz['q']}\n====================================\nجاوب الحين وصعد تفاعلك!")
            return

        if content in ["الغاء الفعالية", "الغاء الفعاليه"]:
            CURRENT_QUIZ["active"] = False
            await bot.send_message(chat_id, "❌ تم إلغاء السؤال الحالي!")
            return

        if content == "نقاطي":
            pts = USER_POINTS.get(uid_str, 0)
            await bot.send_message(chat_id, f"👤 العضو: {nickname}\n📊 رصيدك: {pts} نقطة! 🏆")
            return

        if content in ["الصدارة", "المتفاعلين", "صدارة"]:
            if not USER_POINTS:
                await bot.send_message(chat_id, "📊 قائمة الصدارة فارغة الحين!")
                return
            sorted_pts = sorted(USER_POINTS.items(), key=lambda x: x[1], reverse=True)[:10]
            leaderboard = "🏆 👑 [ لـوحـة صـدارة بـوت الـنخـبـة ] 👑 🏆\n====================================\n"
            for index, (u_id, pts) in enumerate(sorted_pts, start=1):
                name = USER_NICKNAMES.get(u_id, f"عضو ({u_id})")
                leaderboard += f"{index}. 👤 {name} ➔ 🌟 {pts} نقطة\n"
            leaderboard += "===================================="
            await bot.send_message(chat_id, leaderboard)
            return

        if content in AUTO_REPLIES:
            await bot.send_message(chat_id, AUTO_REPLIES[content])
            return

 
    except Exception:
        import traceback
        traceback.print_exc()


# مهمة منبه الأذكار التلقائي
async def auto_athkar_loop():
    global CURRENT_CHAT_ID
    while True:
        try:
            await asyncio.sleep(3600)
            if CURRENT_CHAT_ID:
                dhikr = random.choice(ATHKAR_BANK)
                await bot.send_message(CURRENT_CHAT_ID, dhikr)
        except Exception as e:
            print(e)

async def main():
    print("==================================================")
    print("🚀 Bot Elite: Welcomer & Anti-Spam Engines Co-exist LIVE! 🚀")
    print("==================================================")
    asyncio.create_task(auto_athkar_loop())

    while True:
        try:
            print("[INFO] Starting Karbo websocket connection...")
            await ws.run_forever()
        except KeyboardInterrupt:
            print("[INFO] Bot stopped by user.")
            break
        except Exception as e:
            print(f"[ERROR] WebSocket connection interrupted: {e}")
            print("[INFO] Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
            continue

if __name__ == "__main__":
    asyncio.run(main())