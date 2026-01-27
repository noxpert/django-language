# Migration to add family relationship vocabulary in Hungarian, English, and German

from django.db import migrations


def add_family_vocabulary(apps, schema_editor):
    Language = apps.get_model("vocabulary", "Language")
    Word = apps.get_model("vocabulary", "Word")
    Translation = apps.get_model("vocabulary", "Translation")

    # Get languages
    english = Language.objects.get(code="en")
    hungarian = Language.objects.get(code="hu")
    german = Language.objects.get(code="de")

    # Family vocabulary data: (hu_word, hu_def, en_word, en_def, de_word, de_def)
    family_words = [
        (
            "anyós",
            "A házastárs anyja; gyakran viccek szereplője, de remélhetőleg kedves ember",
            "mother-in-law",
            "Your spouse's mother; often featured in jokes but hopefully a lovely person",
            "Schwiegermutter",
            "Die Mutter des Ehepartners; oft Gegenstand von Witzen, aber hoffentlich eine nette Person",
        ),
        (
            "após",
            "A házastárs apja; az ember, akinek jóváhagyását valószínűleg kérted, mielőtt megkérted a kezét",
            "father-in-law",
            "Your spouse's father; the man whose approval you probably sought before proposing",
            "Schwiegervater",
            "Der Vater des Ehepartners; der Mann, dessen Zustimmung man wahrscheinlich vor dem Heiratsantrag suchte",
        ),
        (
            "bátya",
            "A férfi testvér, aki előbb született és soha nem hagyja elfelejteni",
            "older brother",
            "The male sibling who got there first and never lets you forget it",
            "älterer Bruder",
            "Der männliche Geschwisterteil, der zuerst da war und es dich nie vergessen lässt",
        ),
        (
            "feleség",
            "Az a nő, aki igent mondott és az élettársad lett (és valószínűleg a főnök)",
            "wife",
            "The woman who said yes and became your life partner (and probably the boss)",
            "Ehefrau",
            "Die Frau, die ja gesagt hat und dein Lebenspartner wurde (und wahrscheinlich der Chef ist)",
        ),
        (
            "férj",
            "Az a férfi, aki megígérte, hogy szeret és dédelget; dupla szerepben üvegnyitó és pókeltávolító",
            "husband",
            "The man who promised to love and cherish; also doubles as jar opener and spider remover",
            "Ehemann",
            "Der Mann, der versprochen hat zu lieben und zu ehren; dient auch als Glasöffner und Spinnenentferner",
        ),
        (
            "gyerek",
            "Kis ember, aki naponta körülbelül 437-szer kérdezi, hogy miért",
            "child",
            "A small human who asks why approximately 437 times per day",
            "Kind",
            "Ein kleiner Mensch, der ungefähr 437 Mal am Tag fragt warum",
        ),
        (
            "húg",
            "A női testvér, aki utánad jött és határozottan ellopta a szüleid figyelmét",
            "younger sister",
            "The female sibling who came after you and definitely stole your parents' attention",
            "jüngere Schwester",
            "Die weibliche Geschwister, die nach dir kam und definitiv die Aufmerksamkeit deiner Eltern gestohlen hat",
        ),
        (
            "menyasszony",
            "Esküvőt tervező nő; óvatosan közelíts a torta kóstolás alatt",
            "bride or fiancée",
            "A woman planning a wedding; approach with caution during cake tastings",
            "Braut oder Verlobte",
            "Eine Frau, die eine Hochzeit plant; nähere dich mit Vorsicht während der Kuchenverkostung",
        ),
        (
            "nagyapa",
            "A szülőd apja; régi történetek őrzője és általában a legtitokzatosabb cukorka-szállító",
            "grandfather",
            "Your parent's father; keeper of old stories and usually the sneakiest candy supplier",
            "Großvater",
            "Der Vater deines Elternteils; Hüter alter Geschichten und normalerweise der heimlichste Süßigkeitenlieferant",
        ),
        (
            "nagybácsi",
            "A szülőd testvére; gyakran menőbb, mint a szüleid és jobb a titkok megőrzésében",
            "uncle",
            "Your parent's brother; often cooler than your parents and better at keeping secrets",
            "Onkel",
            "Der Bruder deines Elternteils; oft cooler als deine Eltern und besser im Geheimnisse bewahren",
        ),
        (
            "nagymama",
            "A szülőd anyja; mesterszakács, aki ragaszkodik hozzá, hogy túl vékony vagy három adag ellenére",
            "grandmother",
            "Your parent's mother; master chef who insists you're too skinny despite three helpings",
            "Großmutter",
            "Die Mutter deines Elternteils; Meisterköchin, die darauf besteht, dass du zu dünn bist trotz drei Portionen",
        ),
        (
            "nagynéni",
            "A szülőd nővére; második legjobb ölelő nagymama után és szülinapi kártyák pénzzel ellátója",
            "aunt",
            "Your parent's sister; second-best hugger after grandma and supplier of birthday cards with money",
            "Tante",
            "Die Schwester deines Elternteils; zweitbeste Umarmerin nach Oma und Lieferantin von Geburtstagskarten mit Geld",
        ),
        (
            "nagyszülő",
            "A szülőd szülője; professzionális unokák kényeztetője és veterán mentegetődzője",
            "grandparent",
            "Your parent's parent; professional spoiler of grandchildren and veteran excuse-maker",
            "Großelternteil",
            "Das Elternteil deines Elternteils; professioneller Verwöhner von Enkelkindern und erfahrener Ausredenerfinder",
        ),
        (
            "nővér",
            "A női testvér, aki először érkezett és fotóbizonyítékkal rendelkezik kínos éveidről",
            "older sister",
            "The female sibling who arrived first and has photographic evidence of your awkward years",
            "ältere Schwester",
            "Die weibliche Geschwister, die zuerst ankam und fotografische Beweise deiner peinlichen Jahre hat",
        ),
        (
            "öcs",
            "A férfi testvér, aki később jött, de valahogy mégis kölcsönkérte a cuccaidat kérdezés nélkül",
            "younger brother",
            "The male sibling who came later but somehow still borrowed your stuff without asking",
            "jüngerer Bruder",
            "Der männliche Geschwisterteil, der später kam, aber irgendwie trotzdem deine Sachen ohne zu fragen geliehen hat",
        ),
        (
            "rokon",
            "Valaki, akihez vér vagy házasság köt; részvétel a családi vacsorákon változó",
            "relative",
            "Someone you're related to by blood or marriage; attendance at family dinners may vary",
            "Verwandter",
            "Jemand, mit dem du durch Blut oder Heirat verwandt bist; Anwesenheit bei Familienessen kann variieren",
        ),
        (
            "szülő",
            "Az a személy, aki felnevelt; jogosult bárhol zavarba hozni baba fotókkal",
            "parent",
            "The person who raised you; entitled to embarrass you with baby photos at any time",
            "Elternteil",
            "Die Person, die dich großgezogen hat; berechtigt, dich jederzeit mit Babyfotos in Verlegenheit zu bringen",
        ),
        (
            "unoka",
            "A gyereked gyereke; bizonyíték arra, hogy a karma létezik, amikor úgy viselkednek, mint te",
            "grandchild",
            "Your child's child; proof that karma exists when they behave exactly like you did",
            "Enkelkind",
            "Das Kind deines Kindes; Beweis, dass Karma existiert, wenn sie sich genau so verhalten wie du",
        ),
        (
            "unokahúg",
            "A testvéred lánya; valaki, akit elkényeztethetsz, majd visszaadhatod a szüleinek",
            "niece",
            "Your sibling's daughter; someone you can spoil and then return to their parents",
            "Nichte",
            "Die Tochter deines Geschwisters; jemand, den du verwöhnen und dann an ihre Eltern zurückgeben kannst",
        ),
        (
            "vőlegény",
            "Egy férfi, aki megkérdezte a kezét és most a színsémákról és asztalelrendezésről tanul",
            "groom or fiancé",
            "A man who proposed and is now learning about color schemes and table arrangements",
            "Bräutigam oder Verlobter",
            "Ein Mann, der einen Heiratsantrag gemacht hat und jetzt über Farbschemata und Tischanordnungen lernt",
        ),
        (
            "társ",
            "Társad az élet kalandjaiban; az a személy, aki tudja, hol rejtegeted a csokoládét",
            "partner",
            "Your companion in life's adventures; the person who knows where you hide the chocolate",
            "Partner",
            "Dein Begleiter in den Abenteuern des Lebens; die Person, die weiß, wo du die Schokolade versteckst",
        ),
        (
            "iker",
            "Méhtársad; valaki hátborzongatóan hasonló arccal, akit hibáidért okolnak",
            "twin",
            "Your womb-mate; someone with an eerily similar face who gets blamed for your mistakes",
            "Zwilling",
            "Dein Gebärmutter-Mitbewohner; jemand mit einem unheimlich ähnlichen Gesicht, der für deine Fehler verantwortlich gemacht wird",
        ),
        (
            "ős",
            "Valaki a családfádból régen; felelős azért a furcsa genetikai vonásért, amit te is örököltél",
            "ancestor",
            "Someone from way back in your family tree; responsible for that weird genetic trait you have",
            "Vorfahr",
            "Jemand aus weit zurückliegender Zeit in deinem Stammbaum; verantwortlich für die seltsame genetische Eigenschaft, die du hast",
        ),
        (
            "leszármazott",
            "Jövőbeli családtagjaid, akik egy nap zavarba jönnek a közösségi média bejegyzéseid miatt",
            "descendant",
            "Your future family members who will one day be embarrassed by your social media posts",
            "Nachkomme",
            "Deine zukünftigen Familienmitglieder, die eines Tages von deinen Social-Media-Beiträgen peinlich berührt sein werden",
        ),
        (
            "házastárs",
            "Jogilag kötött élettársad; főszereplő a házasságotok nevű napi sitcomban",
            "spouse",
            "Your legally bound life partner; co-star in the daily sitcom called your marriage",
            "Ehepartner",
            "Dein rechtlich gebundener Lebenspartner; Co-Star in der täglichen Sitcom namens deine Ehe",
        ),
        (
            "felnőtt",
            "Valaki, aki állítólag kitalálta az életet, de néha vacsorára müzlit eszik",
            "adult",
            "Someone who allegedly has life figured out but still eats cereal for dinner sometimes",
            "Erwachsener",
            "Jemand, der angeblich das Leben herausgefunden hat, aber manchmal immer noch Müsli zum Abendessen isst",
        ),
        (
            "család",
            "Azok az emberek, akiket nem választottál, de szeretsz mindenképpen; a bűntudat-utazás és kéretlen tanács mesterei",
            "family",
            "The people you didn't choose but love anyway; masters of the guilt trip and unsolicited advice",
            "Familie",
            "Die Menschen, die du nicht ausgesucht hast, aber trotzdem liebst; Meister der Schuldgefühle und ungebetenen Ratschläge",
        ),
        (
            "unokaöcs",
            "A testvéred fia; valaki, akit minden bosszantó dologra megtaníthatsz, amit a szüleik betiltottak",
            "nephew",
            "Your sibling's son; someone you teach all the annoying things their parents banned",
            "Neffe",
            "Der Sohn deines Geschwisters; jemand, dem du all die nervigen Dinge beibringst, die ihre Eltern verboten haben",
        ),
        (
            "fiú",
            "Férfi utódod; jövőbeli tinédzser, aki úgy tesz, mintha nem ismerné nyilvánosan",
            "son",
            "Your male offspring; future teenager who will pretend not to know you in public",
            "Sohn",
            "Dein männlicher Nachkomme; zukünftiger Teenager, der so tun wird, als würde er dich in der Öffentlichkeit nicht kennen",
        ),
        (
            "lánya",
            "Női utódod; az a személy, aki egy nap engedély nélkül rajtaüt a szekrényeden",
            "daughter",
            "Your female offspring; the person who will one day raid your closet without permission",
            "Tochter",
            "Dein weiblicher Nachkomme; die Person, die eines Tages ohne Erlaubnis deinen Schrank plündern wird",
        ),
        (
            "testvér",
            "Valaki, aki megosztja a szüleidet és a gyermekkori traumáidat; első barátod és riválisod",
            "sibling",
            "Someone who shares your parents and childhood trauma; your first friend and rival",
            "Geschwister",
            "Jemand, der deine Eltern und Kindheitstraumata teilt; dein erster Freund und Rivale",
        ),
    ]

    # Create words and translations
    for hu_word, hu_def, en_word, en_def, de_word, de_def in family_words:
        # Create Hungarian word
        hu = Word.objects.create(language=hungarian, word=hu_word, definition=hu_def)

        # Create English word
        en = Word.objects.create(language=english, word=en_word, definition=en_def)

        # Create German word
        de = Word.objects.create(language=german, word=de_word, definition=de_def)

        # Create translations: Hungarian <-> English
        Translation.objects.create(
            source_word=hu,
            target_word=en,
            confidence="exact",
            notes="Family vocabulary",
        )

        # German <-> English
        Translation.objects.create(
            source_word=de,
            target_word=en,
            confidence="exact",
            notes="Family vocabulary",
        )

        # Hungarian <-> German
        Translation.objects.create(
            source_word=hu,
            target_word=de,
            confidence="exact",
            notes="Family vocabulary",
        )


def remove_family_vocabulary(apps, schema_editor):
    """Remove all family vocabulary words and their translations."""
    Word = apps.get_model("vocabulary", "Word")
    Translation = apps.get_model("vocabulary", "Translation")

    # Delete translations with 'Family vocabulary' notes
    Translation.objects.filter(notes="Family vocabulary").delete()

    # Delete words that are part of family vocabulary
    # (This assumes these are the only words with these specific texts)
    family_word_list = [
        "anyós",
        "após",
        "bátya",
        "feleség",
        "férj",
        "gyerek",
        "húg",
        "menyasszony",
        "nagyapa",
        "nagybácsi",
        "nagymama",
        "nagynéni",
        "nagyszülő",
        "nővér",
        "öcs",
        "rokon",
        "szülő",
        "unoka",
        "unokahúg",
        "vőlegény",
        "társ",
        "iker",
        "ős",
        "leszármazott",
        "házastárs",
        "felnőtt",
        "család",
        "unokaöcs",
        "fiú",
        "lánya",
        "testvér",
        # English
        "mother-in-law",
        "father-in-law",
        "older brother",
        "wife",
        "husband",
        "child",
        "younger sister",
        "bride or fiancée",
        "grandfather",
        "uncle",
        "grandmother",
        "aunt",
        "grandparent",
        "older sister",
        "younger brother",
        "relative",
        "parent",
        "grandchild",
        "niece",
        "groom or fiancé",
        "partner",
        "twin",
        "ancestor",
        "descendant",
        "spouse",
        "adult",
        "family",
        "nephew",
        "son",
        "daughter",
        "sibling",
        # German
        "Schwiegermutter",
        "Schwiegervater",
        "älterer Bruder",
        "Ehefrau",
        "Ehemann",
        "Kind",
        "jüngere Schwester",
        "Braut oder Verlobte",
        "Großvater",
        "Onkel",
        "Großmutter",
        "Tante",
        "Großelternteil",
        "ältere Schwester",
        "jüngerer Bruder",
        "Verwandter",
        "Elternteil",
        "Enkelkind",
        "Nichte",
        "Bräutigam oder Verlobter",
        "Partner",
        "Zwilling",
        "Vorfahr",
        "Nachkomme",
        "Ehepartner",
        "Erwachsener",
        "Familie",
        "Neffe",
        "Sohn",
        "Tochter",
        "Geschwister",
    ]

    Word.objects.filter(word__in=family_word_list).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0008_update_initial_words_with_translations"),
    ]

    operations = [
        migrations.RunPython(add_family_vocabulary, remove_family_vocabulary),
    ]
