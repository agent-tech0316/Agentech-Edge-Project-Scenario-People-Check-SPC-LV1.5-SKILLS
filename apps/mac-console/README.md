# Mac Console

The Mac console is the local command center.

First UI responsibilities:

- Choose today's class
- Show roster and attendance state
- Display iPhone capture QR code
- Show recognized faces and confidence
- Confirm uncertain matches
- Manually mark present, late, absent, or excused
- Export reports

Technical direction:

- Start as a local web app served from the Mac
- Keep database and media local
- Expose LAN-only upload endpoints for iPhone capture
- Later package as a native macOS app or menu bar app

