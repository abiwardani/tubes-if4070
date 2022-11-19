def clean_filename(text):
    res = text.lower()

    val_chars = "abcdefghijklmnopqrstuvwxyz0123456789_- "
    for char in text:
        if char not in val_chars:
            res = res.replace(char, "")
    
    return res.replace(" ", "_")