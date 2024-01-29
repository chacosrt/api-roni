import unicodedata as _unicodedata
import functions.fn as _fn


# *************************************************************************************************************************************
# STDNUM.EXCEPTIONS in use functions
# *************************************************************************************************************************************


class ValidationError(Exception):
    """Top-level error for validating numbers.
    This exception should normally not be raised, only subclasses of this
    exception."""

    def __str__(self):
        """Return the exception message."""
        return "".join(self.args[:1]) or getattr(self, "message", "")


# *************************************************************************************************************************************


class InvalidFormat(ValidationError):  # noqa N818
    """Something is wrong with the format of the number.
    This generally means characters or delimiters that are not allowed are
    part of the number or required parts are missing."""

    message = "El valor tiene un formato inválido."


# *************************************************************************************************************************************


class InvalidChecksum(ValidationError):  # noqa N818
    """The number's internal checksum or check digit does not match."""

    message = "El dígito verificador y/o checksum del valor es inválido."


# *************************************************************************************************************************************


class InvalidLength(InvalidFormat):  # noqa N818
    """The length of the number is wrong."""

    message = "El valor tiene una longitud inválida."


# *************************************************************************************************************************************


class InvalidComponent(ValidationError):  # noqa N818
    """One of the parts of the number has an invalid reference.
    Some part of the number refers to some external entity like a country
    code, a date or a predefined collection of values. The number contains
    some invalid reference."""

    message = "Alguna de las partes de valor es inválido o desconocido.."


# *************************************************************************************************************************************
# STDNUM.UTIL in use functions
# *************************************************************************************************************************************


def _mk_char_map(mapping):
    """Transform a dictionary with comma separated uniode character names
    to tuples with unicode characters as key."""
    for key, value in mapping.items():
        for char in key.split(","):
            try:
                yield (_unicodedata.lookup(char), value)
            except KeyError:  # pragma: no cover (does not happen on Python3)
                pass


# *************************************************************************************************************************************

_char_map = dict(
    _mk_char_map(
        {
            "HYPHEN-MINUS,ARMENIAN HYPHEN,HEBREW PUNCTUATION MAQAF,HYPHEN,"
            "NON-BREAKING HYPHEN,FIGURE DASH,EN DASH,EM DASH,HORIZONTAL BAR,"
            "SMALL HYPHEN-MINUS,FULLWIDTH HYPHEN-MINUS,MONGOLIAN NIRUGU,OVERLINE,"
            "HYPHEN BULLET,MACRON,MODIFIER LETTER MINUS SIGN,FULLWIDTH MACRON,"
            "OGHAM SPACE MARK,SUPERSCRIPT MINUS,SUBSCRIPT MINUS,MINUS SIGN,"
            "HORIZONTAL LINE EXTENSION,HORIZONTAL SCAN LINE-1,HORIZONTAL SCAN LINE-3,"
            "HORIZONTAL SCAN LINE-7,HORIZONTAL SCAN LINE-9,STRAIGHTNESS": "-",
            "ASTERISK,ARABIC FIVE POINTED STAR,SYRIAC HARKLEAN ASTERISCUS,"
            "FLOWER PUNCTUATION MARK,VAI FULL STOP,SMALL ASTERISK,FULLWIDTH ASTERISK,"
            "ASTERISK OPERATOR,STAR OPERATOR,HEAVY ASTERISK,LOW ASTERISK,"
            "OPEN CENTRE ASTERISK,EIGHT SPOKED ASTERISK,SIXTEEN POINTED ASTERISK,"
            "TEARDROP-SPOKED ASTERISK,OPEN CENTRE TEARDROP-SPOKED ASTERISK,"
            "HEAVY TEARDROP-SPOKED ASTERISK,EIGHT TEARDROP-SPOKED PROPELLER ASTERISK,"
            "HEAVY EIGHT TEARDROP-SPOKED PROPELLER ASTERISK,"
            "ARABIC FIVE POINTED STAR": "*",
            "COMMA,ARABIC COMMA,SINGLE LOW-9 QUOTATION MARK,IDEOGRAPHIC COMMA,"
            "ARABIC DECIMAL SEPARATOR,ARABIC THOUSANDS SEPARATOR,PRIME,RAISED COMMA,"
            "PRESENTATION FORM FOR VERTICAL COMMA,SMALL COMMA,"
            "SMALL IDEOGRAPHIC COMMA,FULLWIDTH COMMA,CEDILLA": ",",
            "FULL STOP,MIDDLE DOT,GREEK ANO TELEIA,ARABIC FULL STOP,"
            "IDEOGRAPHIC FULL STOP,SYRIAC SUPRALINEAR FULL STOP,"
            "SYRIAC SUBLINEAR FULL STOP,SAMARITAN PUNCTUATION NEQUDAA,"
            "TIBETAN MARK INTERSYLLABIC TSHEG,TIBETAN MARK DELIMITER TSHEG BSTAR,"
            "RUNIC SINGLE PUNCTUATION,BULLET,ONE DOT LEADER,HYPHENATION POINT,"
            "WORD SEPARATOR MIDDLE DOT,RAISED DOT,KATAKANA MIDDLE DOT,"
            "SMALL FULL STOP,FULLWIDTH FULL STOP,HALFWIDTH KATAKANA MIDDLE DOT,"
            "AEGEAN WORD SEPARATOR DOT,PHOENICIAN WORD SEPARATOR,"
            "KHAROSHTHI PUNCTUATION DOT,DOT ABOVE,ARABIC SYMBOL DOT ABOVE,"
            "ARABIC SYMBOL DOT BELOW,BULLET OPERATOR,DOT OPERATOR": ".",
            "SOLIDUS,SAMARITAN PUNCTUATION ARKAANU,FULLWIDTH SOLIDUS,DIVISION SLASH,"
            "MATHEMATICAL RISING DIAGONAL,BIG SOLIDUS,FRACTION SLASH": "/",
            "COLON,ETHIOPIC WORDSPACE,RUNIC MULTIPLE PUNCTUATION,MONGOLIAN COLON,"
            "PRESENTATION FORM FOR VERTICAL COLON,FULLWIDTH COLON,"
            "PRESENTATION FORM FOR VERTICAL TWO DOT LEADER,SMALL COLON": ":",
            "SPACE,NO-BREAK SPACE,EN QUAD,EM QUAD,EN SPACE,EM SPACE,"
            "THREE-PER-EM SPACE,FOUR-PER-EM SPACE,SIX-PER-EM SPACE,FIGURE SPACE,"
            "PUNCTUATION SPACE,THIN SPACE,HAIR SPACE,NARROW NO-BREAK SPACE,"
            "MEDIUM MATHEMATICAL SPACE,IDEOGRAPHIC SPACE": " ",
            "FULLWIDTH DIGIT ZERO,MATHEMATICAL BOLD DIGIT ZERO,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT ZERO,MATHEMATICAL SANS-SERIF DIGIT ZERO,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT ZERO,MATHEMATICAL MONOSPACE DIGIT ZERO": "0",
            "FULLWIDTH DIGIT ONE,MATHEMATICAL BOLD DIGIT ONE,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT ONE,MATHEMATICAL SANS-SERIF DIGIT ONE,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT ONE,MATHEMATICAL MONOSPACE DIGIT ONE": "1",
            "FULLWIDTH DIGIT TWO,MATHEMATICAL BOLD DIGIT TWO,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT TWO,MATHEMATICAL SANS-SERIF DIGIT TWO,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT TWO,MATHEMATICAL MONOSPACE DIGIT TWO": "2",
            "FULLWIDTH DIGIT THREE,MATHEMATICAL BOLD DIGIT THREE,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT THREE,MATHEMATICAL SANS-SERIF DIGIT THREE,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT THREE,MATHEMATICAL MONOSPACE DIGIT THREE": "3",
            "FULLWIDTH DIGIT FOUR,MATHEMATICAL BOLD DIGIT FOUR,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT FOUR,MATHEMATICAL SANS-SERIF DIGIT FOUR,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT FOUR,MATHEMATICAL MONOSPACE DIGIT FOUR": "4",
            "FULLWIDTH DIGIT FIVE,MATHEMATICAL BOLD DIGIT FIVE,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT FIVE,MATHEMATICAL SANS-SERIF DIGIT FIVE,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT FIVE,MATHEMATICAL MONOSPACE DIGIT FIVE": "5",
            "FULLWIDTH DIGIT SIX,MATHEMATICAL BOLD DIGIT SIX,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT SIX,MATHEMATICAL SANS-SERIF DIGIT SIX,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT SIX,MATHEMATICAL MONOSPACE DIGIT SIX": "6",
            "FULLWIDTH DIGIT SEVEN,MATHEMATICAL BOLD DIGIT SEVEN,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT SEVEN,MATHEMATICAL SANS-SERIF DIGIT SEVEN,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT SEVEN,MATHEMATICAL MONOSPACE DIGIT SEVEN": "7",
            "FULLWIDTH DIGIT EIGHT,MATHEMATICAL BOLD DIGIT EIGHT,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT EIGHT,MATHEMATICAL SANS-SERIF DIGIT EIGHT,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT EIGHT,MATHEMATICAL MONOSPACE DIGIT EIGHT": "8",
            "FULLWIDTH DIGIT NINE,MATHEMATICAL BOLD DIGIT NINE,"
            "MATHEMATICAL DOUBLE-STRUCK DIGIT NINE,MATHEMATICAL SANS-SERIF DIGIT NINE,"
            "MATHEMATICAL SANS-SERIF BOLD DIGIT NINE,MATHEMATICAL MONOSPACE DIGIT NINE": "9",
            "APOSTROPHE,GRAVE ACCENT,ACUTE ACCENT,MODIFIER LETTER RIGHT HALF RING,"
            "MODIFIER LETTER LEFT HALF RING,MODIFIER LETTER PRIME,"
            "MODIFIER LETTER TURNED COMMA,MODIFIER LETTER APOSTROPHE,"
            "MODIFIER LETTER VERTICAL LINE,COMBINING GRAVE ACCENT,"
            "COMBINING ACUTE ACCENT,COMBINING TURNED COMMA ABOVE,"
            "COMBINING COMMA ABOVE,ARMENIAN APOSTROPHE,"
            "SINGLE HIGH-REVERSED-9 QUOTATION MARK,LEFT SINGLE QUOTATION MARK,"
            "RIGHT SINGLE QUOTATION MARK": "'",
        }
    )
)

# *************************************************************************************************************************************


def to_unicode(text):
    """Convert the specified text to a unicode string."""
    if not isinstance(text, type("")):
        try:
            return text.decode("utf-8")
        except UnicodeDecodeError:
            return text.decode("iso-8859-15")
    return text


# *************************************************************************************************************************************


def _clean_chars(number):
    """Replace various Unicode characters with their ASCII counterpart."""
    return "".join(_char_map.get(x, x) for x in number)


# *************************************************************************************************************************************


def clean(number, deletechars=""):

    if number is None:
        number = ""

    """Remove the specified characters from the supplied number.
    >>> clean('123-456:78 9', ' -:')
    '123456789'
    >>> clean('1–2—3―4')
    '1-2-3-4'
    """
    try:
        number = "".join(x for x in number)
    except Exception:  # noqa: B902
        raise InvalidFormat()
    # if sys.version < '3' and isinstance(number, str):  # pragma: no cover (Python 2 specific code)
    #    try:
    #        number = _clean_chars(number.decode()).encode()
    #    except UnicodeError:
    #        try:
    #            number = _clean_chars(number.decode('utf-8')).encode('utf-8')
    #        except UnicodeError:
    #            pass
    # else:  # pragma: no cover (Python 3 specific code)
    number = _clean_chars(number)
    return "".join(x for x in number if x not in deletechars)


# *************************************************************************************************************************************
