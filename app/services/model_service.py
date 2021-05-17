import numpy as np
import pickle
from pyvi import ViTokenizer
import re
from bs4 import BeautifulSoup

import string
import codecs

# Từ điển tích cực, tiêu cực, phủ định
path_nag = "app/resources/sentiment_dict/nag.txt"
path_pos = "app/resources/sentiment_dict/pos.txt"
path_not = "app/resources/sentiment_dict/not.txt"
path_spos = "app/resources/sentiment_dict/spos.txt"
path_snot = "app/resources/sentiment_dict/snot.txt"

with codecs.open(path_nag, "r", encoding="UTF-8") as f:
    nag = f.readlines()
nag_list = [n.replace("\n", "") for n in nag]

with codecs.open(path_pos, "r", encoding="UTF-8") as f:
    pos = f.readlines()
pos_list = [n.replace("\n", "") for n in pos]
with codecs.open(path_not, "r", encoding="UTF-8") as f:
    not_ = f.readlines()
not_list = [n.replace("\n", "") for n in not_]

with codecs.open(path_spos, "r", encoding="UTF-8") as f:
    spos = f.readlines()
spos_list = [n.rstrip() for n in spos]

with codecs.open(path_snot, "r", encoding="UTF-8") as f:
    snot_ = f.readlines()
snot_list = [n.rstrip() for n in snot_]


def predict_lgr(model, text):
    pre_proba = model.predict_proba([text])[0]
    index = np.argmax(pre_proba)
    acc = str(round(pre_proba[index] * 100, 2))
    if index == 1:
        what = "positive"
    elif index == -1:
        what = "negative"
    else :
        what = "neutral"
    acc = str(acc) + "%"
    return acc, what


def load_model_lgr(filename="app/resources/trained_models/lr_model_huy.pkl"):
    classifier_filename_exp = filename
    with open(classifier_filename_exp, "rb") as infile:
        model = pickle.load(infile)
    return model


def load_model_svm(filename="app/resources/trained_models/svm_model.pkl"):
    classifier_filename_exp = filename
    with open(classifier_filename_exp, "rb") as infile:
        model = pickle.load(infile)
    return model


def predict_svm(model, text):
    predict = model.predict([text])[0]
    if predict == 1:
        label = "positive"
    elif predict == 0:
        label = "negative"
    else:
        label = "neutral"

    return label


def normalize_text(text):
    # Remove các ký tự kéo dài: vd: đẹppppppp
    text = re.sub(
        r"([A-Z])\1+", lambda m: m.group(1).upper(), text, flags=re.IGNORECASE
    )

    # Chuyển thành chữ thường
    text = text.lower()

    # Chuẩn hóa tiếng Việt, xử lý emoj, chuẩn hóa tiếng Anh, thuật ngữ
    replace_list = {
        "òa": "oà",
        "óa": "oá",
        "ỏa": "oả",
        "õa": "oã",
        "ọa": "oạ",
        "òe": "oè",
        "óe": "oé",
        "ỏe": "oẻ",
        "õe": "oẽ",
        "ọe": "oẹ",
        "ùy": "uỳ",
        "úy": "uý",
        "ủy": "uỷ",
        "ũy": "uỹ",
        "ụy": "uỵ",
        "uả": "ủa",
        "ả": "ả",
        "ố": "ố",
        "u´": "ố",
        "ỗ": "ỗ",
        "ồ": "ồ",
        "ổ": "ổ",
        "ấ": "ấ",
        "ẫ": "ẫ",
        "ẩ": "ẩ",
        "ầ": "ầ",
        "ỏ": "ỏ",
        "ề": "ề",
        "ễ": "ễ",
        "ắ": "ắ",
        "ủ": "ủ",
        "ế": "ế",
        "ở": "ở",
        "ỉ": "ỉ",
        "ẻ": "ẻ",
        "àk": u" à ",
        "aˋ": "à",
        "iˋ": "ì",
        "ă´": "ắ",
        "ử": "ử",
        "e˜": "ẽ",
        "y˜": "ỹ",
        "a´": "á",
        # Quy các icon về 2 loại emoj: Tích cực hoặc tiêu cực
        "👹": "nagative",
        "👻": "positive",
        "💃": "positive",
        "🤙": " positive ",
        "👍": " positive ",
        "💄": "positive",
        "💎": "positive",
        "💩": "positive",
        "😕": "nagative",
        "😱": "nagative",
        "😸": "positive",
        "😾": "nagative",
        "🚫": "nagative",
        "🤬": "nagative",
        "🧚": "positive",
        "🧡": "positive",
        "🐶": " positive ",
        "👎": " nagative ",
        "😣": " nagative ",
        "✨": " positive ",
        "❣": " positive ",
        "☀": " positive ",
        "♥": " positive ",
        "🤩": " positive ",
        "like": " positive ",
        "💌": " positive ",
        "🤣": " positive ",
        "🖤": " positive ",
        "🤤": " positive ",
        ":(": " nagative ",
        "😢": " nagative ",
        "❤": " positive ",
        "😍": " positive ",
        "😘": " positive ",
        "😪": " nagative ",
        "😊": " positive ",
        "?": " ? ",
        "😁": " positive ",
        "💖": " positive ",
        "😟": " nagative ",
        "😭": " nagative ",
        "💯": " positive ",
        "💗": " positive ",
        "♡": " positive ",
        "💜": " positive ",
        "🤗": " positive ",
        "^^": " positive ",
        "😨": " nagative ",
        "☺": " positive ",
        "💋": " positive ",
        "👌": " positive ",
        "😖": " nagative ",
        "😀": " positive ",
        ":((": " nagative ",
        "😡": " nagative ",
        "😠": " nagative ",
        "😒": " nagative ",
        "🙂": " positive ",
        "😏": " nagative ",
        "😝": " positive ",
        "😄": " positive ",
        "😙": " positive ",
        "😤": " nagative ",
        "😎": " positive ",
        "😆": " positive ",
        "💚": " positive ",
        "✌": " positive ",
        "💕": " positive ",
        "😞": " nagative ",
        "😓": " nagative ",
        "️🆗️": " positive ",
        "😉": " positive ",
        "😂": " positive ",
        ":v": "  positive ",
        "=))": "  positive ",
        "😋": " positive ",
        "💓": " positive ",
        "😐": " nagative ",
        ":3": " positive ",
        "😫": " nagative ",
        "😥": " nagative ",
        "😃": " positive ",
        "😬": " 😬 ",
        "😌": " 😌 ",
        "💛": " positive ",
        "🤝": " positive ",
        "🎈": " positive ",
        "😗": " positive ",
        "🤔": " nagative ",
        "😑": " nagative ",
        "🔥": " nagative ",
        "🙏": " nagative ",
        "🆗": " positive ",
        "😻": " positive ",
        "💙": " positive ",
        "💟": " positive ",
        "😚": " positive ",
        "❌": " nagative ",
        "👏": " positive ",
        ";)": " positive ",
        "<3": " positive ",
        "🌝": " positive ",
        "🌷": " positive ",
        "🌸": " positive ",
        "🌺": " positive ",
        "🌼": " positive ",
        "🍓": " positive ",
        "🐅": " positive ",
        "🐾": " positive ",
        "👉": " positive ",
        "💐": " positive ",
        "💞": " positive ",
        "💥": " positive ",
        "💪": " positive ",
        "💰": " positive ",
        "😇": " positive ",
        "😛": " positive ",
        "😜": " positive ",
        "🙃": " positive ",
        "🤑": " positive ",
        "🤪": " positive ",
        "☹": " nagative ",
        "💀": " nagative ",
        "😔": " nagative ",
        "😧": " nagative ",
        "😩": " nagative ",
        "😰": " nagative ",
        "😳": " nagative ",
        "😵": " nagative ",
        "😶": " nagative ",
        "🙁": " nagative ",
        # Chuẩn hóa 1 số sentiment words/English words
        ":))": "  positive ",
        ":)": " positive ",
        "ô kêi": " ok ",
        "okie": " ok ",
        " o kê ": " ok ",
        "okey": " ok ",
        "ôkê": " ok ",
        "oki": " ok ",
        " oke ": " ok ",
        " okay": " ok ",
        "okê": " ok ",
        " tks ": u" cám ơn ",
        "thks": u" cám ơn ",
        "thanks": u" cám ơn ",
        "ths": u" cám ơn ",
        "thank": u" cám ơn ",
        "⭐": "star ",
        "*": "star ",
        "🌟": "star ",
        "🎉": u" positive ",
        "ko": u"không",
        "kg ": u" không ",
        "not": u" không ",
        u" kg ": u" không ",
        '"k ': u" không ",
        " kh ": u" không ",
        "kô": u" không ",
        "hok": u" không ",
        " kp ": u" không phải ",
        u" kô ": u" không ",
        '"ko ': u" không ",
        u" ko ": u" không ",
        u" k ": u" không ",
        "khong": u" không ",
        u" hok ": u" không ",
        "he he": " positive ",
        "hehe": " positive ",
        "hihi": " positive ",
        "haha": " positive ",
        "hjhj": " positive ",
        " lol ": " nagative ",
        " cc ": " nagative ",
        "cute": u" dễ thương ",
        "huhu": " nagative ",
        " vs ": u" với ",
        "wa": " quá ",
        "wá": u" quá",
        "j": u" gì ",
        "“": " ",
        " sz ": u" cỡ ",
        "size": u" cỡ ",
        u" đx ": u" được ",
        "dk": u" được ",
        "dc": u" được ",
        "đk": u" được ",
        "đc": u" được ",
        "authentic": u" chuẩn chính hãng ",
        u" aut ": u" chuẩn chính hãng ",
        u" auth ": u" chuẩn chính hãng ",
        "thick": u" positive ",
        "store": u" cửa hàng ",
        "shop": u" cửa hàng ",
        "sp": u" sản phẩm ",
        "gud": u" tốt ",
        "god": u" tốt ",
        "wel done": " tốt ",
        "good": u" tốt ",
        "gút": u" tốt ",
        "sấu": u" xấu ",
        "gut": u" tốt ",
        u" tot ": u" tốt ",
        u" nice ": u" tốt ",
        "perfect": "rất tốt",
        "bt": u" bình thường ",
        "time": u" thời gian ",
        "qá": u" quá ",
        u" ship ": u" giao hàng ",
        u" m ": u" mình ",
        u" mik ": u" mình ",
        "ể": "ể",
        "product": "sản phẩm",
        "quality": "chất lượng",
        "chat": " chất ",
        "excelent": "hoàn hảo",
        "bad": "tệ",
        "fresh": " tươi ",
        "sad": " tệ ",
        "date": u" hạn sử dụng ",
        "hsd": u" hạn sử dụng ",
        "quickly": u" nhanh ",
        "quick": u" nhanh ",
        "fast": u" nhanh ",
        "delivery": u" giao hàng ",
        u" síp ": u" giao hàng ",
        "beautiful": u" đẹp tuyệt vời ",
        u" tl ": u" trả lời ",
        u" r ": u" rồi ",
        u" shopE ": u" cửa hàng ",
        u" order ": u" đặt hàng ",
        "chất lg": u" chất lượng ",
        u" sd ": u" sử dụng ",
        u" dt ": u" điện thoại ",
        u" nt ": u" nhắn tin ",
        u" tl ": u" trả lời ",
        u" sài ": u" xài ",
        u"bjo": u" bao giờ ",
        "thik": u" thích ",
        u" sop ": u" cửa hàng ",
        " fb ": " facebook ",
        " face ": " facebook ",
        " very ": u" rất ",
        u"quả ng ": u" quảng  ",
        "dep": u" đẹp ",
        u" xau ": u" xấu ",
        "delicious": u" ngon ",
        u"hàg": u" hàng ",
        u"qủa": u" quả ",
        "iu": u" yêu ",
        "fake": u" giả mạo ",
        "trl": "trả lời",
        "><": u" positive ",
        " por ": u" tệ ",
        " poor ": u" tệ ",
        "ib": u" nhắn tin ",
        "rep": u" trả lời ",
        u"fback": " feedback ",
        "fedback": " feedback ",
        # dưới 3* quy về 1*, trên 3* quy về 5*
        "6 sao": " 5star ",
        "6 star": " 5star ",
        "5star": " 5star ",
        "5 sao": " 5star ",
        "5sao": " 5star ",
        "starstarstarstarstar": " 5star ",
        "1 sao": " 1star ",
        "1sao": " 1star ",
        "2 sao": " 1star ",
        "2sao": " 1star ",
        "1 star": "1star",
        "2 starstar": " 1star ",
        "1star": " 1star ",
        "0 sao": " 1star ",
        "0star": " 1star ",
    }

    for k, v in replace_list.items():
        text = text.replace(k, v)

    # chuyen punctuation thành space
    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
    text = text.translate(translator)
    text = re.sub(r"http\S+", "", text)
    text = BeautifulSoup(text, "lxml").get_text()
    text = re.sub("\S*\d\S*", "", text).strip()

    """
    str =  " Thời gian giao hàng rất nhanh giá rẻ mà giày cực chất! Êm chân lắm.thanks shop nhiều" 
    text = ViTokenizer.tokenize(str) "Thời_gian giao hàng rất nhanh giá rẻ mà giày cực chất ! Êm chân lắm . thanks shop nhiều" 
    texts = text.split() ['Thời_gian', 'giao', 'hàng', 'rất', 'nhanh', 'giá', 'rẻ', 'mà', 'giày', 'cực', 'chất', '!', 'Êm', 'chân', 'lắm', '.', 'thanks', 'shop', 'nhiều']
    texts = [t.replace('_', ' ') for t in texts] ['Thời gian', 'giao', 'hàng', 'rất', 'nhanh', 'giá', 'rẻ', 'mà', 'giày', 'cực', 'chất', '!', 'Êm', 'chân', 'lắm', '.', 'thanks', 'shop', 'nhiều']
    """
    text = ViTokenizer.tokenize(text)
    texts = text.split()
    len_text = len(texts)

    texts = [t.replace("_", " ") for t in texts]
    for i in range(len_text):
        cp_text = texts[i]
        if (
                cp_text in not_list
        ):  # Xử lý vấn đề phủ định (VD: áo này chẳng đẹp--> áo này notpos)
            numb_word = 2 if len_text - i - 1 >= 4 else len_text - i - 1

            for j in range(numb_word):
                if texts[i + j + 1] in pos_list:
                    texts[i] = "notpos"
                    texts[i + j + 1] = ""

                if texts[i + j + 1] in nag_list:
                    texts[i] = "notnag"
                    texts[i + j + 1] = ""
        else:  # Thêm feature cho những sentiment words (áo này đẹp--> áo này đẹp positive)
            if cp_text in pos_list:
                texts.append("positive")
            elif cp_text in nag_list:
                texts.append("negative")

    text = u" ".join(texts)

    # remove nốt những ký tự thừa thãi
    text = text.replace(u'"', u" ")
    text = text.replace(u"️", u"")
    text = text.replace("🏻", "")
    for pos in spos_list:
        if pos in text:
            text += " " + "positive"
    for snot in snot_list:
        if snot in text:
            text += " " + "negative"
    return text
