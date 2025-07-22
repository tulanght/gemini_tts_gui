# src/gemini_tts_app/constants.py
# Phiên bản: constants_v8.0 - Tái cấu trúc PREDEFINED_READING_STYLES thành từ điển đa ngôn ngữ.
APP_NAME = "Gemini Creative Suite"
APP_VERSION = "1.6.0"
APP_AUTHOR = "Cuong Tran" 

# --- API Key Settings ---
NUM_API_KEYS = 3 

# --- TTS Settings ---
DEFAULT_VOICE = "Algieba"
DEFAULT_TEMPERATURE = 1.0
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
DEFAULT_TOP_P = 0.95
MIN_TOP_P = 0.0
MAX_TOP_P = 1.0

# --- MỚI: Hằng số cho Trợ lý Biên tập ---
DATABASE_FILE = "assistant_data.db"

# Ngưỡng ký tự cho Tiêu đề
TITLE_CHAR_LIMIT_GOOD_MIN = 90
TITLE_CHAR_LIMIT_GOOD_MAX = 100
TITLE_CHAR_LIMIT_MAX = 100

# Màu sắc cảnh báo
COLOR_OK = "#2E7D32"      # Xanh lá đậm
COLOR_WARN = "#FF8F00"   # Vàng cam
COLOR_ERROR = "#D32F2F"   # Đỏ đậm
COLOR_NORMAL = "black"

# Regex để bóc tách các lựa chọn
GEMINI_RESPONSE_PATTERN = r"\*\*LỰA CHỌN \d+.*?\*\*([\s\S]*?)(?=\*\*LỰA CHỌN|\Z)"

GEMINI_TTS_VOICES_DETAILED = [
    {'name': 'Orus', 'gender': 'Nam', 'description': 'Nghiêm túc, đĩnh đạc - Giới thiệu sản phẩm, chuyên sâu'},
    {'name': 'Lapetus', 'gender': 'Nam', 'description': 'Rõ ràng, dễ hiểu - Hướng dẫn kỹ thuật, bài giảng'},
    {'name': 'Rasalgethi', 'gender': 'Nam', 'description': 'Mạch lạc, logic - Voice cho trợ lý ảo, đào tạo nội bộ'},
    {'name': 'Schedar', 'gender': 'Nam', 'description': 'Ổn định, tin cậy - Đọc tài liệu, nội dung AI'},
    {'name': 'Kore', 'gender': 'Nam', 'description': 'Chuyên nghiệp, gãy gọn - Video thuyết trình, sản phẩm'},
    {'name': 'Erinome', 'gender': 'Nam', 'description': 'Trung tính, dễ tiếp cận - Video khoa học, giáo dục'},
    {'name': 'Charon', 'gender': 'Nam', 'description': 'Trẻ trung, dễ nghe - Video học tập, chia sẻ kiến thức'},
    {'name': 'Anilam', 'gender': 'Nam', 'description': 'Kiên định, chắc chắn - Dẫn dắt nội dung chuyên môn'},
    {'name': 'Enceladus', 'gender': 'Nam', 'description': 'Êm ái, thư giãn - Voice đọc sách, kiến thức nhẹ nhàng'},
    {'name': 'Sadaltager', 'gender': 'Nữ', 'description': 'Lôi cuốn, trò chuyện - Giải thích công nghệ, nội dung chuyên sâu'},
    {'name': 'Leda', 'gender': 'Nữ', 'description': 'Tươi mới, rõ ràng - Nội dung học tập cho Gen Z'},
    {'name': 'Autonoe', 'gender': 'Nữ', 'description': 'Ấm áp, truyền cảm - Video startup, khởi nghiệp'},
    {'name': 'Despina', 'gender': 'Nữ', 'description': 'Êm dịu, dễ tiếp thu - Storytelling nhẹ nhàng, kể chuyện giáo dục'},
    {'name': 'Umbriel', 'gender': 'Nam', 'description': 'Bình tĩnh, thân thiện - Podcast cuộc sống, chia sẻ cá nhân'},
    {'name': 'Algenib', 'gender': 'Nam', 'description': 'Trầm lắng, nghiêm túc - Podcast chủ đề sâu'},
    {'name': 'Pulcherrima', 'gender': 'Nữ', 'description': 'Nhiệt huyết, truyền cảm - Call-to-action, podcast mạnh mẽ'},
    {'name': 'Callirrhoe', 'gender': 'Nữ', 'description': 'Nhẹ nhàng, sâu lắng - Healing content, podcast thư giãn'},
    {'name': 'Achernar', 'gender': 'Nữ', 'description': 'Trầm sâu, cảm xúc - Podcast ban đêm, chủ đề sâu sắc'},
    {'name': 'Sulafar', 'gender': 'Nữ', 'description': 'Truyền cảm, ấm áp - Podcast tâm sự, đài tập'},
    {'name': 'Fenrir', 'gender': 'Nam', 'description': 'Sôi nổi, mạnh mẽ - Video giới thiệu sản phẩm, quảng cáo'},
    {'name': 'Algieba', 'gender': 'Nam', 'description': 'Đậm chất truyền cảm - Giọng kể chuyện bán hàng'},
    {'name': 'Achird', 'gender': 'Nữ', 'description': 'Thân thiện, gần gũi - Video giới thiệu sản phẩm nhẹ nhàng'},
    {'name': 'Sadachbia', 'gender': 'Nữ', 'description': 'Tươi sáng, nhiệt huyết - Quảng cáo năng lượng, truyền động lực'},
    {'name': 'Zephyr', 'gender': 'Nữ', 'description': 'Ngọt ngào, cảm xúc - Giới thiệu sản phẩm thiên về cảm nhận'},
    {'name': 'Laomedeia', 'gender': 'Nữ', 'description': 'Trẻ trung, hiện đại - TikTok giới thiệu sản phẩm'},
    {'name': 'Puck', 'gender': 'Nam', 'description': 'Hóm hỉnh, vui vẻ - Video TikTok, giải trí ngắn'},
    {'name': 'Zubenelgenubi', 'gender': 'Nam', 'description': 'Tự nhiên, sinh động - TikTok đời thường, chia sẻ cuộc sống'},
    {'name': 'Aoede', 'gender': 'Nữ', 'description': 'Dễ chịu, vui vẻ - Voice cho lifestyle, game, giải trí'},
    {'name': 'Vindemiatrix', 'gender': 'Nữ', 'description': 'Nhẹ nhàng, chuyên nghiệp - Voice trợ lý ảo, CSKH'},
    {'name': 'Gacrux', 'gender': 'Nam', 'description': 'Tự tin, có chiều sâu - Voice review, đánh giá sản phẩm'},
]

# Cấu trúc mới hỗ trợ đa ngôn ngữ
PREDEFINED_READING_STYLES = {
    'vi': [
        # Prompt 1: Tối ưu cho truyện tâm sự gia đình, đêm khuya - Tự nhiên & Khách quan
        "Phong cách: kể chuyện một cách bình tĩnh, khách quan. Tông giọng: đều, không quá nhấn nhá, giữ sự trung lập. Tốc độ: vừa phải, trôi chảy. Yêu cầu quan trọng: không tự ý thêm cảm xúc cá nhân vào lời kể, tránh các khoảng ngừng dài không cần thiết, đọc như một người quan sát và tường thuật lại câu chuyện.",
        # Prompt 2: Phong cách Radio tâm sự - Ấm áp nhưng kiểm soát
        "Vai trò: người dẫn chương trình radio tâm sự. Giọng đọc ấm, rõ ràng nhưng có kiểm soát, không bi lụy. Nhịp điệu chậm rãi, đều đặn. Ngắt nghỉ ngắn gọn tại các dấu câu. Mục tiêu là tạo sự tin cậy và đồng cảm một cách tinh tế, không phải diễn kịch.",
        # Prompt 3: Kể chuyện đời thường - Gần gũi, không màu mè
        "Phong cách: như đang trò chuyện, kể lại một câu chuyện đời thường. Giọng nói tự nhiên, không màu mè, không cần quá trau chuốt. Tốc độ nói nhanh hơn một chút, thể hiện sự gần gũi. Tránh sử dụng ngữ điệu của người kể chuyện chuyên nghiệp.",
        # Prompt 4: Đọc tin tức xã hội - Rõ ràng, trung lập
        "Phong cách của một biên tập viên đọc tin tức xã hội: rõ ràng, mạch lạc, dứt khoát. Giọng đọc giữ thái độ trung lập, không thể hiện quan điểm cá nhân. Tập trung vào việc truyền đạt thông tin một cách chính xác.",
        "" # Lựa chọn trống
    ],
    'en': [
        # Prompt 1: Optimized for narration, documentary - Clear & Objective
        "Style: narrate in a calm, objective manner. Tone: even, without excessive emotional emphasis, maintaining neutrality. Pace: moderate and fluent. Key instruction: do not add personal feelings to the narration, avoid unnecessary long pauses, read as an observer recounting events.",
        # Prompt 2: Audiobook storyteller style - Engaging & Warm
        "Role: an audiobook narrator. Voice: warm, clear, and engaging. Pacing: steady, with appropriate pauses for dramatic effect at punctuation. The goal is to create an immersive listening experience.",
        # Prompt 3: Casual conversation, vlogging style - Friendly & Natural
        "Style: as if speaking to a friend in a vlog. Voice: natural, relaxed, not overly polished. Pace: slightly faster, conveying a sense of casual conversation. Avoid a formal, professional narrator's tone.",
        # Prompt 4: News report style - Authoritative & Clear
        "Style of a news anchor reporting on a serious topic: clear, articulate, and authoritative. The voice should remain neutral, focusing on delivering information accurately and without bias.",
        "" # Empty option
    ]
}