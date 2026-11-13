"""
Multilingual Outreach Templates & Language Detection for Pewbeam
Supports English, German, French, Spanish, Italian, Dutch, and Portuguese.
"""

import re

COUNTRY_TLD_MAP = {
    "de": "de", "at": "de", "ch": "de",
    "fr": "fr", "be": "fr",
    "es": "es", "mx": "es", "ar": "es", "co": "es",
    "it": "it",
    "nl": "nl",
    "pt": "pt", "br": "pt",
    "uk": "en", "us": "en", "ca": "en", "au": "en", "za": "en", "ng": "en"
}

LOCATION_KEYWORD_MAP = {
    # German
    "germany": "de", "deutschland": "de", "berlin": "de", "munich": "de", "münchen": "de", 
    "frankfurt": "de", "hamburg": "de", "cologne": "de", "köln": "de", "stuttgart": "de", 
    "austria": "de", "österreich": "de", "vienna": "de", "wien": "de", "switzerland": "de", "zurich": "de", "zürich": "de",
    # French
    "france": "fr", "paris": "fr", "lyon": "fr", "marseille": "fr", "toulouse": "fr", 
    "bordeaux": "fr", "nice": "fr", "strasbourg": "fr", "belgium": "fr", "brussels": "fr", "bruxelles": "fr",
    # Spanish
    "spain": "es", "españa": "es", "madrid": "es", "barcelona": "es", "valencia": "es", 
    "seville": "es", "sevilla": "es", "malaga": "es", "málaga": "es", "bilbao": "es",
    # Italian
    "italy": "it", "italia": "it", "rome": "it", "roma": "it", "milan": "it", "milano": "it", 
    "naples": "it", "napoli": "it", "turin": "it", "torino": "it", "florence": "it", "firenze": "it",
    # Dutch
    "netherlands": "nl", "nederland": "nl", "amsterdam": "nl", "rotterdam": "nl", "utrecht": "nl", 
    "the hague": "nl", "den haag": "nl", "eindhoven": "nl",
    # Portuguese
    "portugal": "pt", "lisbon": "pt", "lisboa": "pt", "porto": "pt", "brazil": "pt", "brasil": "pt",
    # English
    "united kingdom": "en", "uk": "en", "london": "en", "manchester": "en", "birmingham": "en", 
    "edinburgh": "en", "glasgow": "en", "ireland": "en", "dublin": "en", "usa": "en"
}

TEMPLATES = {
    "en": {
        "name": "English",
        "flag": "🇬🇧 / 🇺🇸",
        "team_label": "Media & Tech Team",
        "subject": "Quick question about Sunday AV at {church_name}",
        "email_body": """Hi {team_label},

Noticed the great production work your team is doing over at {church_name} in {city}.

One of the biggest hurdles church media directors share with us is the Sunday scramble: when the pastor quotes a scripture off-script mid-sermon, and the booth is frantically searching, copying, and formatting slides before the moment passes.

We built Pewbeam (https://pewbeam.com/) specifically for that. It uses real-time AI audio recognition to listen to the sermon and automatically project the exact Bible verses on screens and livestream lower-thirds (NDI / OBS / vMix compatible) with zero manual searching.

Would you be open to a 2-minute video walkthrough to see if it could save your team time this Sunday?

Warm regards,

[Your Name]
Pewbeam (https://pewbeam.com)""",
        "linkedin_dm": """Hey [First Name] — saw your media & production work with {church_name} in {city}. Quick question: how does your booth team currently handle unexpected scripture quotes when the pastor goes off sermon notes?

We built an AI tool called Pewbeam (https://pewbeam.com) that detects spoken scriptures live and pushes verses to projector screens and OBS/NDI lower-thirds automatically. Would love to send a 60-second clip if you're curious!""",
        "bump": "Hey {church_name} team, just bumping this in case Sunday prep was busy! Happy to send over the 60-second clip showing real-time verse projection if you'd like to check it out."
    },

    "de": {
        "name": "German (Deutsch)",
        "flag": "🇩🇪 / 🇦🇹 / 🇨🇭",
        "team_label": "Technik- & Medienteam",
        "subject": "Kurze Frage zur Beamer- & Livestream-Technik bei {church_name}",
        "email_body": """Hallo {team_label},

ich habe eure Medien- und Gottesdienstarbeit bei {church_name} in {city} gesehen – großes Kompliment an euer Team!

Viele Leiter der Gemeindetechnik kennen das typische Problem am Sonntagmorgen: Der Pastor zitiert während der Predigt spontan eine Bibelstelle, die nicht im Ablaufplan stand, und das Beamer-Team muss in Sekundenschnelle hektisch nach der Stelle suchen und Folien erstellen.

Genau dafür haben wir Pewbeam (https://pewbeam.com/) entwickelt. Unsere Software hört der Predigt per KI in Echtzeit zu und projiziert automatisch die passenden Bibelverse auf die Leinwand sowie als Bauchbinde in den Livestream (voll kompatibel mit NDI, OBS und vMix) – komplett ohne manuelles Suchen.

Hättet ihr Zeit für ein kurzes 2-minütiges Video, um zu sehen, wie Pewbeam eure Gottesdienste entlasten kann?

Herzliche Grüße,

[Dein Name]
Pewbeam Team (https://pewbeam.com)""",
        "linkedin_dm": """Hallo [Vorname] – ich habe deine Arbeit im Technik-/Medienbereich bei {church_name} in {city} gesehen. Kurze Frage: Wie handhabt euer Beamer-Team spontane Bibelzitate, wenn der Pastor vom Predigtskript abweicht?

Wir haben Pewbeam (https://pewbeam.com) entwickelt – eine KI, die gesprochene Verse live erkennt und sofort auf Beamer & OBS/NDI projiziert. Wenn du möchtest, schicke ich dir gerne ein 60-Sekunden-Demo-Video!""",
        "bump": "Hallo {church_name} Team, kurze Nachfrage, falls die Vorbereitung fürs Wochenende voll war! Meldet euch gerne, wenn ihr das 60-Sekunden-Video zur automatischen Vers-Projektion sehen möchtet."
    },

    "fr": {
        "name": "French (Français)",
        "flag": "🇫🇷 / 🇧🇪 / 🇨🇭",
        "team_label": "Équipe Régie & Audiovisuelle",
        "subject": "Question rapide sur votre régie technique à {church_name}",
        "email_body": """Bonjour {team_label},

Félicitations pour la qualité des cultes et de la diffusion que vous réalisez à {church_name} à {city}.

La plupart des responsables techniques d'église partagent le même défi le dimanche : lorsque le pasteur cite un verset biblique de manière impromptue pendant la prédication, l'équipe régie doit chercher et formater les diapositives dans l'urgence.

Nous avons créé Pewbeam (https://pewbeam.com/) pour résoudre ce problème. Notre solution écoute la prédication en temps réel grâce à l'IA et affiche instantanément les versets bibliques exacts sur vos écrans de projection et en sous-titres/bandeaux sur le livestream (compatible NDI, OBS, vMix), sans aucune manipulation manuelle.

Seriez-vous ouverts à une vidéo démo de 2 minutes pour voir comment cela fonctionne avec votre régie ?

Bien cordialement,

[Votre Nom]
L'équipe Pewbeam (https://pewbeam.com)""",
        "linkedin_dm": """Bonjour [Prénom] — j'ai vu votre travail audiovisuel avec {church_name} à {city}. Petite question : comment votre régie gère-t-elle les versets bibliques imprévus lorsque le pasteur improvise pendant son message ?

Nous avons conçu Pewbeam (https://pewbeam.com), une IA qui détecte en temps réel les versets prononcés et les envoie automatiquement sur projecteur et OBS/NDI. Je serais ravi de vous partager une vidéo de 60 secondes si vous êtes curieux !""",
        "bump": "Bonjour l'équipe de {church_name}, je me permets une petite relance entre deux cultes ! N'hésitez pas si vous souhaitez recevoir le court extrait vidéo montrant la projection automatique en direct."
    },

    "es": {
        "name": "Spanish (Español)",
        "flag": "🇪🇸 / 🇲🇽 / 🇦🇷",
        "team_label": "Equipo Multimedia y Audiovisual",
        "subject": "Pregunta rápida sobre la transmisión y pantallas en {church_name}",
        "email_body": """Hola {team_label},

Quería felicitarlos por el gran trabajo de producción y streaming que realizan en {church_name} en {city}.

Muchos directores de multimedia nos comentan el mismo desafío de los domingos: cuando el pastor cita un versículo bíblico improvisado durante la predicación, la cabina tiene que correr para buscarlo, formatearlo y proyectarlo antes de que pase el momento.

Por eso creamos Pewbeam (https://pewbeam.com/). Utiliza inteligencia artificial para escuchar la prédica en tiempo real y proyecta automáticamente los versículos bíblicos en las pantallas y en los tercios inferiores de la transmisión en vivo (compatible con NDI, OBS y vMix) sin necesidad de búsquedas manuales.

¿Estarían abiertos a un video de 2 minutos para ver cómo se integra con su sistema actual?

Un cordial saludo,

[Tu Nombre]
Equipo Pewbeam (https://pewbeam.com)""",
        "linkedin_dm": """Hola [Nombre] — vi tu labor en el área de medios de {church_name} en {city}. Una consulta rápida: ¿cómo maneja su equipo técnico los versículos espontáneos cuando el pastor se sale de las notas del sermón?

Desarrollamos Pewbeam (https://pewbeam.com), una IA que escucha en directo y proyecta los versículos automáticamente en pantallas y OBS/NDI. ¡Me encantaría enviarte un video de 60 segundos si te da curiosidad!""",
        "bump": "¡Hola equipo de {church_name}! Paso a saludar por si la preparación del domingo estuvo ocupada. Si desean ver el clip de 60 segundos mostrando cómo funciona en vivo, con gusto se los comparto."
    },

    "it": {
        "name": "Italian (Italiano)",
        "flag": "🇮🇹",
        "team_label": "Team Regia & Multimediale",
        "subject": "Breve domanda sulla regia video di {church_name}",
        "email_body": """Gentile {team_label},

Complimenti per l'ottimo lavoro di produzione e streaming che svolgete presso {church_name} a {city}.

Molti responsabili tecnici di chiesa affrontano la stessa difficoltà ogni domenica: quando il pastore cita un versetto biblico a braccio senza preavviso, la regia deve cercare e impaginare le slide a tempo di record.

Abbiamo sviluppato Pewbeam (https://pewbeam.com/) appositamente per questo. Grazie all'intelligenza artificiale, ascolta il sermone in tempo reale e proietta automaticamente i versetti biblici sugli schermi e nella grafica del livestream (compatibile con NDI, OBS e vMix) senza alcuna ricerca manuale.

Sareste disponibili per un breve video di 2 minuti per vedere come funziona?

Un cordiale saluto,

[Tuo Nome]
Team Pewbeam (https://pewbeam.com)""",
        "linkedin_dm": """Ciao [Nome] — ho notato il vostro lavoro di produzione video con {church_name} a {city}. Una domanda veloce: come gestisce la vostra regia i versetti biblici improvvisati durante la predicazione?

Abbiamo creato Pewbeam (https://pewbeam.com), un'IA che riconosce i versetti parlati in diretta e li invia automaticamente a schermi e OBS/NDI. Sarei felice di inviarti una demo di 60 secondi se ti incuriosisce!""",
        "bump": "Ciao team di {church_name}, un piccolo promemoria qualora foste stati impegnati con la preparazione del culto! Fatemi sapere se desiderate dare un'occhiata al video di 60 secondi."
    },

    "nl": {
        "name": "Dutch (Nederlands)",
        "flag": "🇳🇱 / 🇧🇪",
        "team_label": "Beamer- & Mediateam",
        "subject": "Korte vraag over jullie kerktechniek bij {church_name}",
        "email_body": """Beste {team_label},

Complimenten voor de mooie diensten en livestream bij {church_name} in {city}!

Veel kerktechnici herkennen het haastmoment op zondagochtend: wanneer de voorganger tijdens de preek spontaan een bijbeltekst aanhaalt die niet in de liturgie stond, moet het beamerteam in allerijl zoeken, kopiëren en projecteren.

Daarom hebben wij Pewbeam (https://pewbeam.com/) ontwikkeld. Onze software luistert via AI live mee met de preek en projecteert automatisch de juiste bijbelverzen op de schermen en in de livestream lower-thirds (NDI, OBS en vMix ondersteund) – zonder handmatig zoekwerk.

Zouden jullie openstaan voor een korte video van 2 minuten om te zien hoe dit werkt?

Met vriendelijke groet,

[Je Naam]
Pewbeam Team (https://pewbeam.com)""",
        "linkedin_dm": """Hoi [Voornaam] — ik zag je werk bij het mediateam van {church_name} in {city}. Korte vraag: hoe vangt jullie beamerteam onverwachte bijbelteksten op als de spreker afwijkt van de aantekeningen?

Wij hebben Pewbeam (https://pewbeam.com) gebouwd: AI die gesproken bijbelteksten live herkent en direct doorstuurt naar schermen en OBS/NDI. Laat het gerust weten als je een video van 60 seconden wilt bekijken!""",
        "bump": "Hoi team {church_name}, even een korte herinnering tussen de zondagen door! Laat gerust weten als jullie het korte demovideootje willen zien."
    },

    "pt": {
        "name": "Portuguese (Português)",
        "flag": "🇵🇹 / 🇧🇷",
        "team_label": "Equipe de Mídia e Audiovisual",
        "subject": "Pergunta rápida sobre a transmissão e projeção na {church_name}",
        "email_body": """Olá {team_label},

Parabéns pelo excelente trabalho de produção e transmissão que realizam na {church_name} em {city}.

A maioria dos líderes de mídia compartilha o mesmo aperto aos domingos: quando o pastor cita um versículo bíblico de improviso durante a mensagem, a equipe da mesa precisa correr para buscar, formatar e projetar o slide antes que o momento passe.

Criamos o Pewbeam (https://pewbeam.com/) exatamente para isso. Ele usa inteligência artificial para ouvir a pregação em tempo real e projeta automaticamente os versículos bíblicos nos telões e nos letterings da transmissão ao vivo (compatível com NDI, OBS e vMix) sem necessidade de pesquisa manual.

Vocês teriam interesse em ver um vídeo de 2 minutos demonstrando como funciona com a estrutura de vocês?

Um abraço,

[Seu Nome]
Equipe Pewbeam (https://pewbeam.com)""",
        "linkedin_dm": """Olá [Nome] — vi seu trabalho na área de multimídia da {church_name} em {city}. Uma pergunta rápida: como a equipe da cabine lida com versículos espontâneos quando o pastor sai do esboço da mensagem?

Desenvolvemos o Pewbeam (https://pewbeam.com), uma IA que reconhece versículos falados ao vivo e os projeta automaticamente nas telas e no OBS/NDI. Se tiver curiosidade, posso te enviar um vídeo de 60 segundos!""",
        "bump": "Olá equipe da {church_name}! Passando apenas para lembrar caso os preparativos de domingo tenham sido corridos. Se quiserem ver o vídeo de 60 segundos com o sistema em ação, é só avisar!"
    }
}

def detect_language(church_name: str = "", city: str = "", state: str = "", website: str = "") -> str:
    text_to_check = f"{church_name} {city} {state}".lower()
    
    # 1. Check TLD from website
    if website:
        # Extract domain extension
        match = re.search(r"\.([a-z]{2,3})(?:/|$)", website.lower())
        if match:
            tld = match.group(1)
            if tld in COUNTRY_TLD_MAP:
                return COUNTRY_TLD_MAP[tld]

    # 2. Check keywords in city/state/name
    for keyword, lang in LOCATION_KEYWORD_MAP.items():
        if keyword in text_to_check:
            return lang

    # Default to English
    return "en"

def get_outreach_content(lang_code: str, church_name: str, city: str):
    template = TEMPLATES.get(lang_code, TEMPLATES["en"])
    
    formatted_subject = template["subject"].format(church_name=church_name, city=city)
    formatted_email = template["email_body"].format(
        church_name=church_name,
        city=city,
        team_label=template["team_label"]
    )
    formatted_linkedin = template["linkedin_dm"].format(
        church_name=church_name,
        city=city
    )
    formatted_bump = template["bump"].format(
        church_name=church_name,
        city=city
    )

    return {
        "lang_code": lang_code,
        "lang_name": template["name"],
        "flag": template["flag"],
        "subject": formatted_subject,
        "email_body": formatted_email,
        "linkedin_dm": formatted_linkedin,
        "bump": formatted_bump
    }
