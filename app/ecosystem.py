"""Static content describing each Damba Royal ecosystem section."""

SECTIONS = {
    "labyrinth": {
        "icon": "🏰",
        "title": "Royal Heritage Labyrinth",
        "tagline": "Train online, compete, and qualify for the future championship.",
        "status": "Online training live · Championship under development",
        "purpose": "A heritage-inspired challenge platform where players train, earn XP and Royal Tokens, and build a record toward future championship qualification.",
        "features": [
            "Training challenges (available now)",
            "XP, levels and Royal Tokens (available now)",
            "Online live competition, seasons, ranks and leaderboards (see the Labyrinth page for what is currently enabled)",
            "Future physical championship qualification (planned; no dates or invitations confirmed)",
        ],
        "availability": "Training challenges are playable today. Seasons, global rankings and championship qualification are still being developed.",
        "next_steps": "Continue your journey in the Labyrinth to earn XP and Royal Tokens.",
        "cta": ("/challenge", "Enter the Royal Labyrinth"),
        "enquiry": False,
    },
    "sal-africa": {
        "icon": "🪙",
        "title": "SAL AFRICA",
        "tagline": "Sovereign Asset Ledger",
        "status": "Prototype",
        "purpose": "The Sovereign Asset Ledger is intended to hold a player's Royal ID and a record of Royal Tokens and future assets.",
        "features": [
            "Royal ID issued at registration (available now)",
            "XP and Royal Token balances shown on your dashboard (available now)",
            "Digital wallet and asset services (planned; not operating)",
        ],
        "availability": "Your Royal ID, XP and Royal Token balances are real records on this platform. Wallet transfers, payments and asset services are not available.",
        "next_steps": "View your Royal ID and balances on the dashboard.",
        "cta": ("/dashboard#profile", "View my Royal ID and balances"),
        "enquiry": False,
    },
    "resort": {
        "icon": "🏨",
        "title": "Damba Royal Luxury Resort",
        "tagline": "A future destination for heritage hospitality.",
        "status": "Under development",
        "purpose": "A planned luxury resort and hospitality concept inspired by Northern Ghana heritage.",
        "features": [
            "Hospitality and accommodation concepts (planning)",
            "Cultural experiences (planning)",
            "Accommodation enquiries (open now)",
            "Reservations (future; not available)",
        ],
        "availability": "The resort is not built or operating. No bookings can be made and nothing here is a reservation. Enquiries are recorded for follow-up.",
        "next_steps": "Send an enquiry to register your interest.",
        "enquiry": True,
        "enquiry_label": "Register resort interest",
    },
    "journey": {
        "icon": "✈️",
        "title": "Royal Journey",
        "tagline": "Travel support for Damba Royal guests.",
        "status": "Enquiry-based service",
        "purpose": "Coordinates travel services for players and guests.",
        "features": [
            "Travel and booking enquiries",
            "Visa-assistance enquiries (information and document guidance only)",
            "Airport pickup requests",
            "Accommodation coordination",
        ],
        "availability": "Requests are recorded and followed up manually. Damba Royal does not issue visas and cannot guarantee visa approval. Requests are not confirmed bookings.",
        "next_steps": "Describe your trip below and the team will respond.",
        "enquiry": True,
        "enquiry_label": "Submit a travel enquiry",
    },
    "polo": {
        "icon": "🐎",
        "title": "Polo & Royal Equestrian Park",
        "tagline": "A planned home for polo and equestrian heritage.",
        "status": "Under development",
        "purpose": "A planned park for polo, equestrian experiences and riding activities.",
        "features": [
            "Polo and equestrian experiences (planned)",
            "Riding activities (planned)",
            "Facilities information (planned)",
            "Enquiries (open now)",
        ],
        "availability": "The park is not yet operating. No sessions or events can be booked.",
        "next_steps": "Send an enquiry to be informed as development progresses.",
        "enquiry": True,
        "enquiry_label": "Equestrian park enquiry",
    },
    "livestock": {
        "icon": "🐂",
        "title": "Damba Royal Livestock",
        "tagline": "Livestock listings maintained by the livestock administrator.",
        "status": "Listings and enquiries",
        "purpose": "Shows livestock currently listed, with details and availability.",
        "features": [
            "Listings with details and availability",
            "Booking or purchase enquiries",
            "Listings maintained by the designated livestock administrator",
        ],
        "availability": "Online payment is not available. An enquiry is not a confirmed sale; availability is confirmed by the administrator.",
        "next_steps": "Browse listings and submit an enquiry.",
        "enquiry": True,
        "enquiry_label": "General livestock enquiry",
        "catalog": True,
    },
    "luxury": {
        "icon": "🛍️",
        "title": "Damba Royal Luxury",
        "tagline": "Premium products inspired by Northern heritage.",
        "status": "Catalogue preview",
        "purpose": "A premium product section with details and inventory status.",
        "features": [
            "Product details and inventory status",
            "Product enquiries (open now)",
            "Online purchasing (future; not available)",
        ],
        "availability": "Inventory status is informational. There is no checkout or payment; enquiries are not orders.",
        "next_steps": "Browse products and send an enquiry.",
        "enquiry": True,
        "enquiry_label": "General product enquiry",
        "catalog": True,
    },
}

CATALOG_SECTIONS = ("livestock", "luxury")

CATALOG_STATUSES = {
    "available": "Available",
    "limited": "Limited availability",
    "reserved": "Reserved",
    "sold_out": "Sold out / unavailable",
    "coming_soon": "Coming soon",
}

NEWS_CATEGORIES = ["General", "Labyrinth", "Resort", "Journey", "Polo", "Livestock", "Luxury", "SAL AFRICA"]

INITIAL_NEWS = [
    ("Resort under development", "Resort",
     "The Damba Royal Luxury Resort is under development. No opening date has been announced and reservations are not yet available. You may register interest through an enquiry."),
    ("Polo & Royal Equestrian Park under development", "Polo",
     "The Polo & Royal Equestrian Park is a planned facility under development. No sessions or events can be booked yet."),
    ("Royal Journey enquiries open", "Journey",
     "Royal Journey travel, visa-assistance, airport pickup and accommodation-coordination requests are handled as enquiries. Requests are not confirmed bookings and visa approval is not guaranteed."),
    ("Livestock and Luxury listings", "Livestock",
     "Damba Royal Livestock and Damba Royal Luxury listings are maintained by administrators. Online payment is not available; availability is confirmed after an enquiry."),
]

NEWS_CATEGORY_BY_SLUG = {
    "labyrinth": "Labyrinth", "sal-africa": "SAL AFRICA", "resort": "Resort",
    "journey": "Journey", "polo": "Polo", "livestock": "Livestock", "luxury": "Luxury",
}
