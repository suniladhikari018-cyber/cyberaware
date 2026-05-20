import json
from models import db, Challenge

def seed_challenges():
    if Challenge.query.count() > 0:
        return

    challenges = [
        # ── PHISHING ──────────────────────────────────────────────────────────────
        {
            "title": "Spot the Phishing Email #1",
            "category": "Phishing",
            "description": (
                "You receive this email:\n\n"
                "**From:** security@paypa1.com\n"
                "**Subject:** Urgent: Your account has been compromised!\n\n"
                "'Dear Customer, We detected suspicious activity. "
                "Click HERE immediately to verify your account or it will be suspended within 24 hours.'\n\n"
                "What should you do?"
            ),
            "options": [
                "Click the link immediately to secure your account",
                "Reply asking for more details",
                "Delete the email – it's a phishing attempt (note the '1' in paypa1.com)",
                "Forward to all your contacts to warn them"
            ],
            "correct_index": 2,
            "explanation": "The sender domain is 'paypa1.com' (with a number 1, not letter l) – a classic typosquatting phishing trick. Legitimate companies never create urgency to get you to click links. Always check the sender domain carefully.",
            "points": 20,
            "difficulty": "easy"
        },
        {
            "title": "Spot the Phishing Email #2",
            "category": "Phishing",
            "description": (
                "You receive an email:\n\n"
                "**From:** it-support@yourcompany.com\n"
                "**Subject:** Password Reset Required\n\n"
                "'Hi, your password expires today. Reset it now at: http://yourcompany-reset.xyz/login'\n\n"
                "The link goes to a different domain. What's the safest action?"
            ),
            "options": [
                "Click the link and reset your password right away",
                "Visit the official company portal directly by typing the URL in your browser",
                "Reply to the email asking if it's legitimate",
                "Call the number provided in the email"
            ],
            "correct_index": 1,
            "explanation": "Even if the sender looks legitimate, the link points to 'yourcompany-reset.xyz' – not the company domain. Always navigate to official sites by typing the URL directly, never via email links.",
            "points": 25,
            "difficulty": "medium"
        },
        {
            "title": "Phishing Red Flags",
            "category": "Phishing",
            "description": "Which of the following is NOT a typical red flag of a phishing email?",
            "options": [
                "Generic greeting like 'Dear Customer'",
                "Urgent language demanding immediate action",
                "Email sent from your colleague's known email address with correct spelling",
                "Misspelled company name in the link"
            ],
            "correct_index": 2,
            "explanation": "A correctly spelled, known colleague email is not itself a red flag (though accounts can still be compromised). The others – generic greetings, urgency, and misspellings – are classic phishing indicators.",
            "points": 20,
            "difficulty": "easy"
        },
        {
            "title": "CEO Fraud / Spear Phishing",
            "category": "Phishing",
            "description": (
                "Your boss (CEO) emails you:\n\n"
                "'I'm in a meeting and need you to urgently wire $5,000 to a vendor. "
                "Don't call me – just do it now and I'll explain later.'\n\n"
                "What should you do?"
            ),
            "options": [
                "Wire the money immediately since your boss asked",
                "Do nothing since the amount is small",
                "Verify through a separate channel (call your boss directly using a known number)",
                "Reply to the email asking for the vendor details"
            ],
            "correct_index": 2,
            "explanation": "This is a Business Email Compromise (BEC) attack. Attackers impersonate executives and create urgency. Always verify financial requests through a separate, known communication channel – never just reply to the same email.",
            "points": 30,
            "difficulty": "hard"
        },
        {
            "title": "Suspicious Attachment",
            "category": "Phishing",
            "description": "You receive an email from an unknown sender with a file called 'Invoice_2024.pdf.exe'. What is this file?",
            "options": [
                "A normal PDF invoice",
                "A malware executable disguised as a PDF",
                "A compressed archive",
                "A harmless text file"
            ],
            "correct_index": 1,
            "explanation": "'.pdf.exe' is a double extension trick. Windows hides known extensions by default, so the file appears as 'Invoice_2024.pdf' but is actually an executable (.exe) that can run malware. Never open unexpected attachments.",
            "points": 25,
            "difficulty": "medium"
        },

        # ── PASSWORD ──────────────────────────────────────────────────────────────
        {
            "title": "Strong Password Basics",
            "category": "Password",
            "description": "Which of these passwords is the STRONGEST?",
            "options": [
                "password123",
                "P@ssw0rd",
                "Tr0ub4dor&3",
                "qwerty!1"
            ],
            "correct_index": 2,
            "explanation": "'Tr0ub4dor&3' is longest (11 chars) with mixed case, numbers, and special characters. 'password123' is in every dictionary. 'P@ssw0rd' is a common substitution pattern. Length + randomness = strength.",
            "points": 20,
            "difficulty": "easy"
        },
        {
            "title": "Password Reuse Risk",
            "category": "Password",
            "description": "You use the same password for your email, banking, and social media. One site gets breached. What's the risk?",
            "options": [
                "No risk – the breach only affects that one site",
                "Attackers can try your password on all other accounts (credential stuffing)",
                "Your password becomes stronger from exposure",
                "Only your email is at risk"
            ],
            "correct_index": 1,
            "explanation": "Credential stuffing is when attackers take leaked username/password combos and try them on many services automatically. If you reuse passwords, a single breach can compromise ALL your accounts.",
            "points": 20,
            "difficulty": "easy"
        },
        {
            "title": "Multi-Factor Authentication",
            "category": "Password",
            "description": "What does Multi-Factor Authentication (MFA) protect against, even if your password is stolen?",
            "options": [
                "Nothing – if the password is stolen, the account is lost",
                "Unauthorized login – attacker needs a second factor (e.g., your phone)",
                "Malware on your device",
                "Phishing emails reaching your inbox"
            ],
            "correct_index": 1,
            "explanation": "MFA requires something you KNOW (password) + something you HAVE (phone/token) or something you ARE (biometric). Even with your password, an attacker cannot log in without the second factor.",
            "points": 25,
            "difficulty": "medium"
        },
        {
            "title": "Password Manager",
            "category": "Password",
            "description": "Why should you use a password manager instead of memorizing all passwords?",
            "options": [
                "Password managers are always free",
                "They let you use one password for everything safely",
                "They generate and store unique strong passwords for every site",
                "They share passwords between family members automatically"
            ],
            "correct_index": 2,
            "explanation": "Password managers generate unique, long, random passwords for every site and store them encrypted. You only need to remember one master password. This prevents reuse while maintaining strong, unique credentials everywhere.",
            "points": 20,
            "difficulty": "easy"
        },
        {
            "title": "Dictionary Attack",
            "category": "Password",
            "description": "A 'dictionary attack' on passwords means:",
            "options": [
                "Attackers look up your password in a physical dictionary",
                "Attackers try every word/common password from a list automatically",
                "Attackers guess passwords one character at a time",
                "Attackers use your browser history to guess your password"
            ],
            "correct_index": 1,
            "explanation": "Dictionary attacks use automated tools to try thousands of common words, names, phrases and known passwords per second. This is why 'password', 'iloveyou', or 'dragon' are terrible choices – they're in every dictionary list.",
            "points": 25,
            "difficulty": "medium"
        },

        # ── SOCIAL ENGINEERING ────────────────────────────────────────────────────
        {
            "title": "Pretexting Attack",
            "category": "Social Engineering",
            "description": (
                "Someone calls claiming to be from your bank's fraud department. "
                "They say suspicious transactions were detected and ask you to confirm "
                "your full card number and CVV to 'verify your identity'. What do you do?"
            ),
            "options": [
                "Provide the details since they called you first",
                "Hang up and call your bank using the number on the back of your card",
                "Give only the last 4 digits to be safe",
                "Ask them to email you instead"
            ],
            "correct_index": 1,
            "explanation": "Your bank will NEVER ask for your full card number or CVV over the phone. This is vishing (voice phishing) using a pretext. Always hang up and call back using the official number from your card or the bank's website.",
            "points": 30,
            "difficulty": "hard"
        },
        {
            "title": "USB Drop Attack",
            "category": "Social Engineering",
            "description": "You find a USB drive in the office car park labeled 'Payroll Q4 2024'. What should you do?",
            "options": [
                "Plug it in to find the owner and return it",
                "Take it home to check on a personal computer",
                "Hand it to IT/security without plugging it in",
                "Format it and use it as extra storage"
            ],
            "correct_index": 2,
            "explanation": "This is a classic 'USB drop' social engineering attack. Curiosity makes people plug in unknown drives, which can auto-run malware. NEVER plug in a found USB. Hand it to IT/security who have tools to safely examine it.",
            "points": 30,
            "difficulty": "hard"
        },
        {
            "title": "Tailgating / Piggybacking",
            "category": "Social Engineering",
            "description": "Someone follows closely behind you as you badge into a secure area, smiling and holding coffee cups. What's the correct response?",
            "options": [
                "Hold the door – it would be rude not to",
                "Let them in if they look like an employee",
                "Politely ask them to badge in themselves or contact reception",
                "Ignore them and let security handle it"
            ],
            "correct_index": 2,
            "explanation": "Tailgating (piggybacking) is a physical security attack where unauthorized people follow authorized personnel into secure areas. Politeness is exploited. Everyone must badge in separately, no exceptions – politely ask them to use their own access.",
            "points": 25,
            "difficulty": "medium"
        },

        # ── SECURE BROWSING ───────────────────────────────────────────────────────
        {
            "title": "HTTPS vs HTTP",
            "category": "Secure Browsing",
            "description": "When entering your credit card details online, what should you look for in the browser?",
            "options": [
                "The website has a nice design",
                "The URL starts with 'https://' and shows a padlock",
                "The website loads quickly",
                "The URL contains the word 'secure'"
            ],
            "correct_index": 1,
            "explanation": "HTTPS (the 'S' stands for Secure) encrypts data between your browser and the server using TLS. The padlock icon confirms the certificate is valid. HTTP sends data in plain text – anyone on the same network can intercept it.",
            "points": 20,
            "difficulty": "easy"
        },
        {
            "title": "Public Wi-Fi Risks",
            "category": "Secure Browsing",
            "description": "You're at a café and connect to 'CafeWifi_FREE'. What's the safest activity on this network?",
            "options": [
                "Online banking",
                "Shopping with your credit card",
                "Browsing general news websites",
                "Logging into work email with sensitive data"
            ],
            "correct_index": 2,
            "explanation": "Public Wi-Fi is often unencrypted and can be monitored or spoofed (evil twin attack). Safe uses: reading public websites. Avoid: banking, shopping, work logins. If you must, use a VPN to encrypt all traffic.",
            "points": 25,
            "difficulty": "medium"
        },
        {
            "title": "Software Updates",
            "category": "Secure Browsing",
            "description": "Your OS prompts you to install a security update. You're busy. What should you do?",
            "options": [
                "Ignore it – updates often break things",
                "Schedule it for soon and install it – security patches fix known vulnerabilities",
                "Wait a month to see if others report problems",
                "Disable automatic updates to stay in control"
            ],
            "correct_index": 1,
            "explanation": "Security updates patch known vulnerabilities that attackers actively exploit. The longer you delay, the longer you're exposed. Most updates are safe and critical. Schedule promptly – don't ignore them.",
            "points": 20,
            "difficulty": "easy"
        },
    ]

    for c in challenges:
        ch = Challenge(
            title=c['title'],
            category=c['category'],
            description=c['description'],
            options=json.dumps(c['options']),
            correct_index=c['correct_index'],
            explanation=c['explanation'],
            points=c['points'],
            difficulty=c['difficulty']
        )
        db.session.add(ch)

    db.session.commit()
    print(f"Seeded {len(challenges)} challenges.")
